"""
Utility functions for candidate search matching
"""
from django.db.models import Q
from accounts.models import Profile
from .models import SavedCandidateSearch, CandidateSearchMatch
from .recommendations import parse_skills, split_skills
from django.utils import timezone


def find_candidates_for_search(saved_search):
    """
    Find all candidates that match a saved search criteria.
    Returns a queryset of Profile objects.
    """
    candidates = Profile.objects.filter(role='seeker', is_public=True).select_related('user')
    
    # Text search (name, headline, bio)
    if saved_search.search_query:
        query = saved_search.search_query.strip()
        candidates = candidates.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(headline__icontains=query) |
            Q(bio__icontains=query)
        )
    
    # Location filter
    if saved_search.location:
        candidates = candidates.filter(location__icontains=saved_search.location)
    
    # Skills filter
    if saved_search.skills:
        skill_list = [skill.strip() for skill in saved_search.skills.split(',') if skill.strip()]
        if skill_list:
            # Parse skills for matching
            search_skills = set(parse_skills(saved_search.skills))
            skill_query = Q()
            for skill in skill_list:
                skill_query |= Q(skills__icontains=skill)
            candidates = candidates.filter(skill_query)
    
    return candidates


def find_new_matches_for_search(saved_search):
    """
    Find new candidates that match a saved search but haven't been tracked yet.
    Returns a list of Profile objects.
    """
    if not saved_search.is_active:
        return []
    
    # Get all matching candidates
    matching_candidates = find_candidates_for_search(saved_search)
    
    # Get IDs of candidates we've already tracked
    existing_match_ids = CandidateSearchMatch.objects.filter(
        saved_search=saved_search
    ).values_list('candidate_id', flat=True)
    
    # Filter out candidates we've already seen
    new_candidates = matching_candidates.exclude(id__in=existing_match_ids)
    
    return list(new_candidates)


def create_matches_for_search(saved_search, candidates):
    """
    Create CandidateSearchMatch records for the given candidates.
    Returns the number of matches created.
    """
    matches_created = 0
    for candidate in candidates:
        match, created = CandidateSearchMatch.objects.get_or_create(
            saved_search=saved_search,
            candidate=candidate,
            defaults={
                'first_matched_date': timezone.now(),
            }
        )
        if created:
            matches_created += 1
    
    # Update last_checked timestamp
    saved_search.last_checked = timezone.now()
    saved_search.save(update_fields=['last_checked'])
    
    return matches_created

