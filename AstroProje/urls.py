from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin Panel Özelleştirmeleri
admin.site.site_header = "AstroEşleşme Yönetim Paneli"
admin.site.site_title = "AstroEşleşme Admin"
admin.site.index_title = "AstroEşleşme Yönetim Portalı"