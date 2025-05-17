from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from astro_core.models import BirthChart
from astro_core.services.birth_chart import BirthChartService
from api.serializers import TransitSerializer, ProgressionSerializer, SolarReturnSerializer

class TransitViewSet(viewsets.ViewSet):
    """Transit ve diğer astrolojik hesaplamalar için ViewSet"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.birth_chart_service = BirthChartService()
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Belirtilen tarih için transit hesaplar"""
        serializer = TransitSerializer(data=request.data)
        
        if serializer.is_valid():
            # Geçerli verileri al
            data = serializer.validated_data
            chart_id = data['chart_id']
            
            # Transit tarih/saat belirtilmemişse şu anki zamanı kullan
            transit_date = data.get('transit_date') or datetime.now().date()
            transit_time = data.get('transit_time') or datetime.now().time()
            
            try:
                # Doğum haritasının kullanıcının olduğundan emin ol
                birth_chart = BirthChart.objects.get(id=chart_id, user=request.user)
                
                # Transit hesapla
                transit_data = self.birth_chart_service.calculate_transits(
                    birth_chart_id=chart_id,
                    transit_date=transit_date,
                    transit_time=transit_time
                )
                
                return Response(transit_data)
            except BirthChart.DoesNotExist:
                return Response(
                    {"error": "Doğum haritası bulunamadı veya erişim izniniz yok."},
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
    
    @action(detail=False, methods=['post'])
    def progressions(self, request):
        """İlerlemeleri hesaplar"""
        serializer = ProgressionSerializer(data=request.data)
        
        if serializer.is_valid():
            # Geçerli verileri al
            data = serializer.validated_data
            chart_id = data['chart_id']
            
            # İlerleme tarihi belirtilmemişse şu anki zamanı kullan
            progression_date = data.get('progression_date') or datetime.now().date()
            
            try:
                # Doğum haritasının kullanıcının olduğundan emin ol
                birth_chart = BirthChart.objects.get(id=chart_id, user=request.user)
                
                # İlerlemeleri hesapla
                progression_data = self.birth_chart_service.calculate_secondary_progressions(
                    birth_chart_id=chart_id,
                    target_date=progression_date
                )
                
                return Response(progression_data)
            except BirthChart.DoesNotExist:
                return Response(
                    {"error": "Doğum haritası bulunamadı veya erişim izniniz yok."},
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
    
    @action(detail=False, methods=['post'])
    def solar_return(self, request):
        """Güneş dönüşünü hesaplar"""
        serializer = SolarReturnSerializer(data=request.data)
        
        if serializer.is_valid():
            # Geçerli verileri al
            data = serializer.validated_data
            chart_id = data['chart_id']
            
            # Yıl belirtilmemişse şu anki yılı kullan
            year = data.get('year') or datetime.now().year
            
            try:
                # Doğum haritasının kullanıcının olduğundan emin ol
                birth_chart = BirthChart.objects.get(id=chart_id, user=request.user)
                
                # Güneş dönüşünü hesapla
                solar_return_data = self.birth_chart_service.calculate_solar_return(
                    birth_chart_id=chart_id,
                    year=year
                )
                
                return Response(solar_return_data)
            except BirthChart.DoesNotExist:
                return Response(
                    {"error": "Doğum haritası bulunamadı veya erişim izniniz yok."},
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