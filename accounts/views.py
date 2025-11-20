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
from .models import Conversation, Message, CandidateEmailLog
from .forms import MessageForm, EmailCandidateForm, ReplyForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

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
            # mirror the email onto the profile for easy access
            profile.email = user.email
            profile.save(update_fields=["role", "email"])

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

        # Detect whether formset data is present. The JS-driven page supplies management
        # forms; however some tests or minimal POSTs may only submit the profile form.
        has_edu = any(k.startswith('education-') for k in request.POST.keys())
        has_work = any(k.startswith('work_experience-') for k in request.POST.keys())

        edu_formset = EducationFormSet(request.POST, instance=prof, prefix="education") if has_edu else None
        work_formset = WorkFormSet(request.POST, instance=prof, prefix="work_experience") if has_work else None

        # Validate profile_form first
        if profile_form.is_valid():
            # If formsets were posted, require them to be valid as well
            if (edu_formset is None or edu_formset.is_valid()) and (work_formset is None or work_formset.is_valid()):
                profile = profile_form.save()
                # Keep User.email in sync with Profile.email
                new_email = profile_form.cleaned_data.get('email')
                if new_email is not None:
                    user = request.user
                    user.email = new_email
                    user.save(update_fields=['email'])
                    profile.email = new_email
                    profile.save(update_fields=['email'])

                if edu_formset is not None:
                    edu_formset.save()
                if work_formset is not None:
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


@login_required
def conversation_list(request):
    """List conversations involving the logged-in user (as recruiter or seeker)."""
    profile = request.user.profile
    # Find conversations where the user is sender or recipient via messages
    conversations_qs = (
        Conversation.objects.filter(
            Q(messages__sender=profile) | Q(messages__recipient=profile)
        )
        .distinct()
        .order_by("-created_at")
    )

    # Build a lightweight structure for the template to avoid complex queries in templates.
    convo_items = []
    # Prefetch messages and related users to reduce DB hits
    for conv in conversations_qs.prefetch_related('messages__sender__user', 'messages__recipient__user'):
        msgs = list(conv.messages.all())
        last = msgs[-1] if msgs else None
        # Determine other participant (exclude current user's profile)
        participants = {m.sender for m in msgs} | {m.recipient for m in msgs}
        other = None
        for p in participants:
            if p != profile:
                other = p
                break

        # Unread count for this conversation for current profile
        unread = sum(1 for m in msgs if (m.recipient_id == profile.id and not m.is_read))

        convo_items.append({
            'conversation': conv,
            'last_message': last,
            'other': other,
            'unread': unread,
        })

    return render(request, "accounts/messages_list.html", {"conversations": convo_items})


@login_required
def start_conversation(request, username):
    """Start or open a conversation with the candidate username."""
    # Only recruiters should initiate per product decision, but Option C allows recruiters to message any seeker.
    profile = request.user.profile
    target_user = get_object_or_404(get_user_model(), username=username)
    target_profile = get_object_or_404(Profile, user=target_user)

    # Only allow messaging a seeker
    if target_profile.role != 'seeker':
        messages.error(request, "You may only start conversations with job seekers.")
        return redirect("profile_detail", username=username)

    # Handle GET (show compose form) and POST (create or reuse conversation)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data['body']

            # Try to find an existing two-party conversation between the profiles
            conv_qs = Conversation.objects.filter(
                messages__sender__in=[profile, target_profile],
                messages__recipient__in=[profile, target_profile],
            ).distinct()
            conv = conv_qs.first() if conv_qs.exists() else None

            # Create conversation if needed
            if not conv:
                conv = Conversation.objects.create()

            # Determine recipient (the other profile)
            recipient = target_profile

            Message.objects.create(
                conversation=conv,
                sender=profile,
                recipient=recipient,
                body=body,
            )
            messages.success(request, 'Message sent.')
            return redirect('conversation_detail', pk=conv.pk)
    else:
        # GET: show compose form
        form = MessageForm()

    return render(request, 'accounts/start_conversation.html', {'form': form, 'candidate': target_profile})


@login_required
def conversation_detail(request, pk):
    conv = get_object_or_404(Conversation, pk=pk)
    profile = request.user.profile

    # Ensure the user is a participant (has messages in the conversation) or staff.
    participants = set()
    for m in conv.messages.all():
        participants.add(m.sender_id)
        participants.add(m.recipient_id)
    # Allow viewing if user is staff, a participant, or the conversation is empty
    if not (request.user.is_staff or profile.id in participants or not conv.messages.exists()):
        messages.error(request, "You are not permitted to view this conversation.")
        return redirect('profile')

    # Mark messages addressed to the current user as read
    conv.messages.filter(recipient=profile, is_read=False).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data['body']
            subject = form.cleaned_data.get('subject')
            # Determine recipient: if last message exists, flip sender/recipient; else require explicit recipient via POST
            last = conv.messages.last()
            if last and last.sender != profile:
                recipient = last.sender
            elif last:
                recipient = last.recipient
            else:
                # No messages yet - try to get recipient from query param
                recipient_username = request.GET.get('recipient')
                if recipient_username:
                    try:
                        user_model = get_user_model()
                        target_user = user_model.objects.get(username=recipient_username)
                        recipient = Profile.objects.get(user=target_user)
                    except Exception:
                        messages.error(request, 'Cannot determine recipient for this conversation.')
                        return redirect('conversation_detail', pk=conv.pk)
                else:
                    messages.error(request, 'Cannot determine recipient for this conversation.')
                    return redirect('conversation_detail', pk=conv.pk)

            Message.objects.create(
                conversation=conv,
                sender=profile,
                recipient=recipient,
                body=body,
            )
            messages.success(request, 'Message sent.')
            return redirect('conversation_detail', pk=conv.pk)
    else:
        form = MessageForm()

    messages_qs = conv.messages.select_related('sender__user', 'recipient__user')
    # Determine 'other' profile for header display
    other_profile = None
    participants = set()
    for m in conv.messages.all():
        participants.add(m.sender)
        participants.add(m.recipient)
    for p in participants:
        if p != profile:
            other_profile = p
            break

    # If conversation empty (no messages) try to use recipient query param
    if not other_profile:
        recipient_username = request.GET.get('recipient')
        if recipient_username:
            try:
                user_model = get_user_model()
                target_user = user_model.objects.get(username=recipient_username)
                other_profile = Profile.objects.get(user=target_user)
            except Exception:
                other_profile = None

    return render(request, 'accounts/conversation_detail.html', {
        'conversation': conv,
        'messages': messages_qs,
        'form': form,
        'other_profile': other_profile,
    })


@login_required
def email_candidate(request, username):
    profile = request.user.profile
    target_user = get_object_or_404(get_user_model(), username=username)
    candidate = get_object_or_404(Profile, user=target_user)

    # Only allow emailing seekers
    if candidate.role != 'seeker':
        messages.error(request, "You may only email job seekers.")
        return redirect('profile_detail', username=username)

    # Candidate must have an email address either on profile or user
    to_email = candidate.email or candidate.user.email
    if not to_email:
        messages.error(request, 'This candidate does not have an email address listed.')
        return redirect('profile_detail', username=username)

    if request.method == 'POST':
        form = EmailCandidateForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            try:
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or None
                send_mail(subject, body, from_email, [to_email])
                CandidateEmailLog.objects.create(
                    recruiter=profile,
                    candidate=candidate,
                    subject=subject,
                    body=body,
                    success=True,
                )
                messages.success(request, 'Email sent successfully.')
                return redirect('profile_detail', username=username)
            except Exception as exc:
                CandidateEmailLog.objects.create(
                    recruiter=profile,
                    candidate=candidate,
                    subject=subject,
                    body=body,
                    success=False,
                    error_text=str(exc),
                )
                messages.error(request, 'Failed to send email: %s' % str(exc))
    else:
        form = EmailCandidateForm()

    return render(request, 'accounts/email_candidate_form.html', {'form': form, 'candidate': candidate})
