from django.db import models
from django.contrib.auth.models import User
class Profile(models.Model):
    ROLE_CHOICES = [
        ('seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='seeker')

    # --- Shared fields ---
    email = models.EmailField(blank=True, null=True)
    headline = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated list of skills")
    links = models.TextField(blank=True, null=True, help_text="Comma-separated external links")

    # --- Recruiter-specific fields ---
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    position_title = models.CharField(max_length=100, blank=True, null=True, help_text="Your position at the company")

    # --- Privacy controls (for seekers only, ignored for recruiters) ---
    is_public = models.BooleanField(default=True, help_text="If off, only you and staff can see your profile.")
    show_email = models.BooleanField(default=False)
    show_links = models.BooleanField(default=True)
    show_education = models.BooleanField(default=True)
    show_work = models.BooleanField(default=True)
    show_skills = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_recruiter(self):
        return self.role == 'recruiter'

    def is_seeker(self):
        return self.role == 'seeker'

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="education")
    school = models.CharField(
        max_length=255,
        error_messages={"blank": "Please enter the name of your school."},
    )
    major = models.CharField(max_length=120, blank=True, null=True, default="")
    minor = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(
        blank=False, null=False,
        error_messages={"required": "Please provide a start date."}
    )
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.school} ({self.major})"

class WorkExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="work_experience")
    company = models.CharField(
        max_length=255,
        error_messages={"blank": "Please enter your company name."},
    )
    position = models.CharField(
        max_length=255,
        error_messages={"blank": "Please enter your job title."},
    )
    start_date = models.DateField(
        blank=False, null=False,
        error_messages={"required": "Please provide a start date."}
    )
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.position} at {self.company}"


