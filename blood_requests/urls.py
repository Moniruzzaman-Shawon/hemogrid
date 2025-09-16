from django.urls import path
from .views import (
    BloodRequestCreateView,
    BloodRequestListView,
    AcceptBloodRequestView,
    UserDonationHistoryView,
    MyRequestsView, 
    DonationHistoryView,
    UpdateBloodRequestStatusView,
    AdminBloodRequestListView,
    AdminStatsView,
    RequestContactView,
    CompleteBloodRequestView,
    CancelBloodRequestView
)

urlpatterns = [
    # List all active blood requests (excluding own)
    path('', BloodRequestListView.as_view(), name='blood-request-list'),

    # Create a new blood request
    path('create/', BloodRequestCreateView.as_view(), name='blood-request-create'),

    # Accept a blood request
    path('<int:pk>/accept/', AcceptBloodRequestView.as_view(), name='blood-request-accept'),

    # Contact info for a request (only participants)
    path('<int:pk>/contact/', RequestContactView.as_view(), name='blood-request-contact'),

    # Update blood request status (only requester can do this)
    path('<int:pk>/update-status/', UpdateBloodRequestStatusView.as_view(), name='blood-request-update-status'),
    
    # Complete and cancel blood requests
    path('<int:pk>/complete/', CompleteBloodRequestView.as_view(), name='blood-request-complete'),
    path('<int:pk>/cancel/', CancelBloodRequestView.as_view(), name='blood-request-cancel'),

    # Requester's own requests
    path('my-requests/', MyRequestsView.as_view(), name='my-requests'),

    # Donor's donation history via blood requests (optional extra view)
    path('donation-history/', UserDonationHistoryView.as_view(), name='user-donation-history'),
    path('donation-history/all/', DonationHistoryView.as_view(), name='donation-history-all'),

    # Admin
    path('admin/requests/', AdminBloodRequestListView.as_view(), name='admin-requests-list'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),

]
