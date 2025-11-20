from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # User log in / sign up
    path("recruiter/dashboard/", views.recruiter_dashboard, name="recruiter_dashboard"),

    # Job browsing
    path('', views.job_list, name='job_list'),
    path('<int:pk>/', views.job_detail, name='job_detail'),

    # Job applications
    path('<int:pk>/apply/', views.apply_to_job, name='apply_to_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),

    
    # Recommendations
    path('recommended/', views.recommended_jobs, name='recommended_jobs'),
    
    # Saved jobs
    path('<int:pk>/save/', views.save_job, name='save_job'),
    path('saved/', views.saved_jobs, name='saved_jobs'),

    # Job posting (for recruiters/staff)
    path('post/', views.post_job, name='post_job'),
    path('<int:job_pk>/applications/', views.manage_applications, name='manage_applications'),
    path('applications/<int:pk>/update/', views.update_application_status, name='update_application_status'),

    path("<int:pk>/edit/", views.edit_job, name="edit_job"),
    path('<int:job_pk>/pipeline/', views.application_pipeline, name='application_pipeline'),
    path('<int:job_pk>/pipeline/', views.application_pipeline, name='application_pipeline'),

    path("api/jobs/", views.jobs_api, name="jobs_api"),
    path("api/recommendations/", views.recommendations_api, name="recommendations_api"),

    # Saved candidate searches
    path('searches/', views.saved_candidate_searches, name='saved_candidate_searches'),
    path('searches/create/', views.create_saved_search, name='create_saved_search'),
    path('searches/<int:pk>/edit/', views.edit_saved_search, name='edit_saved_search'),
    path('searches/<int:pk>/delete/', views.delete_saved_search, name='delete_saved_search'),
    path('searches/<int:pk>/matches/', views.saved_search_matches, name='saved_search_matches'),

    # Candidate recommendations for jobs
    path('<int:pk>/recommendations/', views.job_candidate_recommendations, name='job_candidate_recommendations'),

    # Applicant location map
    path('applicants/map/', views.applicant_location_map, name='applicant_location_map'),
    path('api/applicants/', views.applicants_api, name='applicants_api'),

    # Admin reporting and CSV exports
    path('admin/reporting/', admin_views.admin_reporting_dashboard, name='admin_reporting_dashboard'),
    path('admin/export/jobs/', admin_views.export_jobs, name='admin_export_jobs'),
    path('admin/export/applications/', admin_views.export_applications, name='admin_export_applications'),
    path('admin/export/users/', admin_views.export_users, name='admin_export_users'),
    path('admin/export/profiles/', admin_views.export_profiles, name='admin_export_profiles'),
    path('admin/export/stats/', admin_views.export_usage_stats, name='admin_export_stats'),

]
