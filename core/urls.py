from django.contrib import admin
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import include
#rom django.urls import include


schema_view = get_schema_view(
    openapi.Info(
        title="WMS API",
        default_version="v1",
        description="API documentation for WMS",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="leanstixx@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', lambda request: JsonResponse({'message': 'Welcome to the WMS API!'}), name='welcome'),
    path('api/organizations/', include('organizations.urls')),
]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)