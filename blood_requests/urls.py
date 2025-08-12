from django.urls import path
from .views import (
    BloodRequestCreateView,
    BloodRequestListView,
    AcceptBloodRequestView,
    UserDonationHistoryView,
    MyRequestsView, 
    DonationHistoryView
)

urlpatterns = [
    path('requests/', BloodRequestListView.as_view(), name='blood-request-list'),
    path('blood-requests/create/', BloodRequestCreateView.as_view(), name='blood-request-create'),
    path('blood-requests/<int:pk>/accept/', AcceptBloodRequestView.as_view(), name='blood-request-accept'),
    path('donation-history/', UserDonationHistoryView.as_view(), name='donation-history'),
    path('my-requests/', MyRequestsView.as_view(), name='my-requests'),
    path('donation-history/', DonationHistoryView.as_view(), name='donation-history'),
    
]
