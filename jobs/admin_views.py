"""
Admin-only views for reporting and CSV exports
"""
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from jobs.models import Job, JobApplication, SavedJob, SavedCandidateSearch
from jobs.export_utils import (
    export_jobs_csv, export_applications_csv, 
    export_users_csv, export_profiles_csv, export_usage_stats_csv
)
from accounts.models import Profile
from django.contrib.auth.models import User


@staff_member_required
def admin_reporting_dashboard(request):
    """Admin dashboard for reporting and data exports"""
    
    # Calculate statistics
    total_users = User.objects.count()
    total_recruiters = Profile.objects.filter(role='recruiter').count()
    total_seekers = Profile.objects.filter(role='seeker').count()
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    total_applications = JobApplication.objects.count()
    
    # Applications by status (for template)
    applications_by_status_list = []
    for status_code, status_name in JobApplication.STATUS_CHOICES:
        count = JobApplication.objects.filter(status=status_code).count()
        applications_by_status_list.append({'code': status_code, 'name': status_name, 'count': count})
    
    # Also create a dict for easy lookup in template
    applications_by_status = {item['code']: item for item in applications_by_status_list}
    
    # Jobs by work type
    jobs_by_work_type = {}
    for work_type_code, work_type_name in Job.WORK_TYPE_CHOICES:
        count = Job.objects.filter(work_type=work_type_code).count()
        jobs_by_work_type[work_type_name] = count
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_jobs = Job.objects.filter(posted_date__gte=thirty_days_ago).count()
    recent_applications = JobApplication.objects.filter(applied_date__gte=thirty_days_ago).count()
    recent_users = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Top recruiters by job count
    top_recruiters = Profile.objects.filter(role='recruiter').annotate(
        job_count=Count('posted_jobs')
    ).order_by('-job_count')[:10]
    
    # Jobs with most applications
    top_jobs = Job.objects.annotate(
        application_count=Count('applications')
    ).order_by('-application_count')[:10]
    
    context = {
        'total_users': total_users,
        'total_recruiters': total_recruiters,
        'total_seekers': total_seekers,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'applications_by_status': applications_by_status,
        'applications_by_status_list': applications_by_status_list,
        'jobs_by_work_type': jobs_by_work_type,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
        'recent_users': recent_users,
        'top_recruiters': top_recruiters,
        'top_jobs': top_jobs,
    }
    
    return render(request, 'jobs/admin_reporting_dashboard.html', context)


@staff_member_required
def export_jobs(request):
    """Export all jobs to CSV"""
    # Allow filtering by active/inactive
    is_active = request.GET.get('is_active')
    queryset = Job.objects.select_related('posted_by__user').all()
    
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active.lower() == 'true')
    
    return export_jobs_csv(queryset)


@staff_member_required
def export_applications(request):
    """Export all job applications to CSV"""
    # Allow filtering by status
    status = request.GET.get('status')
    queryset = JobApplication.objects.select_related('job', 'applicant__profile').all()
    
    if status:
        queryset = queryset.filter(status=status)
    
    return export_applications_csv(queryset)


@staff_member_required
def export_users(request):
    """Export all users to CSV"""
    # Allow filtering by role
    role = request.GET.get('role')
    queryset = User.objects.select_related('profile').all()
    
    if role:
        queryset = queryset.filter(profile__role=role)
    
    return export_users_csv(queryset)


@staff_member_required
def export_profiles(request):
    """Export all profiles to CSV"""
    # Allow filtering by role
    role = request.GET.get('role')
    queryset = Profile.objects.select_related('user').all()
    
    if role:
        queryset = queryset.filter(role=role)
    
    return export_profiles_csv(queryset)


@staff_member_required
def export_usage_stats(request):
    """Export usage statistics to CSV"""
    return export_usage_stats_csv()

