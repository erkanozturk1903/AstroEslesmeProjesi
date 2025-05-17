from rest_framework import serializers
from astro_core.models import BirthChart

class BirthChartCreateSerializer(serializers.Serializer):
    """Yeni doğum haritası oluşturmak için kullanılacak serializer"""
    name = serializers.CharField(max_length=255)
    birth_date = serializers.DateField()
    birth_time = serializers.TimeField()
    birth_latitude = serializers.FloatField()
    birth_longitude = serializers.FloatField()
    birth_place = serializers.CharField(max_length=255)
    system_id = serializers.IntegerField(default=1)  # Varsayılan olarak Batı Astrolojisi

class BirthChartSerializer(serializers.ModelSerializer):
    """Doğum haritasını görüntülemek için kullanılacak serializer"""
    class Meta:
        model = BirthChart
        fields = ['id', 'name', 'birth_date', 'birth_time', 'birth_latitude', 
                  'birth_longitude', 'birth_place', 'ascendant_sign', 'chart_data']
        read_only_fields = fields