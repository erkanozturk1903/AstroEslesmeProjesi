from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from astro_core.models import BirthChart
from astro_core.services.birth_chart import BirthChartService
from api.serializers import BirthChartCreateSerializer, BirthChartSerializer

class BirthChartViewSet(viewsets.ModelViewSet):
    """Doğum haritası işlemleri için ViewSet"""
    serializer_class = BirthChartSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.birth_chart_service = BirthChartService()
    
    def get_queryset(self):
        """Sadece kullanıcının kendi doğum haritalarını görmesini sağlar"""
        return BirthChart.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_chart(self, request):
        """Yeni bir doğum haritası oluşturur"""
        serializer = BirthChartCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Geçerli verileri al
            data = serializer.validated_data
            
            try:
                # Doğum haritası oluştur
                birth_chart = self.birth_chart_service.generate_birth_chart(
                    user=request.user,
                    name=data['name'],
                    birth_date=data['birth_date'],
                    birth_time=data['birth_time'],
                    latitude=data['birth_latitude'],
                    longitude=data['birth_longitude'],
                    birth_place=data['birth_place'],
                    system_id=data.get('system_id', 1)
                )
                
                # Oluşturulan haritayı döndür
                return Response(
                    BirthChartSerializer(birth_chart).data,
                    status=status.HTTP_201_CREATED
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