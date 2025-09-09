from django.urls import path
from .views import (
    AdminUserListView,
    AdminUserSuspendView,
    AdminUserVerifyView,
    AdminBloodRequestListView,
    AdminStatsView,
)

urlpatterns = [
    # Users
    path('users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<int:pk>/suspend/', AdminUserSuspendView.as_view(), name='admin-user-suspend'),
    path('users/<int:pk>/verify/', AdminUserVerifyView.as_view(), name='admin-user-verify'),

    # Blood Requests
    path('requests/', AdminBloodRequestListView.as_view(), name='admin-blood-request-list'),

    # Statistics
    path('stats/', AdminStatsView.as_view(), name='admin-stats'),
]
