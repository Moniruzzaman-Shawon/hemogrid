from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from .views import RegisterView, VerifyEmailView, DonorProfileView, DonorListView, DashboardView, PublicDonorListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),

    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),

    path('donor-profile/', DonorProfileView.as_view(), name='donor-profile'),
    path('donors/', PublicDonorListView.as_view(), name='public-donor-list'),    
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('donor/profile/', DonorProfileView.as_view(), name='donor-profile'),

]
