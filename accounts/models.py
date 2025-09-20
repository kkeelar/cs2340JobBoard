from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True)  # editable email
    headline = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)  # could later become ManyToMany
    links = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="education")
    school = models.CharField(
        max_length=255,
        error_messages={"blank": "Please enter the name of your school."},
    )
    major = models.CharField(
        max_length=255,
        error_messages={"blank": "Please enter your major."},
    )
    minor = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(
        error_messages={"null": "Please provide a start date."}
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
        error_messages={"null": "Please provide a start date."}
    )
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.position} at {self.company}"
