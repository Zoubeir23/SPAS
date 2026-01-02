"""
Authentication URL configuration with enhanced security features.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views

app_name = 'authentication'

urlpatterns = [
    # Registration & Email Verification
    path('register/', views.register_view, name='register'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),

    # Login & Logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('logout-all/', views.logout_all_devices_view, name='logout_all_devices'),

    # JWT Token Management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist-status/', views.check_token_blacklist_view, name='token_blacklist_status'),

    # Password Management
    path('password/forgot/', views.password_reset_request_view, name='password_reset_request'),
    path('password/reset/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('password/change/', views.change_password_view, name='change_password'),
    path('password/check-strength/', views.check_password_strength_view, name='check_password_strength'),

    # User Information
    path('me/', views.current_user_view, name='current_user'),
    path('activity/', views.auth_activity_view, name='auth_activity'),
]
