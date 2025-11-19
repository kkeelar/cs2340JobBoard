from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Sequence

from django.db.models import QuerySet

from .models import Job, JobApplication, SavedJob
from accounts.models import Profile


SKILL_SPLIT_REGEX = re.compile(r"[,\n;/]+")


def split_skills(raw: str | None) -> List[str]:
    """Split a comma/newline-delimited skills string preserving original case."""
    if not raw:
        return []
    tokens: List[str] = []
    for token in SKILL_SPLIT_REGEX.split(raw):
        cleaned = token.strip()
        if cleaned:
            tokens.append(cleaned)
    return tokens


def parse_skills(raw: str | None) -> List[str]:
    """Return lower-cased skills for matching."""
    return [token.lower() for token in split_skills(raw)]


@dataclass
class RecommendedJob:
    job: Job
    matched_skills: Sequence[str]
    score: int


@dataclass
class RecommendedCandidate:
    candidate: Profile
    matched_skills: Sequence[str]
    score: int


def recommend_jobs_for_profile(profile, limit: int = 12) -> List[RecommendedJob]:
    """
    Return active job postings ordered by overlap with the seeker's skills.
    """
    seeker_skills = set(parse_skills(profile.skills))
    if not seeker_skills:
        return []

    # Exclude jobs the user has already applied to or saved
    user = profile.user
    applied_job_ids = JobApplication.objects.filter(applicant=user).values_list("job_id", flat=True)
    saved_job_ids = SavedJob.objects.filter(user=user).values_list("job_id", flat=True)

    jobs: QuerySet[Job] = (
        Job.objects.filter(is_active=True)
        .exclude(id__in=applied_job_ids)
        .exclude(id__in=saved_job_ids)
        .select_related("posted_by__user")
    )

    recommendations: List[RecommendedJob] = []

    for job in jobs:
        job_tokens = split_skills(job.required_skills)
        if not job_tokens:
            continue
        job_skill_map = {token.lower(): token for token in job_tokens}
        job_skill_keys = set(job_skill_map.keys())

        matched_keys = seeker_skills & job_skill_keys
        if not matched_keys:
            continue
        matched_display: List[str] = []
        seen = set()
        for token in job_tokens:
            key = token.lower()
            if key in matched_keys and key not in seen:
                matched_display.append(token)
                seen.add(key)
        recommendations.append(
            RecommendedJob(
                job=job,
                matched_skills=matched_display,
                score=len(matched_keys),
            )
        )

    recommendations.sort(key=lambda rec: (rec.score, rec.job.posted_date), reverse=True)
    return recommendations[:limit]


def format_skills_for_display(raw: str | None) -> List[str]:
    """Return user-friendly casing for skills."""
    return split_skills(raw)


def recommend_candidates_for_job(job: Job, limit: int = 12) -> List[RecommendedCandidate]:
    """
    Return job seekers (candidates) ordered by overlap with the job's required skills.
    Only returns candidates with public profiles.
    """
    job_skills = set(parse_skills(job.required_skills))
    if not job_skills:
        return []

    # Get all public job seeker profiles
    candidates: QuerySet[Profile] = (
        Profile.objects.filter(role='seeker', is_public=True)
        .select_related('user')
    )

    # Exclude candidates who have already applied
    applied_user_ids = JobApplication.objects.filter(job=job).values_list("applicant_id", flat=True)
    candidates = candidates.exclude(user_id__in=applied_user_ids)

    recommendations: List[RecommendedCandidate] = []

    for candidate in candidates:
        candidate_skills = set(parse_skills(candidate.skills))
        if not candidate_skills:
            continue

        # Calculate skill overlap
        matched_keys = job_skills & candidate_skills
        if not matched_keys:
            continue

        # Get display names for matched skills (preserve original casing)
        candidate_tokens = split_skills(candidate.skills)
        candidate_skill_map = {token.lower(): token for token in candidate_tokens}
        matched_display: List[str] = []
        seen = set()
        for key in matched_keys:
            if key in candidate_skill_map and key not in seen:
                matched_display.append(candidate_skill_map[key])
                seen.add(key)

        recommendations.append(
            RecommendedCandidate(
                candidate=candidate,
                matched_skills=matched_display,
                score=len(matched_keys),
            )
        )

    # Sort by score (number of matched skills) and then by most recent profile update
    recommendations.sort(key=lambda rec: (rec.score, rec.candidate.user.date_joined), reverse=True)
    return recommendations[:limit]
