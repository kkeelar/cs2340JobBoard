"""
CSV Export Utilities for Admin Reporting
"""
import csv
from django.http import HttpResponse
from django.db.models import Count, Q
from datetime import datetime
from jobs.models import Job, JobApplication, SavedJob, SavedCandidateSearch
from accounts.models import Profile
from django.contrib.auth.models import User


def export_jobs_csv(queryset=None, include_stats=True):
    """Export jobs to CSV"""
    if queryset is None:
        queryset = Job.objects.select_related('posted_by__user').all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="jobs_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'ID', 'Title', 'Company', 'Location', 'Latitude', 'Longitude',
        'Salary Min', 'Salary Max', 'Work Type', 'Job Type', 'Experience Level',
        'Visa Sponsorship', 'Required Skills', 'Contact Email',
        'Posted By (Username)', 'Posted By (Email)', 'Posted Date',
        'Application Deadline', 'Is Active', 'Application Count',
        'Description'
    ])
    
    # Write data
    for job in queryset:
        posted_by_username = job.posted_by.user.username if job.posted_by else 'N/A'
        posted_by_email = job.posted_by.user.email if job.posted_by and job.posted_by.user else 'N/A'
        app_count = job.applications.count() if include_stats else 0
        
        writer.writerow([
            job.id,
            job.title,
            job.company,
            job.location,
            job.latitude or '',
            job.longitude or '',
            job.salary_min or '',
            job.salary_max or '',
            job.get_work_type_display(),
            job.job_type,
            job.experience_level,
            'Yes' if job.visa_sponsorship else 'No',
            job.required_skills,
            job.contact_email,
            posted_by_username,
            posted_by_email,
            job.posted_date.strftime('%Y-%m-%d %H:%M:%S') if job.posted_date else '',
            job.application_deadline.strftime('%Y-%m-%d %H:%M:%S') if job.application_deadline else '',
            'Yes' if job.is_active else 'No',
            app_count,
            job.description.replace('\n', ' ').replace('\r', ' ')[:500],  # Truncate long descriptions
        ])
    
    return response


def export_applications_csv(queryset=None):
    """Export job applications to CSV"""
    if queryset is None:
        queryset = JobApplication.objects.select_related('job', 'applicant__profile').all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="applications_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'ID', 'Job ID', 'Job Title', 'Company', 'Applicant Username',
        'Applicant Email', 'Applicant Full Name', 'Applicant Location',
        'Applicant Headline', 'Status', 'Applied Date', 'Last Updated',
        'Cover Note', 'Recruiter Notes'
    ])
    
    # Write data
    for app in queryset:
        applicant_profile = getattr(app.applicant, 'profile', None)
        applicant_name = app.applicant.get_full_name() or app.applicant.username
        applicant_email = app.applicant.email or (applicant_profile.email if applicant_profile else '')
        applicant_location = applicant_profile.location if applicant_profile else ''
        applicant_headline = applicant_profile.headline if applicant_profile else ''
        
        writer.writerow([
            app.id,
            app.job.id,
            app.job.title,
            app.job.company,
            app.applicant.username,
            applicant_email,
            applicant_name,
            applicant_location,
            applicant_headline,
            app.get_status_display(),
            app.applied_date.strftime('%Y-%m-%d %H:%M:%S') if app.applied_date else '',
            app.last_updated.strftime('%Y-%m-%d %H:%M:%S') if app.last_updated else '',
            app.cover_note.replace('\n', ' ').replace('\r', ' ')[:500],
            app.recruiter_notes.replace('\n', ' ').replace('\r', ' ')[:500],
        ])
    
    return response


def export_users_csv(queryset=None):
    """Export users to CSV"""
    if queryset is None:
        queryset = User.objects.select_related('profile').all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'ID', 'Username', 'Email', 'First Name', 'Last Name',
        'Is Staff', 'Is Superuser', 'Is Active', 'Date Joined', 'Last Login',
        'Role', 'Location', 'Headline', 'Company Name', 'Skills',
        'Profile Created', 'Total Applications', 'Total Jobs Posted'
    ])
    
    # Write data
    for user in queryset:
        profile = getattr(user, 'profile', None)
        role = profile.get_role_display() if profile else 'No Profile'
        location = profile.location if profile else ''
        headline = profile.headline if profile else ''
        company_name = profile.company_name if profile else ''
        skills = profile.skills if profile else ''
        
        # Count applications and jobs posted
        app_count = user.job_applications.count()
        jobs_posted = user.profile.posted_jobs.count() if profile else 0
        
        writer.writerow([
            user.id,
            user.username,
            user.email or '',
            user.first_name or '',
            user.last_name or '',
            'Yes' if user.is_staff else 'No',
            'Yes' if user.is_superuser else 'No',
            'Yes' if user.is_active else 'No',
            user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else '',
            user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
            role,
            location,
            headline,
            company_name,
            skills,
            'Yes' if profile else 'No',
            app_count,
            jobs_posted,
        ])
    
    return response


def export_profiles_csv(queryset=None):
    """Export profiles to CSV"""
    if queryset is None:
        queryset = Profile.objects.select_related('user').all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="profiles_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'ID', 'Username', 'Email', 'Role', 'Location', 'Latitude', 'Longitude',
        'Headline', 'Bio', 'Skills', 'Links', 'Company Name', 'Company Website',
        'Position Title', 'Is Public', 'Show Email', 'Show Links',
        'Show Education', 'Show Work', 'Show Skills'
    ])
    
    # Write data
    for profile in queryset:
        writer.writerow([
            profile.id,
            profile.user.username if profile.user else '',
            profile.email or (profile.user.email if profile.user else ''),
            profile.get_role_display(),
            profile.location or '',
            profile.latitude or '',
            profile.longitude or '',
            profile.headline or '',
            (profile.bio or '').replace('\n', ' ').replace('\r', ' ')[:500],
            profile.skills or '',
            profile.links or '',
            profile.company_name or '',
            profile.company_website or '',
            profile.position_title or '',
            'Yes' if profile.is_public else 'No',
            'Yes' if profile.show_email else 'No',
            'Yes' if profile.show_links else 'No',
            'Yes' if profile.show_education else 'No',
            'Yes' if profile.show_work else 'No',
            'Yes' if profile.show_skills else 'No',
        ])
    
    return response


def export_usage_stats_csv():
    """Export usage statistics to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="usage_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Calculate statistics
    total_users = User.objects.count()
    total_recruiters = Profile.objects.filter(role='recruiter').count()
    total_seekers = Profile.objects.filter(role='seeker').count()
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    total_applications = JobApplication.objects.count()
    total_saved_jobs = SavedJob.objects.count()
    total_saved_searches = SavedCandidateSearch.objects.count()
    
    # Applications by status
    apps_by_status = list(JobApplication.objects.values('status').annotate(count=Count('id')))
    
    # Jobs by work type
    jobs_by_work_type = list(Job.objects.values('work_type').annotate(count=Count('id')))
    
    # Write header
    writer.writerow(['Metric', 'Value'])
    
    # Write general stats
    writer.writerow(['Total Users', total_users])
    writer.writerow(['Total Recruiters', total_recruiters])
    writer.writerow(['Total Job Seekers', total_seekers])
    writer.writerow(['Total Jobs', total_jobs])
    writer.writerow(['Active Jobs', active_jobs])
    writer.writerow(['Inactive Jobs', total_jobs - active_jobs])
    writer.writerow(['Total Applications', total_applications])
    writer.writerow(['Total Saved Jobs', total_saved_jobs])
    writer.writerow(['Total Saved Candidate Searches', total_saved_searches])
    writer.writerow(['', ''])  # Empty row
    
    # Applications by status
    writer.writerow(['', ''])
    writer.writerow(['Applications by Status', ''])
    for item in apps_by_status:
        status_display = dict(JobApplication.STATUS_CHOICES).get(item['status'], item['status'])
        writer.writerow([status_display, item['count']])
    
    writer.writerow(['', ''])
    writer.writerow(['Jobs by Work Type', ''])
    for item in jobs_by_work_type:
        work_type_display = dict(Job.WORK_TYPE_CHOICES).get(item['work_type'], item['work_type'])
        writer.writerow([work_type_display, item['count']])
    
    return response

