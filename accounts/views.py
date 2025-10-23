# accounts/views.py
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ProfileForm, EducationFormSet, WorkFormSet, CustomSignupForm
from .models import Profile  # import your Profile model
from jobs.models import Job, JobApplication

User = get_user_model()


def signup(request):
    if request.method == "POST":
        print(request.POST)
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get("role")

            # Save user first
            user = form.save(commit=False)
            user.email = form.cleaned_data.get("email")
            user.save()

            # Now override the profile created by signal
            profile = Profile.objects.get(user=user)
            profile.role = role
            profile.save(update_fields=["role"])

            auth_login(request, user)
            return redirect("recruiter_dashboard" if role == "recruiter" else "profile")

    else:
        form = CustomSignupForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # redirect based on role
            if hasattr(user, "profile") and user.profile.role == "recruiter":
                return redirect("recruiter_dashboard")
            return redirect("profile")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})



def logout_view(request):
    logout(request)
    return redirect("home")


# ---------- Helpers ----------

def _split_skills(skills_text):
    return [s.strip() for s in skills_text.split(",")] if skills_text else []


# ---------- Owner views (you) ----------

@login_required
def profile(request):
    """
    Owner-only 'My Profile' page.
    Shows everything regardless of privacy flags.
    """
    prof = request.user.profile
    skills = _split_skills(prof.skills)
    return render(request, "accounts/profile.html", {"profile": prof, "skills": skills})


@login_required
@transaction.atomic
def edit_profile(request):
    """
    Edit profile + inline Education and Work formsets.
    Uses prefixes matching your JS: 'education' and 'work_experience'
    """
    prof = request.user.profile
    if request.method == "POST":
        profile_form = ProfileForm(request.POST, instance=prof)
        edu_formset = EducationFormSet(request.POST, instance=prof, prefix="education")
        work_formset = WorkFormSet(request.POST, instance=prof, prefix="work_experience")
        if profile_form.is_valid() and edu_formset.is_valid() and work_formset.is_valid():
            profile_form.save()
            edu_formset.save()
            work_formset.save()
            return redirect("profile")  # back to owner view
    else:
        profile_form = ProfileForm(instance=prof)
        edu_formset = EducationFormSet(instance=prof, prefix="education")
        work_formset = WorkFormSet(instance=prof, prefix="work_experience")

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "profile_form": profile_form,
            "edu_formset": edu_formset,
            "work_formset": work_formset,
        },
    )


# ---------- Public profile (recruiter/other users) ----------

def profile_detail(request, username):
    """
    Public profile page for any user by username.
    - Owner and staff see everything.
    - Everyone else must respect privacy flags:
        * if profile.is_public is False -> 404
        * sections gated by show_email/show_links/show_education/show_work/show_skills
    """
    user = get_object_or_404(User, username=username)
    prof = get_object_or_404(Profile, user=user)

    is_owner = request.user.is_authenticated and (request.user == user)
    is_staff = request.user.is_authenticated and request.user.is_staff
    viewer_is_restricted = not (is_owner or is_staff)

    # If viewer is restricted and profile is private, hide existence
    if viewer_is_restricted and not prof.is_public:
        raise Http404("This profile is private.")

    skills = _split_skills(prof.skills)

    context = {
        "profile": prof,
        "skills": skills,
        "viewer_is_restricted": viewer_is_restricted,
        # Convenience flags for template logic (optional)
        "can_see_email": (not viewer_is_restricted) or (prof.show_email and bool(prof.email)),
        "can_see_links": (not viewer_is_restricted) or (prof.show_links and bool(prof.links)),
        "can_see_skills": (not viewer_is_restricted) or (prof.show_skills and bool(prof.skills)),
        "can_see_education": (not viewer_is_restricted) or prof.show_education,
        "can_see_work": (not viewer_is_restricted) or prof.show_work,
    }
    # Use a dedicated template for public view. You can also reuse accounts/profile.html if you prefer.
    return render(request, "accounts/profile_detail.html", context)

@login_required
def recruiter_dashboard(request):
    """Simple recruiter dashboard placeholder"""
    profile = request.user.profile
    if profile.role != "recruiter":
        return redirect("profile")  # block seekers

    jobs = Job.objects.filter(posted_by=profile)
    context = {
        "jobs": jobs,
        "total_jobs": jobs.count(),
        "total_applicants": JobApplication.objects.filter(job__in=jobs).count(),
    }
    return render(request, "jobs/recruiter_dashboard.html", context)

from django.db.models import Q

@login_required
def candidate_search(request):
    profile = request.user.profile
    if profile.role != "recruiter":
        return redirect("profile")

    query = request.GET.get("q", "")
    location = request.GET.get("location", "")
    skill = request.GET.get("skill", "")

    candidates = Profile.objects.filter(role="seeker", is_public=True)

    if query:
        candidates = candidates.filter(
            Q(user__username__icontains=query) |
            Q(headline__icontains=query) |
            Q(bio__icontains=query)
        )

    if location:
        candidates = candidates.filter(location__icontains=location)

    if skill:
        candidates = candidates.filter(skills__icontains=skill)

    if skill:
        candidates = candidates.filter(skills__icontains=skill)

    for c in candidates:
        raw_skills = c.skills or ""
        # Handle both comma-separated and space-separated input
        if "," in raw_skills:
            skills = raw_skills.split(",")
        else:
            skills = raw_skills.split()
        c.skill_list = [s.strip() for s in skills if s.strip()]

    return render(request, "accounts/candidate_search.html", {
        "candidates": candidates,
        "query": query,
        "location": location,
        "skill": skill,
    })
