from django import forms
from .models import Job, JobApplication


class JobSearchForm(forms.Form):
    """Form for searching and filtering jobs"""

    # Text search
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search job titles, companies, or keywords...',
        }),
        label='Search'
    )

    # Location filter
    location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, State, or "Remote"',
        }),
        label='Location'
    )

    location_lat = forms.FloatField(
        required=False,
        widget=forms.HiddenInput(),
    )

    location_lon = forms.FloatField(
        required=False,
        widget=forms.HiddenInput(),
    )

    location_radius = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 250,
            'step': 1,
        }),
        label='Radius (miles)',
        initial=25,
        help_text='Applies when a suggested address or your location is selected.',
    )

    # Skills filter
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Python, JavaScript, React',
        }),
        label='Skills',
        help_text='Comma-separated skills'
    )

    # Salary range
    salary_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '50000',
            'min': 0,
        }),
        label='Minimum Salary'
    )

    salary_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '150000',
            'min': 0,
        }),
        label='Maximum Salary'
    )

    # Work type
    work_type = forms.ChoiceField(
        choices=[('', 'Any')] + Job.WORK_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Work Type'
    )

    # Visa sponsorship
    visa_sponsorship = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Requires Visa Sponsorship'
    )


class JobApplicationForm(forms.ModelForm):
    """Form for applying to a job"""

    class Meta:
        model = JobApplication
        fields = ['cover_note']
        widgets = {
            'cover_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write a personalized note to explain why you\'re interested in this position...',
            }),
        }
        labels = {
            'cover_note': 'Cover Note (Optional)',
        }
        help_texts = {
            'cover_note': 'Add a personal touch to your application to stand out to recruiters.',
        }


class JobPostForm(forms.ModelForm):
    """Form for posting a new job (for recruiters/admins)"""

    class Meta:
        model = Job
        fields = [
            'title', 'description', 'company', 'location',
            'salary_min', 'salary_max', 'required_skills',
            'work_type', 'visa_sponsorship', 'job_type',
            'experience_level', 'application_deadline', 'contact_email',
            'latitude', 'longitude',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., San Francisco, CA or Remote'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'required_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., Python, Django, React, JavaScript'
            }),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'visa_sponsorship': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'job_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Full-time, Part-time, Contract'}),
            'experience_level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Entry level, Mid-level, Senior'}),
            'application_deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'latitude':  forms.HiddenInput(),
            'longitude': forms.HiddenInput(),

        }
        labels = {
            'required_skills': 'Required Skills',
            'work_type': 'Work Arrangement',
            'visa_sponsorship': 'Offers Visa Sponsorship',
            'job_type': 'Employment Type',
            'experience_level': 'Experience Level',
            'application_deadline': 'Application Deadline',
            'contact_email': 'Contact Email',
        }
        help_texts = {
            'required_skills': 'Comma-separated list of skills',
            'salary_min': 'Minimum salary in USD',
            'salary_max': 'Maximum salary in USD',
            'application_deadline': 'Leave blank for no deadline',
        }


class ApplicationStatusUpdateForm(forms.ModelForm):
    """Form for recruiters to update application status"""

    class Meta:
        model = JobApplication
        fields = ['status', 'recruiter_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'recruiter_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Internal notes about this application...'
            }),
        }
        labels = {
            'recruiter_notes': 'Internal Notes',
        }
        help_texts = {
            'recruiter_notes': 'These notes are only visible to recruiters and staff.',
        }
