from django import forms
from django.forms import inlineformset_factory
from .models import Profile, Education, WorkExperience
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomSignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ('seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    ]
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            # allow editing email from the edit profile page
            "email",
            # existing fields:
            "headline", "bio", "location", "skills", "links",
            # privacy fields (new):
            "is_public", "show_email", "show_links", "show_education", "show_work", "show_skills",
        ]
        labels = {
            "headline": "Headline",
            "bio": "Bio",
            "location": "Location",
            "skills": "Skills (comma-separated)",
            "links": "Links (comma-separated URLs)",
            "is_public": "Public profile",
            "show_email": "Show email",
            "show_links": "Show links",
            "show_education": "Show education",
            "show_work": "Show work experience",
            "show_skills": "Show skills",
        }
        widgets = {
            # explicit widget for email so it appears nicely in edit form
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "headline": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "skills": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "links": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            # checkboxes:
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_email": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_links": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_education": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_work": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_skills": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

# Education formset
EducationFormSet = inlineformset_factory(
    Profile, Education,
    fields=("school", "major", "minor", "start_date", "end_date"),
    extra=0,  # don’t auto-show a blank row
    can_delete=True,
    labels={
        "school": "School Name",
        "major": "Major",
        "minor": "Minor (optional)",
        "start_date": "Start Date",
        "end_date": "End Date (required: expected or actual)",
    },
    widgets={
        "school": forms.TextInput(attrs={"class": "form-control"}),
        "major": forms.TextInput(attrs={"class": "form-control"}),
        "minor": forms.TextInput(attrs={"class": "form-control"}),
        "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    },
    error_messages={
        "school": {"required": "School name is required."},
        "major": {"required": "Major is required."},
        "start_date": {"required": "Start date is required."},
        "end_date": {"required": "End date or expected graduation date is required."},
    }
)


# Work formset
WorkFormSet = inlineformset_factory(
    Profile, WorkExperience,
    fields=("company", "position", "start_date", "end_date", "description"),
    extra=0,
    can_delete=True,
    labels={
        "company": "Company",
        "position": "Job Title",
        "start_date": "Start Date",
        "end_date": "End Date (leave blank if current job)",
        "description": "Description",
    },
    widgets={
        "company": forms.TextInput(attrs={"class": "form-control"}),
        "position": forms.TextInput(attrs={"class": "form-control"}),
        "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    },
    error_messages={
        "company": {"required": "Company name is required."},
        "position": {"required": "Job title is required."},
        "start_date": {"required": "Start date is required."},
    }
)


class MessageForm(forms.Form):
    # Conversation messages no longer include a subject — only body is required.
    body = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}), required=True)


class EmailCandidateForm(forms.Form):
    subject = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    body = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 6}), required=True)


class ReplyForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}), required=True)


class EmailEditForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Please provide an email address.")
        # allow the same email as current user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        qs = User.objects.filter(email__iexact=email)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email


