from django.contrib import admin
from .models import Job, JobApplication, SavedJob, SavedCandidateSearch, CandidateSearchMatch


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


@admin.register(SavedCandidateSearch)
class SavedCandidateSearchAdmin(admin.ModelAdmin):
    list_display = ['name', 'recruiter', 'is_active', 'match_count', 'created_date', 'last_checked', 'last_notified']
    list_filter = ['is_active', 'created_date', 'last_checked']
    search_fields = ['name', 'recruiter__user__username', 'search_query', 'location', 'skills']
    readonly_fields = ['created_date', 'last_checked', 'last_notified']
    list_editable = ['is_active']
    date_hierarchy = 'created_date'
    ordering = ['-created_date']
    
    def match_count(self, obj):
        return obj.matches.count()
    match_count.short_description = 'Matches'
    
    fieldsets = (
        ('Search Info', {
            'fields': ('name', 'recruiter', 'is_active')
        }),
        ('Search Criteria', {
            'fields': ('search_query', 'location', 'skills')
        }),
        ('Tracking', {
            'fields': ('created_date', 'last_checked', 'last_notified'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CandidateSearchMatch)
class CandidateSearchMatchAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'saved_search', 'first_matched_date', 'notified', 'notified_date']
    list_filter = ['notified', 'first_matched_date', 'notified_date']
    search_fields = ['candidate__user__username', 'saved_search__name']
    readonly_fields = ['first_matched_date', 'notified_date']
    date_hierarchy = 'first_matched_date'
    ordering = ['-first_matched_date']