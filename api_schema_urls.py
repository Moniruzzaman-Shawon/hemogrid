from django.urls import path, include

# A minimal URLConf used only for schema generation, avoiding drf_yasg imports
urlpatterns = [
    path('api/', include('api.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/blood-requests/', include('blood_requests.urls')),
    path('api/donation/', include('donation.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/admin/', include('admin_api.urls')),
]

