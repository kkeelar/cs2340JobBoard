from django import forms
from django.forms import inlineformset_factory
from .models import Profile, Education, WorkExperience


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["headline", "bio", "location", "skills", "links"]
        labels = {
            "headline": "Headline",
            "bio": "Bio",
            "location": "Location",
            "skills": "Skills (comma-separated)",
            "links": "Links (comma-separated URLs)",
        }
        widgets = {
            "headline": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "skills": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "links": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
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
