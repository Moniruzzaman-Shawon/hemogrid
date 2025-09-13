from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework import permissions
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
try:
   from rest_framework.schemas.openapi import SchemaGenerator as DRFSchemaGenerator
except Exception:
   DRFSchemaGenerator = None
import logging


logger = logging.getLogger(__name__)

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


def safe_swagger_view(request):
   """Serve Swagger UI normally; serve OpenAPI JSON with a safe fallback.
   This prevents 500s in the UI when schema generation raises.
   """
   fmt = request.GET.get('format')
   if fmt == 'openapi':
      try:
         # Prefer DRF's built-in OpenAPI generator to avoid drf-yasg introspection issues
         if DRFSchemaGenerator is not None:
            factory = APIRequestFactory()
            drf_req = Request(factory.get('/'))
            generator = DRFSchemaGenerator(
               title="Hemogird: A Blood Donation & Request Management System",
               version="v1",
               urlconf='api_schema_urls',
            )
            schema = generator.get_schema(request=drf_req, public=True)
            return JsonResponse(schema)
         # Fallback to drf-yasg's generator if DRF one is unavailable
         return schema_view.without_ui(cache_timeout=0)(request)
      except Exception as exc:
         logger.exception("Swagger schema generation failed; returning minimal schema: %s", exc)
         fallback = {
            "openapi": "3.0.0",
            "info": {
               "title": "Hemogird: A Blood Donation & Request Management System",
               "version": "v1",
               "description": "HemoGrid API schema (fallback)",
               "termsOfService": "https://www.google.com/policies/terms/",
               "contact": {"email": "m.zaman.djp@gmail.com"},
               "license": {"name": "LICENSE"},
            },
            "paths": {},
         }
         return JsonResponse(fallback)
   # No format param: return the UI page
   return schema_view.with_ui('swagger', cache_timeout=0)(request)


def safe_redoc_view(request):
   fmt = request.GET.get('format')
   if fmt == 'openapi':
      try:
         if DRFSchemaGenerator is not None:
            factory = APIRequestFactory()
            drf_req = Request(factory.get('/'))
            generator = DRFSchemaGenerator(
               title="Hemogird: A Blood Donation & Request Management System",
               version="v1",
               urlconf='api_schema_urls',
            )
            schema = generator.get_schema(request=drf_req, public=True)
            return JsonResponse(schema)
         return schema_view.without_ui(cache_timeout=0)(request)
      except Exception as exc:
         logger.exception("ReDoc schema generation failed; returning minimal schema: %s", exc)
         fallback = {
            "openapi": "3.0.0",
            "info": {"title": "Hemogird: A Blood Donation & Request Management System", "version": "v1"},
            "paths": {},
         }
         return JsonResponse(fallback)
   return schema_view.with_ui('redoc', cache_timeout=0)(request)


urlpatterns = [
   path('admin/', admin.site.urls),

   # Admin API
   path('api/admin/', include('admin_api.urls')),

   #Redirect to the api
   path('', RedirectView.as_view(url='/api/', permanent=True)),


   path('swagger/', safe_swagger_view, name='schema-swagger-ui'),
   path('redoc/', safe_redoc_view, name='schema-redoc'),

   # JWT Auth
   path('api/auth/jwt/create/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
   path('api/auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

   # API home
   path('api/', include('api.urls')),

   # Accounts
   path('api/auth/', include('accounts.urls')),

   # Notifications
   path('api/notifications/', include('notifications.urls')),

   # Blood Requests
   path('api/blood-requests/', include('blood_requests.urls')),

   # Browsable API login
   path('api-auth/', include('rest_framework.urls')),

   path('api/donation/', include('donation.urls')),
]

if settings.DEBUG:
   import debug_toolbar
   urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
