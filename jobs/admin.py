from django.contrib import admin
from .models import Job, JobApplication, SavedJob


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'work_type', 'salary_range_display', 'posted_date', 'is_active']
    list_filter = ['work_type', 'visa_sponsorship', 'is_active', 'posted_date', 'experience_level']
    search_fields = ['title', 'company', 'location', 'required_skills']
    readonly_fields = ['posted_date']
    list_editable = ['is_active']
    date_hierarchy = 'posted_date'
    ordering = ['-posted_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'company', 'location')
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max')
        }),
        ('Requirements', {
            'fields': ('required_skills', 'experience_level', 'work_type', 'visa_sponsorship')
        }),
        ('Details', {
            'fields': ('job_type', 'contact_email', 'application_deadline')
        }),
        ('Meta', {
            'fields': ('posted_by', 'posted_date', 'is_active'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'applied_date', 'last_updated']
    list_filter = ['status', 'applied_date', 'last_updated']
    search_fields = ['applicant__username', 'job__title', 'job__company']
    readonly_fields = ['applied_date', 'last_updated']
    list_editable = ['status']
    date_hierarchy = 'applied_date'
    ordering = ['-applied_date']
    
    fieldsets = (
        ('Application Info', {
            'fields': ('job', 'applicant', 'status')
        }),
        ('Application Content', {
            'fields': ('cover_note',)
        }),
        ('Internal Notes', {
            'fields': ('recruiter_notes',)
        }),
        ('Timestamps', {
            'fields': ('applied_date', 'last_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'saved_date']
    list_filter = ['saved_date']
    search_fields = ['user__username', 'job__title', 'job__company']
    readonly_fields = ['saved_date']
    date_hierarchy = 'saved_date'
    ordering = ['-saved_date']