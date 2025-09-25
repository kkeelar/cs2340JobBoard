from django.urls import path
from . import views

urlpatterns = [
    # Job browsing
    path('', views.job_list, name='job_list'),
    path('<int:pk>/', views.job_detail, name='job_detail'),
    
    # Job applications
    path('<int:pk>/apply/', views.apply_to_job, name='apply_to_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    
    # Saved jobs
    path('<int:pk>/save/', views.save_job, name='save_job'),
    path('saved/', views.saved_jobs, name='saved_jobs'),
    
    # Job posting (for recruiters/staff)
    path('post/', views.post_job, name='post_job'),
    path('<int:job_pk>/applications/', views.manage_applications, name='manage_applications'),
    path('applications/<int:pk>/update/', views.update_application_status, name='update_application_status'),
]
