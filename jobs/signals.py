"""
Signals to automatically check for candidate matches when profiles are updated.
This enables real-time matching without needing to run the management command manually.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from accounts.models import Profile
from .models import SavedCandidateSearch, CandidateSearchMatch
from .search_utils import find_candidates_for_search


def send_match_notification_email(recipient_email, recruiter_username, saved_search, matches):
    """Send email notification about new candidate matches"""
    subject = f'New Candidate Matches for "{saved_search.name}"'
    
    # Create email content
    match_list = []
    for match in matches[:10]:  # Limit to 10 in email
        candidate = match.candidate
        match_list.append({
            'name': candidate.user.get_full_name() or candidate.user.username,
            'headline': candidate.headline or '',
            'location': candidate.location or '',
            'profile_url': f'{settings.SITE_URL if hasattr(settings, "SITE_URL") else "http://localhost:8000"}/accounts/u/{candidate.user.username}/',
        })
    
    message = f"""
Hello {recruiter_username},

We found {matches.count()} new candidate(s) that match your saved search "{saved_search.name}".

"""
    for i, match_info in enumerate(match_list, 1):
        message += f"{i}. {match_info['name']}"
        if match_info['headline']:
            message += f" - {match_info['headline']}"
        if match_info['location']:
            message += f" ({match_info['location']})"
        message += f"\n   View profile: {match_info['profile_url']}\n\n"

    if matches.count() > 10:
        message += f"\n... and {matches.count() - 10} more match(es).\n"

    message += f"""
View all matches: {settings.SITE_URL if hasattr(settings, "SITE_URL") else "http://localhost:8000"}/jobs/searches/{saved_search.pk}/matches/

Best regards,
JobBoard Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@jobboard.com',
        recipient_list=[recipient_email],
        fail_silently=False,
    )


@receiver(post_save, sender=Profile)
def check_candidate_matches_on_profile_save(sender, instance, created, **kwargs):
    """
    Automatically check for candidate matches when a profile is saved or updated.
    Only processes job seeker profiles that are public.
    """
    # Only process job seeker profiles
    if instance.role != 'seeker':
        return
    
    # Only process public profiles (private profiles shouldn't match searches)
    if not instance.is_public:
        return
    
    # Get all active saved searches
    active_searches = SavedCandidateSearch.objects.filter(is_active=True)
    
    if not active_searches.exists():
        return
    
    # Check each active search to see if this candidate matches
    for saved_search in active_searches:
        # Check if this candidate matches the search criteria
        matching_candidates = find_candidates_for_search(saved_search)
        
        # Check if this specific candidate is in the matching set
        if not matching_candidates.filter(id=instance.id).exists():
            continue
        
        # Check if we've already created a match record for this candidate
        existing_match = CandidateSearchMatch.objects.filter(
            saved_search=saved_search,
            candidate=instance
        ).first()
        
        if existing_match:
            # Match already exists, skip
            continue
        
        # This is a new match! Create the match record
        match, created = CandidateSearchMatch.objects.get_or_create(
            saved_search=saved_search,
            candidate=instance,
            defaults={
                'first_matched_date': timezone.now(),
            }
        )
        
        if created:
            # Update last_checked timestamp on the saved search
            saved_search.last_checked = timezone.now()
            saved_search.save(update_fields=['last_checked'])
            
            # Send notification email if not already notified
            if not match.notified:
                recruiter = saved_search.recruiter
                recruiter_email = recruiter.email or recruiter.user.email
                
                if recruiter_email:
                    try:
                        # Get all unnotified matches for this search to batch in one email
                        unnotified_matches = CandidateSearchMatch.objects.filter(
                            saved_search=saved_search,
                            notified=False
                        ).select_related('candidate__user')
                        
                        if unnotified_matches.exists():
                            send_match_notification_email(
                                recruiter_email,
                                recruiter.user.username,
                                saved_search,
                                unnotified_matches
                            )
                            
                            # Mark all matches as notified
                            unnotified_matches.update(notified=True, notified_date=timezone.now())
                            saved_search.last_notified = timezone.now()
                            saved_search.save(update_fields=['last_notified'])
                    except Exception as e:
                        # Log error but don't fail the save
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f'Failed to send match notification email: {str(e)}')

