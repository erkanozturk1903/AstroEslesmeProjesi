from rest_framework import serializers

class CompatibilitySerializer(serializers.Serializer):
    """İki doğum haritası arasındaki uyumluluğu hesaplamak için kullanılacak serializer"""
    chart1_id = serializers.IntegerField()
    chart2_id = serializers.IntegerField()