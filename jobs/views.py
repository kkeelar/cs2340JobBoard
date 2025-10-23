from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from math import pi, sin, cos, asin, sqrt

from django.views.decorators.http import require_POST

from .models import Job, JobApplication, SavedJob
from .forms import JobSearchForm, JobApplicationForm, JobPostForm, ApplicationStatusUpdateForm
from .recommendations import (
    format_skills_for_display,
    recommend_jobs_for_profile,
)

@login_required
def recruiter_dashboard(request):
    """Dashboard for recruiters showing their postings and stats"""
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "recruiter":
        return redirect("home")

    jobs = Job.objects.filter(posted_by=request.user.profile)
    total_jobs = jobs.count()
    total_applicants = JobApplication.objects.filter(job__in=jobs).count()


    context = {
        "jobs": jobs,
        "total_jobs": total_jobs,
        "total_applicants": total_applicants,
    }
    return render(request, "jobs/recruiter_dashboard.html", context)



def job_list(request):
    """Job search and listing page with filters"""
    form = JobSearchForm(request.GET or None)
    jobs = Job.objects.filter(is_active=True)
    location_lat = None
    location_lon = None
    location_radius_value = form.fields["location_radius"].initial or 25

    # Apply search filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        location = form.cleaned_data.get('location')
        location_lat = form.cleaned_data.get('location_lat')
        location_lon = form.cleaned_data.get('location_lon')
        location_radius_value = form.cleaned_data.get('location_radius') or location_radius_value
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

        # Location filter (distance-based when coordinates are provided)
        if location_lat is not None and location_lon is not None:
            try:
                radius = float(location_radius_value or 25)
            except (TypeError, ValueError):
                radius = 25
            filtered_jobs = []
            for job in jobs.exclude(latitude__isnull=True).exclude(longitude__isnull=True):
                if job.latitude is None or job.longitude is None:
                    continue
                distance = _haversine_miles(location_lat, location_lon, job.latitude, job.longitude)
                if distance <= radius:
                    job.search_distance = round(distance, 1)
                    filtered_jobs.append(job)
            filtered_jobs.sort(key=lambda j: getattr(j, "search_distance", 0))
            jobs = filtered_jobs
        elif location:
            jobs = jobs.filter(location__icontains=location)

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
        'location_filter_active': location_lat is not None and location_lon is not None,
        'location_lat': location_lat,
        'location_lon': location_lon,
        'location_radius': location_radius_value,
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
def recommended_jobs(request):
    """Skill-based recommendations for job seekers."""
    profile = getattr(request.user, "profile", None)
    if not profile:
        messages.error(request, "Please complete your profile to receive recommendations.")
        return redirect("job_list")

    if profile.role == "recruiter":
        messages.info(request, "Recommendations are only available for job seekers.")
        return redirect("recruiter_dashboard")

    recommendations = recommend_jobs_for_profile(profile)
    user_skills = format_skills_for_display(profile.skills)

    context = {
        "recommendations": recommendations,
        "user_skills": user_skills,
        "has_skills": bool(user_skills),
    }
    return render(request, "jobs/recommended_jobs.html", context)


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
    """Recruiters can post new jobs"""
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "recruiter":
        messages.error(request, "Only recruiters can post jobs.")
        return redirect("job_list")

    if request.method == "POST":
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = profile  # ✅ tie to recruiter profile
            job.save()
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect("recruiter_dashboard")
    else:
        form = JobPostForm()

    return render(request, "jobs/post_job.html", {"form": form})



@login_required
def manage_applications(request, job_pk):
    """View for recruiters to manage applications for their job postings"""
    job = get_object_or_404(Job, pk=job_pk, posted_by=request.user.profile)
    return redirect('application_pipeline', job_pk=job.pk)


@login_required
def update_application_status(request, pk):
    """Update application status (recruiters only)"""
    application = get_object_or_404(JobApplication, pk=pk)

    # Check permissions
    if not (request.user.profile == application.job.posted_by or request.user.is_staff):
        messages.error(request, 'You do not have permission to update this application.')
        return redirect('job_list')

    if request.method == 'POST':
        form = ApplicationStatusUpdateForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, f'Application status updated to {application.get_status_display()}.')
            return redirect('application_pipeline', job_pk=application.job.pk)
    else:
        form = ApplicationStatusUpdateForm(instance=application)

    context = {
        'form': form,
        'application': application,
        'job': application.job,
    }
    return render(request, 'jobs/update_application_status.html', context)

@login_required
def edit_job(request, pk):
    """Allow recruiters to edit their own job postings"""
    profile = getattr(request.user, "profile", None)
    job = get_object_or_404(Job, pk=pk, posted_by=profile)

    if profile.role != "recruiter":
        messages.error(request, "Only recruiters can edit jobs.")
        return redirect("job_list")

    if request.method == "POST":
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f'Job "{job.title}" updated successfully!')
            return redirect("application_pipeline", job_pk=job.pk)
    else:
        form = JobPostForm(instance=job)

    return render(request, "jobs/edit_job.html", {"form": form, "job": job})


@login_required
def application_pipeline(request, job_pk):
    """Kanban-style pipeline for managing applicants"""
    job = get_object_or_404(Job, pk=job_pk, posted_by=request.user.profile)

    # Group applications by status
    applications_by_status = {
        status[0]: JobApplication.objects.filter(job=job, status=status[0])
        for status in JobApplication.STATUS_CHOICES
    }

    context = {
        "job": job,
        "applications_by_status": applications_by_status,
        "status_choices": JobApplication.STATUS_CHOICES,
    }
    return render(request, "jobs/application_pipeline.html", context)


@login_required
@require_POST
def update_application_status(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    if request.user.profile != application.job.posted_by:
        messages.error(request, "Unauthorized")
        return redirect("recruiter_dashboard")

    new_status = request.POST.get("status")
    if new_status not in dict(JobApplication.STATUS_CHOICES):
        messages.error(request, "Invalid status")
    else:
        application.status = new_status
        application.save()
        messages.success(request, f"Moved {application.applicant.username} to {application.get_status_display()}")

    return redirect("application_pipeline", job_pk=application.job.pk)


def _haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    p = pi / 180
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = (sin(dlat/2)**2) + cos(lat1*p) * cos(lat2*p) * (sin(dlon/2)**2)
    return 2 * R * asin(sqrt(a))

def jobs_api(request):
    """
    GET /jobs/api/jobs?lat=..&lon=..&radius_miles=..
    If Job has latitude/longitude fields, returns nearby jobs; otherwise empty list.
    """
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    radius = request.GET.get("radius_miles")

    # Only include jobs with lat/lon if those fields exist
    qs = Job.objects.all()
    has_latlon = all(hasattr(Job, f) for f in ["latitude", "longitude"])

    items = []
    if has_latlon:
        qs = qs.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
        if lat and lon and radius:
            lat_f, lon_f, radius_f = float(lat), float(lon), float(radius)
        else:
            lat_f = lon_f = radius_f = None

        for job in qs:
            if job.latitude is None or job.longitude is None:
                continue

            distance = None
            if lat_f is not None and lon_f is not None and radius_f is not None:
                distance = _haversine_miles(lat_f, lon_f, job.latitude, job.longitude)
                if distance > radius_f:
                    continue

            items.append({
                "id": job.id,
                "title": job.title,
                "company": job.company or "",
                "location": job.location or "",
                "lat": job.latitude,
                "lon": job.longitude,
                "distance_miles": round(distance, 2) if distance is not None else None,
                "url": reverse("job_detail", args=[job.id]),
            })

    return JsonResponse({"jobs": items})

@login_required
def recommendations_api(request):
    """
    Returns recommended jobs. If you add a profile.skills M2M and job.required_skills M2M,
    this will sort by overlap. Otherwise it falls back to recent jobs.
    """
    profile = getattr(request.user, "profile", None)
    if not profile:
        return JsonResponse({"recommendations": []})

    recs = recommend_jobs_for_profile(profile, limit=12)
    data = [{
        "id": rec.job.id,
        "title": rec.job.title,
        "company": rec.job.company or "",
        "location": rec.job.location or "",
        "matched_skills": list(rec.matched_skills),
        "score": rec.score,
        "url": reverse("job_detail", args=[rec.job.id]),
    } for rec in recs]

    return JsonResponse({"recommendations": data})
