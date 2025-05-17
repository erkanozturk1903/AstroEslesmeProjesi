from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from api.views import BirthChartViewSet, TransitViewSet, CompatibilityViewSet

# Router oluştur ve viewset'leri ekle
router = DefaultRouter()
router.register(r'birth-charts', BirthChartViewSet, basename='birth-chart')
router.register(r'transits', TransitViewSet, basename='transit')
router.register(r'compatibility', CompatibilityViewSet, basename='compatibility')

# Temel URL paternleri
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('token-auth/', obtain_auth_token, name='token_auth'),
]