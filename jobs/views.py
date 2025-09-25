from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import Job, JobApplication, SavedJob
from .forms import JobSearchForm, JobApplicationForm, JobPostForm, ApplicationStatusUpdateForm


def job_list(request):
    """Job search and listing page with filters"""
    form = JobSearchForm(request.GET or None)
    jobs = Job.objects.filter(is_active=True)
    
    # Apply search filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        location = form.cleaned_data.get('location')
        skills = form.cleaned_data.get('skills')
        salary_min = form.cleaned_data.get('salary_min')
        salary_max = form.cleaned_data.get('salary_max')
        work_type = form.cleaned_data.get('work_type')
        visa_sponsorship = form.cleaned_data.get('visa_sponsorship')
        
        # Text search across title, company, and description
        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(company__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Location filter
        if location:
            jobs = jobs.filter(location__icontains=location)
        
        # Skills filter
        if skills:
            skill_list = [skill.strip() for skill in skills.split(',')]
            skill_query = Q()
            for skill in skill_list:
                skill_query |= Q(required_skills__icontains=skill)
            jobs = jobs.filter(skill_query)
        
        # Salary filters
        if salary_min:
            jobs = jobs.filter(
                Q(salary_min__gte=salary_min) | Q(salary_min__isnull=True)
            )
        if salary_max:
            jobs = jobs.filter(
                Q(salary_max__lte=salary_max) | Q(salary_max__isnull=True)
            )
        
        # Work type filter
        if work_type:
            jobs = jobs.filter(work_type=work_type)
        
        # Visa sponsorship filter
        if visa_sponsorship:
            jobs = jobs.filter(visa_sponsorship=True)
    
    # Pagination
    paginator = Paginator(jobs, 12)  # Show 12 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get user's saved jobs and applications for UI hints
    saved_job_ids = []
    applied_job_ids = []
    if request.user.is_authenticated:
        saved_job_ids = list(
            SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True)
        )
        applied_job_ids = list(
            JobApplication.objects.filter(applicant=request.user).values_list('job_id', flat=True)
        )
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'jobs': page_obj,
        'saved_job_ids': saved_job_ids,
        'applied_job_ids': applied_job_ids,
        'total_jobs': paginator.count,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, pk):
    """Individual job detail page"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    
    # Check if user has already applied or saved this job
    user_application = None
    has_saved = False
    if request.user.is_authenticated:
        try:
            user_application = JobApplication.objects.get(job=job, applicant=request.user)
        except JobApplication.DoesNotExist:
            pass
        
        has_saved = SavedJob.objects.filter(user=request.user, job=job).exists()
    
    context = {
        'job': job,
        'user_application': user_application,
        'has_saved': has_saved,
        'required_skills': job.get_required_skills_list(),
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def apply_to_job(request, pk):
    """One-click job application with optional cover note"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    
    # Check if user already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied to this job.')
        return redirect('job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            
            messages.success(request, f'Successfully applied to {job.title} at {job.company}!')
            return redirect('my_applications')
    else:
        form = JobApplicationForm()
    
    context = {
        'job': job,
        'form': form,
    }
    return render(request, 'jobs/apply_to_job.html', context)


@login_required
def my_applications(request):
    """Dashboard showing user's job applications with status tracking"""
    applications = JobApplication.objects.filter(applicant=request.user)
    
    # Group by status for dashboard view
    status_counts = {
        'applied': applications.filter(status='applied').count(),
        'review': applications.filter(status='review').count(),
        'interview': applications.filter(status='interview').count(),
        'offer': applications.filter(status='offer').count(),
        'closed': applications.filter(status='closed').count(),
    }
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter and status_filter in dict(JobApplication.STATUS_CHOICES):
        applications = applications.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'applications': page_obj,
        'status_counts': status_counts,
        'current_status_filter': status_filter,
        'status_choices': JobApplication.STATUS_CHOICES,
    }
    return render(request, 'jobs/my_applications.html', context)


@login_required
def application_detail(request, pk):
    """Detailed view of a specific application"""
    application = get_object_or_404(JobApplication, pk=pk, applicant=request.user)
    
    context = {
        'application': application,
        'job': application.job,
    }
    return render(request, 'jobs/application_detail.html', context)


@login_required
@require_POST
def save_job(request, pk):
    """AJAX endpoint to save/unsave a job"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    
    saved_job, created = SavedJob.objects.get_or_create(
        user=request.user,
        job=job
    )
    
    if not created:
        # Job was already saved, so unsave it
        saved_job.delete()
        saved = False
    else:
        saved = True
    
    return JsonResponse({
        'saved': saved,
        'message': 'Job saved!' if saved else 'Job removed from saved jobs.'
    })


@login_required
def saved_jobs(request):
    """List of user's saved jobs"""
    saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job')
    
    # Pagination
    paginator = Paginator(saved_jobs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'saved_jobs': page_obj,
    }
    return render(request, 'jobs/saved_jobs.html', context)


@login_required
def post_job(request):
    """Form for posting a new job (staff/recruiters only)"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to post jobs.')
        return redirect('job_list')
    
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobPostForm()
    
    context = {
        'form': form,
    }
    return render(request, 'jobs/post_job.html', context)


@login_required
def manage_applications(request, job_pk):
    """View for recruiters to manage applications for their job postings"""
    job = get_object_or_404(Job, pk=job_pk, posted_by=request.user)
    applications = JobApplication.objects.filter(job=job)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    context = {
        'job': job,
        'applications': applications,
        'status_choices': JobApplication.STATUS_CHOICES,
        'current_status_filter': status_filter,
    }
    return render(request, 'jobs/manage_applications.html', context)


@login_required
def update_application_status(request, pk):
    """Update application status (recruiters only)"""
    application = get_object_or_404(JobApplication, pk=pk)
    
    # Check permissions
    if not (request.user == application.job.posted_by or request.user.is_staff):
        messages.error(request, 'You do not have permission to update this application.')
        return redirect('job_list')
    
    if request.method == 'POST':
        form = ApplicationStatusUpdateForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, f'Application status updated to {application.get_status_display()}.')
            return redirect('manage_applications', job_pk=application.job.pk)
    else:
        form = ApplicationStatusUpdateForm(instance=application)
    
    context = {
        'form': form,
        'application': application,
        'job': application.job,
    }
    return render(request, 'jobs/update_application_status.html', context)