from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),   # if you’ve made a custom login
    path("logout/", views.logout_view, name="logout"),  # use your view here
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    path("recruiter/dashboard/", views.recruiter_dashboard, name="recruiter_dashboard"),

    path("recruiter/search/", views.candidate_search, name="candidate_search"),



    # password management
    path("password_change/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("me/", views.profile, name="profile"),  # owner view
    path("edit/", views.edit_profile, name="edit_profile"),
    path("u/<str:username>/", views.profile_detail, name="profile_detail"),  # public view


]
