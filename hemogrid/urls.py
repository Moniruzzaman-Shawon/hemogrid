from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework import permissions
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Hemogird: A Blood Donation & Request Management System",
      default_version='v1',
      description=" HemoGrid is a RESTful Blood Donation & Request Management System designed to facilitate seamless communication between blood donors and recipients.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="m.zaman.djp@gmail.com"),
      license=openapi.License(name="LICENSE"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    #Redirect to the api
    path('', RedirectView.as_view(url='/api/', permanent=True)),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # JWT Auth
    path('api/auth/jwt/create/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API home
    path('api/', include('api.urls')),

    # Accounts
    path('api/auth/', include('accounts.urls')),

    # Blood Requests
    path('api/blood-requests/', include('blood_requests.urls')),

    # Browsable API login
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
