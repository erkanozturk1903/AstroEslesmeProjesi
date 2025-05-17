from django.db import models
from django.contrib.auth.models import User

class NumberMeaning(models.Model):
    """Sayıların anlamları için model"""
    number = models.IntegerField(unique=True, verbose_name="Sayı")
    name = models.CharField(max_length=100, blank=True, verbose_name="Sayı Adı")
    keywords = models.CharField(max_length=255, blank=True, verbose_name="Anahtar Kelimeler")
    general_meaning = models.TextField(blank=True, verbose_name="Genel Anlam")
    positive_aspects = models.TextField(blank=True, verbose_name="Olumlu Yönleri")
    negative_aspects = models.TextField(blank=True, verbose_name="Olumsuz Yönleri")
    life_path_meaning = models.TextField(blank=True, verbose_name="Yaşam Yolu Sayısı Anlamı")
    destiny_meaning = models.TextField(blank=True, verbose_name="Kader Sayısı Anlamı")
    personality_meaning = models.TextField(blank=True, verbose_name="Kişilik Sayısı Anlamı")
    
    def __str__(self):
        return f"{self.number} - {self.name}"
    
    class Meta:
        verbose_name = "Sayı Anlamı"
        verbose_name_plural = "Sayı Anlamları"
        ordering = ['number']

class NumerologyProfile(models.Model):
    """Kullanıcı numeroloji profili"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='numerology_profile', verbose_name="Kullanıcı")
    birth_name = models.CharField(max_length=255, verbose_name="Doğum Adı")
    birth_date = models.DateField(verbose_name="Doğum Tarihi")
    life_path_number = models.IntegerField(null=True, blank=True, verbose_name="Yaşam Yolu Sayısı")
    destiny_number = models.IntegerField(null=True, blank=True, verbose_name="Kader Sayısı")
    soul_urge_number = models.IntegerField(null=True, blank=True, verbose_name="Ruh İstek Sayısı")
    personality_number = models.IntegerField(null=True, blank=True, verbose_name="Kişilik Sayısı")
    birth_day_number = models.IntegerField(null=True, blank=True, verbose_name="Doğum Günü Sayısı")
    expression_number = models.IntegerField(null=True, blank=True, verbose_name="İfade Sayısı")
    maturity_number = models.IntegerField(null=True, blank=True, verbose_name="Olgunluk Sayısı")
    balance_number = models.IntegerField(null=True, blank=True, verbose_name="Denge Sayısı")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")
    
    def __str__(self):
        return f"Numeroloji Profili - {self.user.username}"
    
    class Meta:
        verbose_name = "Numeroloji Profili"
        verbose_name_plural = "Numeroloji Profilleri"

class LifePathNumber(models.Model):
    """Yaşam Yolu Sayısı detaylı yorumları"""
    number = models.IntegerField(unique=True, verbose_name="Yaşam Yolu Sayısı")
    description = models.TextField(verbose_name="Açıklama")
    strengths = models.TextField(blank=True, verbose_name="Güçlü Yönler")
    challenges = models.TextField(blank=True, verbose_name="Zorluklar")
    career_suggestions = models.TextField(blank=True, verbose_name="Kariyer Önerileri")
    relationship_guidance = models.TextField(blank=True, verbose_name="İlişki Rehberliği")
    health_insights = models.TextField(blank=True, verbose_name="Sağlık İçgörüleri")
    life_purpose = models.TextField(blank=True, verbose_name="Yaşam Amacı")
    
    def __str__(self):
        return f"Yaşam Yolu Sayısı {self.number}"
    
    class Meta:
        verbose_name = "Yaşam Yolu Sayısı"
        verbose_name_plural = "Yaşam Yolu Sayıları"

class DestinyNumber(models.Model):
    """Kader Sayısı detaylı yorumları"""
    number = models.IntegerField(unique=True, verbose_name="Kader Sayısı")
    description = models.TextField(verbose_name="Açıklama")
    talents = models.TextField(blank=True, verbose_name="Yetenekler")
    life_lessons = models.TextField(blank=True, verbose_name="Yaşam Dersleri")
    career_path = models.TextField(blank=True, verbose_name="Kariyer Yolu")
    relationship_compatibility = models.TextField(blank=True, verbose_name="İlişki Uyumluluğu")
    spiritual_growth = models.TextField(blank=True, verbose_name="Ruhsal Gelişim")
    
    def __str__(self):
        return f"Kader Sayısı {self.number}"
    
    class Meta:
        verbose_name = "Kader Sayısı"
        verbose_name_plural = "Kader Sayıları"

class PersonalYearNumber(models.Model):
    """Kişisel Yıl Sayısı yorumları"""
    number = models.IntegerField(unique=True, verbose_name="Kişisel Yıl Sayısı")
    description = models.TextField(verbose_name="Açıklama")
    opportunities = models.TextField(blank=True, verbose_name="Fırsatlar")
    challenges = models.TextField(blank=True, verbose_name="Zorluklar")
    focus_areas = models.TextField(blank=True, verbose_name="Odaklanılması Gereken Alanlar")
    advice = models.TextField(blank=True, verbose_name="Tavsiyeler")
    
    def __str__(self):
        return f"Kişisel Yıl Sayısı {self.number}"
    
    class Meta:
        verbose_name = "Kişisel Yıl Sayısı"
        verbose_name_plural = "Kişisel Yıl Sayıları"

class PersonalMonthNumber(models.Model):
    """Kişisel Ay Sayısı yorumları"""
    personal_year = models.ForeignKey(PersonalYearNumber, on_delete=models.CASCADE, related_name='month_interpretations', verbose_name="Kişisel Yıl")
    month_number = models.IntegerField(verbose_name="Ay Numarası", choices=[(i, i) for i in range(1, 13)])
    description = models.TextField(verbose_name="Açıklama")
    focus_areas = models.TextField(blank=True, verbose_name="Odaklanılması Gereken Alanlar")
    opportunities = models.TextField(blank=True, verbose_name="Fırsatlar")
    challenges = models.TextField(blank=True, verbose_name="Zorluklar")
    
    def __str__(self):
        return f"Kişisel Yıl {self.personal_year.number}, Ay {self.month_number}"
    
    class Meta:
        verbose_name = "Kişisel Ay Sayısı"
        verbose_name_plural = "Kişisel Ay Sayıları"
        unique_together = ('personal_year', 'month_number')

class NameAnalysis(models.Model):
    """İsim analizi sonuçları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='name_analyses', verbose_name="Kullanıcı")
    name = models.CharField(max_length=255, verbose_name="Analiz Edilen İsim")
    expression_number = models.IntegerField(verbose_name="İfade Sayısı")
    soul_urge_number = models.IntegerField(verbose_name="Ruh İstek Sayısı")
    personality_number = models.IntegerField(verbose_name="Kişilik Sayısı")
    analysis_text = models.TextField(blank=True, verbose_name="Analiz Metni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    def __str__(self):
        return f"İsim Analizi: {self.name} - {self.user.username}"
    
    class Meta:
        verbose_name = "İsim Analizi"
        verbose_name_plural = "İsim Analizleri"

class NumerologyChartReading(models.Model):
    """Kapsamlı numeroloji okuma sonuçları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='numerology_readings', verbose_name="Kullanıcı")
    name = models.CharField(max_length=100, verbose_name="Okuma Adı")
    birth_name = models.CharField(max_length=255, verbose_name="Doğum Adı")
    current_name = models.CharField(max_length=255, verbose_name="Şu Anki Adı")
    birth_date = models.DateField(verbose_name="Doğum Tarihi")
    reading_date = models.DateField(verbose_name="Okuma Tarihi")
    life_path_number = models.IntegerField(verbose_name="Yaşam Yolu Sayısı")
    destiny_number = models.IntegerField(verbose_name="Kader Sayısı")
    soul_urge_number = models.IntegerField(verbose_name="Ruh İstek Sayısı")
    personality_number = models.IntegerField(verbose_name="Kişilik Sayısı")
    birth_day_number = models.IntegerField(verbose_name="Doğum Günü Sayısı")
    personal_year_number = models.IntegerField(verbose_name="Kişisel Yıl Sayısı")
    chart_data = models.JSONField(null=True, blank=True, verbose_name="Grafik Verileri")
    notes = models.TextField(blank=True, verbose_name="Notlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    class Meta:
        verbose_name = "Numeroloji Haritası Okuması"
        verbose_name_plural = "Numeroloji Haritası Okumaları"

class NumberCompatibility(models.Model):
    """İki sayı arasındaki uyumluluk yorumları"""
    number1 = models.IntegerField(verbose_name="1. Sayı")
    number2 = models.IntegerField(verbose_name="2. Sayı")
    compatibility_score = models.IntegerField(verbose_name="Uyumluluk Puanı", choices=[(i, i) for i in range(1, 11)])
    general_compatibility = models.TextField(verbose_name="Genel Uyumluluk")
    relationship_guidance = models.TextField(blank=True, verbose_name="İlişki Rehberliği")
    strengths = models.TextField(blank=True, verbose_name="Güçlü Yönler")
    challenges = models.TextField(blank=True, verbose_name="Zorluklar")
    advice = models.TextField(blank=True, verbose_name="Tavsiyeler")
    
    def __str__(self):
        return f"Sayı Uyumluluğu: {self.number1} ve {self.number2}"
    
    class Meta:
        verbose_name = "Sayı Uyumluluğu"
        verbose_name_plural = "Sayı Uyumlulukları"
        unique_together = (('number1', 'number2'),)