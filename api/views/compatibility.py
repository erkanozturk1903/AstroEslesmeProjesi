from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from astro_core.models import BirthChart
from astro_core.services.birth_chart import BirthChartService
from api.serializers import CompatibilitySerializer

class CompatibilityViewSet(viewsets.ViewSet):
    """İki doğum haritası arasındaki uyumluluğu hesaplamak için ViewSet"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.birth_chart_service = BirthChartService()
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """İki doğum haritası arasındaki uyumluluğu analiz eder"""
        serializer = CompatibilitySerializer(data=request.data)
        
        if serializer.is_valid():
            # Geçerli verileri al
            data = serializer.validated_data
            chart1_id = data['chart1_id']
            chart2_id = data['chart2_id']
            
            try:
                # Doğum haritalarının kullanıcının olduğundan emin ol
                chart1 = BirthChart.objects.get(id=chart1_id, user=request.user)
                chart2 = BirthChart.objects.get(id=chart2_id, user=request.user)
                
                # Uyumluluğu hesapla
                compatibility_data = self.birth_chart_service.calculate_compatibility(
                    chart1_id=chart1_id,
                    chart2_id=chart2_id
                )
                
                return Response(compatibility_data)
            except BirthChart.DoesNotExist:
                return Response(
                    {"error": "Bir veya her iki doğum haritası bulunamadı veya erişim izniniz yok."},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )