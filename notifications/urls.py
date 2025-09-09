from django.urls import path
from .views import UserNotificationsView, MarkNotificationReadView

urlpatterns = [
    path('', UserNotificationsView.as_view(), name='notification-list'),
    path('mark-read/<int:pk>/', MarkNotificationReadView.as_view(), name='notification-mark-read'),
]
