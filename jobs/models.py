from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from accounts.models import Profile


class Job(models.Model):
    """Job posting model with all required search and filter fields"""

    # Basic job info
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, help_text="City, State or 'Remote'")
    latitude  = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # Salary info
    salary_min = models.PositiveIntegerField(null=True, blank=True, help_text="Minimum salary in USD")
    salary_max = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum salary in USD")

    # Skills required (comma-separated for now, could be ManyToMany later)
    required_skills = models.TextField(blank=True, help_text="Comma-separated list of required skills")

    # Work arrangement
    WORK_TYPE_CHOICES = [
        ('remote', 'Remote'),
        ('onsite', 'On-site'),
        ('hybrid', 'Hybrid'),
    ]
    work_type = models.CharField(max_length=10, choices=WORK_TYPE_CHOICES, default='onsite')

    # Visa sponsorship
    visa_sponsorship = models.BooleanField(default=False, help_text="Does this job offer visa sponsorship?")

    # Job details
    job_type = models.CharField(max_length=50, default='Full-time', help_text="Full-time, Part-time, Contract, etc.")
    experience_level = models.CharField(max_length=50, default='Mid-level', help_text="Entry, Mid-level, Senior, etc.")

    # Meta
    posted_date = models.DateTimeField(default=timezone.now)
    application_deadline = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Contact info
    contact_email = models.EmailField()
    posted_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='posted_jobs')

    class Meta:
        ordering = ['-posted_date']

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_absolute_url(self):
        return reverse('job_detail', kwargs={'pk': self.pk})

    def get_required_skills_list(self):
        """Return skills as a list"""
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]

    def salary_range_display(self):
        """Return formatted salary range"""
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,}"
        elif self.salary_min:
            return f"${self.salary_min:,}+"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,}"
        return "Salary not specified"


class JobApplication(models.Model):
    """Job application with status tracking"""

    # Application status choices
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('review', 'Under Review'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('closed', 'Closed'),
    ]

    # Application info
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')

    # Application content
    cover_note = models.TextField(blank=True, help_text="Tailored note from applicant")

    # Timestamps
    applied_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    # Notes from recruiter/company
    recruiter_notes = models.TextField(blank=True, help_text="Internal notes (not visible to applicant)")

    class Meta:
        unique_together = ('job', 'applicant')  # Prevent duplicate applications
        ordering = ['-applied_date']

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse('application_detail', kwargs={'pk': self.pk})

    def get_status_badge_class(self):
        """Return Bootstrap badge class for status"""
        status_classes = {
            'applied': 'bg-primary',
            'review': 'bg-warning',
            'interview': 'bg-info',
            'offer': 'bg-success',
            'closed': 'bg-secondary',
        }
        return status_classes.get(self.status, 'bg-secondary')


class SavedJob(models.Model):
    """Allow users to save jobs for later"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-saved_date']

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"