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
    AdminStatsView
)

urlpatterns = [
    # List all blood requests
    path('requests/', BloodRequestListView.as_view(), name='blood-request-list'),

    # Create a new blood request
    path('blood-requests/create/', BloodRequestCreateView.as_view(), name='blood-request-create'),

    # Accept a blood request
    path('blood-requests/<int:pk>/accept/', AcceptBloodRequestView.as_view(), name='blood-request-accept'),

    # Update blood request status (only requester can do this)
    path('blood-requests/<int:pk>/update-status/', UpdateBloodRequestStatusView.as_view(), name='blood-request-update-status'),

    # Requester's own requests
    path('my-requests/', MyRequestsView.as_view(), name='my-requests'),

    # Donor's donation history via blood requests (optional extra view)
    path('donation-history/', UserDonationHistoryView.as_view(), name='user-donation-history'),
    path('donation-history/all/', DonationHistoryView.as_view(), name='donation-history-all'),

    path('admin/requests/', AdminBloodRequestListView.as_view(), name='admin-requests-list'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),

]
