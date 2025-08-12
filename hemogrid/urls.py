from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('blood_requests.urls')),
    path('api-auth/', include('rest_framework.urls')),
    
]
