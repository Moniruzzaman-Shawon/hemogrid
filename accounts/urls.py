from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from .views import (
    RegisterView,
    VerifyEmailView,
    DonorProfileView,
    PublicDonorListView,
    DashboardView,
    ResetPasswordView,
    ChangePasswordView,
    ForgotPasswordView,
    UpdateEmailView,
    UpdateAvailabilityView,
    AdminUserListView,
    AdminUserUpdateView,
    MyTokenObtainPairView
)

app_name = "auth"

urlpatterns = [
    # User registration and verification
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('update-email/', UpdateEmailView.as_view(), name='update-email'),
    path('update-availability/', UpdateAvailabilityView.as_view(), name='update-availability'),

    # Admin
    path('admin/users/', AdminUserListView.as_view(), name='admin-users-list'),
    path('admin/users/<int:pk>/update/', AdminUserUpdateView.as_view(), name='admin-user-update'),

    # JWT authentication
    path('login/', MyTokenObtainPairView.as_view(), name='login'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Donor profile & listing
    path('donor-profile/', DonorProfileView.as_view(), name='donor-profile'),
    path('donors/', PublicDonorListView.as_view(), name='donors'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Password management
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]

# Optionally register logout (blacklist) if app installed
try:
    if 'rest_framework_simplejwt.token_blacklist' in settings.INSTALLED_APPS:
        from rest_framework_simplejwt.views import TokenBlacklistView
        urlpatterns += [
            path('logout/', TokenBlacklistView.as_view(), name='logout'),
        ]
except Exception:
    pass
