from django.db import models
from django.contrib.auth.models import User
from .astrology import AstrologicalSystem, Sign, Planet, Aspect, BirthChart

class SignCompatibility(models.Model):
    """Burçlar arası uyumluluk için model"""
    system = models.ForeignKey(AstrologicalSystem, on_delete=models.CASCADE, related_name='sign_compatibilities', verbose_name="Astrolojik Sistem")
    sign1 = models.ForeignKey(Sign, on_delete=models.CASCADE, related_name='compatibility_as_first', verbose_name="1. Burç")
    sign2 = models.ForeignKey(Sign, on_delete=models.CASCADE, related_name='compatibility_as_second', verbose_name="2. Burç")
    compatibility_score = models.IntegerField(verbose_name="Uyumluluk Puanı", choices=[(i, i) for i in range(1, 11)])
    overall_compatibility = models.TextField(verbose_name="Genel Uyumluluk")
    romantic_compatibility = models.TextField(blank=True, verbose_name="Romantik Uyumluluk")
    friendship_compatibility = models.TextField(blank=True, verbose_name="Arkadaşlık Uyumluluğu")
    communication = models.TextField(blank=True, verbose_name="İletişim")
    emotional_compatibility = models.TextField(blank=True, verbose_name="Duygusal Uyumluluk")
    values_compatibility = models.TextField(blank=True, verbose_name="Değerler Uyumluluğu")
    sexual_compatibility = models.TextField(blank=True, verbose_name="Cinsel Uyumluluk")
    long_term_potential = models.TextField(blank=True, verbose_name="Uzun Vadeli Potansiyel")
    challenges = models.TextField(blank=True, verbose_name="Zorluklar")
    advice = models.TextField(blank=True, verbose_name="Tavsiyeler")
    
    class Meta:
        unique_together = ('system', 'sign1', 'sign2')
        verbose_name = "Burç Uyumluluğu"
        verbose_name_plural = "Burç Uyumlulukları"
        
    def __str__(self):
        return f"{self.sign1.name} & {self.sign2.name} ({self.system.name})"

class RelationshipAspect(models.Model):
    """İki doğum haritası arasındaki açıları yorumlama"""
    system = models.ForeignKey(AstrologicalSystem, on_delete=models.CASCADE, related_name='relationship_aspects', verbose_name="Astrolojik Sistem")
    planet1 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='synastry_aspects_as_first', verbose_name="1. Gezegen")
    planet2 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='synastry_aspects_as_second', verbose_name="2. Gezegen")
    aspect = models.ForeignKey(Aspect, on_delete=models.CASCADE, related_name='synastry_interpretations', verbose_name="Açı")
    interpretation = models.TextField(verbose_name="Yorum")
    positive_influence = models.TextField(blank=True, verbose_name="Olumlu Etkiler")
    negative_influence = models.TextField(blank=True, verbose_name="Olumsuz Etkiler")
    romantic_impact = models.TextField(blank=True, verbose_name="Romantik Etki")
    communication_impact = models.TextField(blank=True, verbose_name="İletişim Etkisi")
    advice = models.TextField(blank=True, verbose_name="Tavsiyeler")
    
    class Meta:
        unique_together = ('system', 'planet1', 'planet2', 'aspect')
        verbose_name = "İlişki Açısı"
        verbose_name_plural = "İlişki Açıları"
        
    def __str__(self):
        return f"{self.planet1.name} {self.aspect.name} {self.planet2.name} (Sinastrİ)"

class CompatibilityScore(models.Model):
    """İki doğum haritası arasındaki genel uyumluluk puanı"""
    chart1 = models.ForeignKey(BirthChart, on_delete=models.CASCADE, related_name='compatibility_as_first', verbose_name="1. Harita")
    chart2 = models.ForeignKey(BirthChart, on_delete=models.CASCADE, related_name='compatibility_as_second', verbose_name="2. Harita")
    overall_score = models.IntegerField(verbose_name="Genel Uyumluluk Puanı", choices=[(i, i) for i in range(1, 101)])
    emotional_score = models.IntegerField(null=True, blank=True, verbose_name="Duygusal Uyumluluk", choices=[(i, i) for i in range(1, 101)])
    communication_score = models.IntegerField(null=True, blank=True, verbose_name="İletişim Uyumluluğu", choices=[(i, i) for i in range(1, 101)])
    romantic_score = models.IntegerField(null=True, blank=True, verbose_name="Romantik Uyumluluk", choices=[(i, i) for i in range(1, 101)])
    sexual_score = models.IntegerField(null=True, blank=True, verbose_name="Cinsel Uyumluluk", choices=[(i, i) for i in range(1, 101)])
    commitment_score = models.IntegerField(null=True, blank=True, verbose_name="Bağlılık Uyumluluğu", choices=[(i, i) for i in range(1, 101)])
    friendship_score = models.IntegerField(null=True, blank=True, verbose_name="Arkadaşlık Uyumluluğu", choices=[(i, i) for i in range(1, 101)])
    spiritual_score = models.IntegerField(null=True, blank=True, verbose_name="Ruhsal Uyumluluk", choices=[(i, i) for i in range(1, 101)])
    detailed_scores = models.JSONField(null=True, blank=True, verbose_name="Detaylı Puanlar")
    summary = models.TextField(blank=True, verbose_name="Özet")
    strengths = models.TextField(blank=True, verbose_name="Güçlü Yönler")
    challenges = models.TextField(blank=True, verbose_name="Zorluklar")
    advice = models.TextField(blank=True, verbose_name="Tavsiyeler")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    class Meta:
        unique_together = ('chart1', 'chart2')
        verbose_name = "Uyumluluk Puanı"
        verbose_name_plural = "Uyumluluk Puanları"
        
    def __str__(self):
        return f"{self.chart1.name} & {self.chart2.name} ({self.overall_score}/100)"

class ElementalCompatibility(models.Model):
    """Element uyumlulukları (Ateş, Toprak, Hava, Su)"""
    ELEMENTS = [
        ('fire', 'Ateş'),
        ('earth', 'Toprak'),
        ('air', 'Hava'),
        ('water', 'Su'),
    ]
    
    element1 = models.CharField(max_length=20, choices=ELEMENTS, verbose_name="1. Element")
    element2 = models.CharField(max_length=20, choices=ELEMENTS, verbose_name="2. Element")
    compatibility_score = models.IntegerField(verbose_name="Uyumluluk Puanı", choices=[(i, i) for i in range(1, 11)])
    description = models.TextField(verbose_name="Açıklama")
    strengths = models.TextField(blank=True, verbose_name="Güçlü Yönler")
    challenges = models.TextField(blank=True, verbose_name="Zorluklar")
    advice = models.TextField(blank=True, verbose_name="Tavsiyeler")
    
    class Meta:
        unique_together = ('element1', 'element2')
        verbose_name = "Element Uyumluluğu"
        verbose_name_plural = "Element Uyumlulukları"
        
    def __str__(self):
        return f"{self.get_element1_display()} & {self.get_element2_display()}"

class ModalityCompatibility(models.Model):
    """Nitelik uyumlulukları (Öncü, Sabit, Değişken)"""
    MODALITIES = [
        ('cardinal', 'Öncü'),
        ('fixed', 'Sabit'),
        ('mutable', 'Değişken'),
    ]
    
    modality1 = models.CharField(max_length=20, choices=MODALITIES, verbose_name="1. Nitelik")
    modality2 = models.CharField(max_length=20, choices=MODALITIES, verbose_name="2. Nitelik")
    compatibility_score = models.IntegerField(verbose_name="Uyumluluk Puanı", choices=[(i, i) for i in range(1, 11)])
    description = models.TextField(verbose_name="Açıklama")
    strengths = models.TextField(blank=True, verbose_name="Güçlü Yönler")
    challenges = models.TextField(blank=True, verbose_name="Zorluklar")
    advice = models.TextField(blank=True, verbose_name="Tavsiyeler")
    
    class Meta:
        unique_together = ('modality1', 'modality2')
        verbose_name = "Nitelik Uyumluluğu"
        verbose_name_plural = "Nitelik Uyumlulukları"
        
    def __str__(self):
        return f"{self.get_modality1_display()} & {self.get_modality2_display()}"

class CompositeBirthChart(models.Model):
    """İki kişinin ortak (composite) doğum haritası"""
    chart1 = models.ForeignKey(BirthChart, on_delete=models.CASCADE, related_name='composite_charts_as_first', verbose_name="1. Harita")
    chart2 = models.ForeignKey(BirthChart, on_delete=models.CASCADE, related_name='composite_charts_as_second', verbose_name="2. Harita")
    name = models.CharField(max_length=100, verbose_name="Harita Adı")
    chart_data = models.JSONField(null=True, blank=True, verbose_name="Harita Verileri")
    interpretation = models.TextField(blank=True, verbose_name="Genel Yorum")
    sun_sign = models.ForeignKey(Sign, null=True, blank=True, on_delete=models.SET_NULL, related_name='composite_sun_charts', verbose_name="Güneş Burcu")
    moon_sign = models.ForeignKey(Sign, null=True, blank=True, on_delete=models.SET_NULL, related_name='composite_moon_charts', verbose_name="Ay Burcu")
    ascendant_sign = models.ForeignKey(Sign, null=True, blank=True, on_delete=models.SET_NULL, related_name='composite_ascendant_charts', verbose_name="Yükselen Burç")
    notes = models.TextField(blank=True, verbose_name="Notlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    class Meta:
        unique_together = ('chart1', 'chart2')
        verbose_name = "Ortak Doğum Haritası"
        verbose_name_plural = "Ortak Doğum Haritaları"
        
    def __str__(self):
        return f"Composite: {self.chart1.name} & {self.chart2.name}"