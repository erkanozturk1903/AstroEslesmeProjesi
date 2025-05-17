from rest_framework import serializers

class TransitSerializer(serializers.Serializer):
    """Transit hesaplamaları için kullanılacak serializer"""
    chart_id = serializers.IntegerField()
    transit_date = serializers.DateField(default=None, required=False)  # Belirtilmezse bugün
    transit_time = serializers.TimeField(default=None, required=False)  # Belirtilmezse şu an

class ProgressionSerializer(serializers.Serializer):
    """İlerlemeler için kullanılacak serializer"""
    chart_id = serializers.IntegerField()
    progression_date = serializers.DateField(default=None, required=False)  # Belirtilmezse bugün

class SolarReturnSerializer(serializers.Serializer):
    """Güneş dönüşü için kullanılacak serializer"""
    chart_id = serializers.IntegerField()
    year = serializers.IntegerField(default=None, required=False)  # Belirtilmezse şu anki yıl