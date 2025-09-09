# api/urls.py
from django.urls import path
from .views import APIHomeView

urlpatterns = [
    path('', APIHomeView.as_view(), name='api-home'),
]
