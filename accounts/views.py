from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, EducationFormSet, WorkFormSet
from .models import Education, WorkExperience

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # auto-login after signup
            return redirect("profile")
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect("profile")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def profile(request):
    profile = request.user.profile
    skills = [s.strip() for s in profile.skills.split(",")] if profile.skills else []
    return render(request, "accounts/profile.html", {"profile": profile, "skills": skills})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, EducationFormSet, WorkFormSet


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        profile_form = ProfileForm(request.POST, instance=profile)
        edu_formset = EducationFormSet(request.POST, instance=profile)
        work_formset = WorkFormSet(request.POST, instance=profile)

        if profile_form.is_valid() and edu_formset.is_valid() and work_formset.is_valid():
            profile_form.save()
            edu_formset.save()
            work_formset.save()
            return redirect("profile")  # ✅ go back to profile page
    else:
        profile_form = ProfileForm(instance=profile)
        edu_formset = EducationFormSet(instance=profile)
        work_formset = WorkFormSet(instance=profile)

    return render(request, "accounts/edit_profile.html", {
        "profile_form": profile_form,
        "edu_formset": edu_formset,
        "work_formset": work_formset,
    })