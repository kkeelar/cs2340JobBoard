# accounts/views.py
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ProfileForm, EducationFormSet, WorkFormSet
from .models import Profile  # import your Profile model

User = get_user_model()


# ---------- Auth ----------

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # ensure a Profile exists for the new user
            Profile.objects.get_or_create(user=user)
            auth_login(request, user)  # auto-login after signup
            return redirect("profile")  # my profile
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect("profile")  # my profile
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
