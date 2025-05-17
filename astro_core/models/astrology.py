# astro_core/models/astrology.py

from django.db import models
from django.contrib.auth.models import User
from .mixins import TranslatableMixin

class AstrologicalSystem(TranslatableMixin, models.Model):
    """Farklı astrolojik sistemler için model (Batı, Vedik, Çin, vb.)"""
    name = models.CharField(max_length=100, verbose_name="Sistem Adı")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Astrolojik Sistem"
        verbose_name_plural = "Astrolojik Sistemler"

class AstrologicalSystemTranslation(models.Model):
    """Astrolojik sistem çevirileri için model"""
    system = models.ForeignKey(AstrologicalSystem, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=[('tr', 'Türkçe'), ('en', 'English')], verbose_name="Dil")
    
    name = models.CharField(max_length=100, verbose_name="Sistem Adı")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    
    class Meta:
        unique_together = ('system', 'language')
        verbose_name = "Astrolojik Sistem Çevirisi"
        verbose_name_plural = "Astrolojik Sistem Çevirileri"
    
    def __str__(self):
        return f"{self.name} ({self.get_language_display()})"

class Sign(TranslatableMixin, models.Model):
    """Zodyak burçları için model"""
    ELEMENT_CHOICES = [
        ('fire', 'Ateş'),
        ('earth', 'Toprak'),
        ('air', 'Hava'),
        ('water', 'Su'),
    ]
    
    MODALITY_CHOICES = [
        ('cardinal', 'Öncü'),
        ('fixed', 'Sabit'),
        ('mutable', 'Değişken'),
    ]
    
    system = models.ForeignKey(AstrologicalSystem, on_delete=models.CASCADE, related_name='signs', verbose_name="Astrolojik Sistem")
    element = models.CharField(max_length=20, choices=ELEMENT_CHOICES, blank=True, verbose_name="Element")
    modality = models.CharField(max_length=20, choices=MODALITY_CHOICES, blank=True, verbose_name="Nitelik")
    ruling_planet = models.CharField(max_length=50, blank=True, verbose_name="Yönetici Gezegen")
    start_date = models.CharField(max_length=5, verbose_name="Başlangıç Tarihi", help_text="Örnek: 21/03 (21 Mart)")
    end_date = models.CharField(max_length=5, verbose_name="Bitiş Tarihi", help_text="Örnek: 19/04 (19 Nisan)")
    image = models.ImageField(upload_to='sign_images/', null=True, blank=True, verbose_name="Görsel")
    
    def __str__(self):
        # Önce Türkçe, yoksa İngilizce çeviri dene
        translation = self.get_translation()
        if translation:
            return f"{translation.name} ({self.system.name})"
        return f"Sign #{self.id} ({self.system.name})"
    
    class Meta:
        verbose_name = "Burç"
        verbose_name_plural = "Burçlar"
        unique_together = ('system', 'element', 'modality', 'ruling_planet', 'start_date', 'end_date')

class SignTranslation(models.Model):
    """Burç çevirileri için model"""
    sign = models.ForeignKey(Sign, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=[('tr', 'Türkçe'), ('en', 'English')], verbose_name="Dil")
    
    name = models.CharField(max_length=50, verbose_name="Burç Adı")
    symbol = models.CharField(max_length=10, blank=True, verbose_name="Sembol")
    keywords = models.CharField(max_length=255, blank=True, verbose_name="Anahtar Kelimeler")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    positive_traits = models.TextField(blank=True, verbose_name="Olumlu Özellikler")
    negative_traits = models.TextField(blank=True, verbose_name="Olumsuz Özellikler")
    
    class Meta:
        unique_together = ('sign', 'language')
        verbose_name = "Burç Çevirisi"
        verbose_name_plural = "Burç Çevirileri"
    
    def __str__(self):
        return f"{self.name} ({self.get_language_display()})"

class Planet(TranslatableMixin, models.Model):
    """Gezegenler ve gökcisimleri için model"""
    system = models.ForeignKey(AstrologicalSystem, on_delete=models.CASCADE, related_name='planets', verbose_name="Astrolojik Sistem")
    rulership = models.ManyToManyField(Sign, blank=True, related_name='ruling_planets', verbose_name="Yönettiği Burçlar")
    exaltation = models.ForeignKey(Sign, null=True, blank=True, on_delete=models.SET_NULL, related_name='exalted_planets', verbose_name="Yüceldiği Burç")
    fall = models.ForeignKey(Sign, null=True, blank=True, on_delete=models.SET_NULL, related_name='fallen_planets', verbose_name="Düştüğü Burç")
    detriment = models.ManyToManyField(Sign, blank=True, related_name='detrimented_planets', verbose_name="Zayıfladığı Burçlar")
    image = models.ImageField(upload_to='planet_images/', null=True, blank=True, verbose_name="Görsel")
    
    def __str__(self):
        translation = self.get_translation()
        if translation:
            return f"{translation.name} ({self.system.name})"
        return f"Planet #{self.id} ({self.system.name})"
    
    class Meta:
        verbose_name = "Gezegen"
        verbose_name_plural = "Gezegenler"
        

class PlanetTranslation(models.Model):
    """Gezegen çevirileri için model"""
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=[('tr', 'Türkçe'), ('en', 'English')], verbose_name="Dil")
    
    name = models.CharField(max_length=50, verbose_name="Gezegen Adı")
    symbol = models.CharField(max_length=10, blank=True, verbose_name="Sembol")
    keywords = models.CharField(max_length=255, blank=True, verbose_name="Anahtar Kelimeler")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    
    class Meta:
        unique_together = ('planet', 'language')
        verbose_name = "Gezegen Çevirisi"
        verbose_name_plural = "Gezegen Çevirileri"
    
    def __str__(self):
        return f"{self.name} ({self.get_language_display()})"

class House(TranslatableMixin, models.Model):
    """Astrolojik evler için model"""
    system = models.ForeignKey(AstrologicalSystem, on_delete=models.CASCADE, related_name='houses', verbose_name="Astrolojik Sistem")
    number = models.IntegerField(verbose_name="Ev Numarası")
    natural_sign = models.ForeignKey(Sign, on_delete=models.SET_NULL, null=True, blank=True, related_name='natural_house', verbose_name="Doğal Burç")
    
    def __str__(self):
        translation = self.get_translation()
        if translation:
            return f"{self.number}. Ev - {translation.name} ({self.system.name})"
        return f"{self.number}. Ev ({self.system.name})"
    
    class Meta:
        verbose_name = "Ev"
        verbose_name_plural = "Evler"
        ordering = ['number']
        unique_together = ('system', 'number')

class HouseTranslation(models.Model):
    """Ev çevirileri için model"""
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=[('tr', 'Türkçe'), ('en', 'English')], verbose_name="Dil")
    
    name = models.CharField(max_length=100, blank=True, verbose_name="Ev Adı")
    keywords = models.CharField(max_length=255, blank=True, verbose_name="Anahtar Kelimeler")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    ruled_areas = models.TextField(blank=True, verbose_name="Yönettiği Alanlar")
    
    class Meta:
        unique_together = ('house', 'language')
        verbose_name = "Ev Çevirisi"
        verbose_name_plural = "Ev Çevirileri"
    
    def __str__(self):
        return f"{self.house.number}. Ev - {self.name} ({self.get_language_display()})"

class Aspect(TranslatableMixin, models.Model):
    """Astrolojik açılar için model"""
    system = models.ForeignKey(AstrologicalSystem, on_delete=models.CASCADE, related_name='aspects', verbose_name="Astrolojik Sistem")
    degrees = models.FloatField(verbose_name="Derece")
    orb = models.FloatField(default=5.0, verbose_name="Orb (Derece)")
    
    def __str__(self):
        translation = self.get_translation()
        if translation:
            return f"{translation.name} ({self.degrees}°)"
        return f"Aspect {self.degrees}°"
    
    class Meta:
        verbose_name = "Açı"
        verbose_name_plural = "Açılar"
        unique_together = ('system', 'degrees')

class AspectTranslation(models.Model):
    """Açı çevirileri için model"""
    aspect = models.ForeignKey(Aspect, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=[('tr', 'Türkçe'), ('en', 'English')], verbose_name="Dil")
    
    name = models.CharField(max_length=50, verbose_name="Açı Adı")
    symbol = models.CharField(max_length=10, blank=True, verbose_name="Sembol")
    keywords = models.CharField(max_length=255, blank=True, verbose_name="Anahtar Kelimeler")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    nature = models.CharField(max_length=50, blank=True, verbose_name="Doğası")  # Harmonik, Zorlayıcı, Nötr
    
    class Meta:
        unique_together = ('aspect', 'language')
        verbose_name = "Açı Çevirisi"
        verbose_name_plural = "Açı Çevirileri"
    
    def __str__(self):
        return f"{self.name} ({self.get_language_display()})"

class PlanetInSign(TranslatableMixin, models.Model):
    """Gezegenlerin burçlardaki konumlarının yorumları"""
    system = models.ForeignKey(AstrologicalSystem, on_delete=models.CASCADE, related_name='planet_sign_interpretations', verbose_name="Astrolojik Sistem")
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='sign_interpretations', verbose_name="Gezegen")
    sign = models.ForeignKey(Sign, on_delete=models.CASCADE, related_name='planet_interpretations', verbose_name="Burç")
    # Yeni alanlar
    birth_chart = models.ForeignKey('BirthChart', null=True, blank=True, on_delete=models.CASCADE, related_name='planet_signs', verbose_name="Doğum Haritası")
    degree = models.FloatField(null=True, blank=True, verbose_name="Burç Derecesi")
    is_retrograde = models.BooleanField(default=False, verbose_name="Retrograd mı?")
    chart_position = models.CharField(max_length=50, null=True, blank=True, default='natal', verbose_name="Harita Konumu")
    
    def __str__(self):
        planet_trans = self.planet.get_translation()
        sign_trans = self.sign.get_translation()
        if planet_trans and sign_trans:
            return f"{planet_trans.name} in {sign_trans.name} ({self.system.name})"
        return f"Planet {self.planet.id} in Sign {self.sign.id} ({self.system.name})"
    
    class Meta:
        unique_together = ('system', 'planet', 'sign', 'birth_chart')
        verbose_name = "Gezegen Burç Yorumu"
        verbose_name_plural = "Gezegen Burç Yorumları"

class PlanetInSignTranslation(models.Model):
    """Gezegen burç yorumu çevirileri için model"""
    planet_in_sign = models.ForeignKey(PlanetInSign, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=[('tr', 'Türkçe'), ('en', 'English')], verbose_name="Dil")
    
    general_interpretation = models.TextField(verbose_name="Genel Yorum")
    personality_traits = models.TextField(blank=True, verbose_name="Kişilik Özellikleri")
    challenges = models.TextField(blank=True, verbose_name="Zorluklar")
    opportunities = models.TextField(blank=True, verbose_name="Fırsatlar")
    relationship_impact = models.TextField(blank=True, verbose_name="İlişkilere Etkisi")
    career_impact = models.TextField(blank=True, verbose_name="Kariyere Etkisi")
    advice = models.TextField(blank=True, verbose_name="Tavsiyeler")
    
    class Meta:
        unique_together = ('planet_in_sign', 'language')
        verbose_name = "Gezegen Burç Yorumu Çevirisi"
        verbose_name_plural = "Gezegen Burç Yorumu Çevirileri"
    
    def __str__(self):
        planet_name = self.planet_in_sign.planet.get_translation(self.language)
        sign_name = self.planet_in_sign.sign.get_translation(self.language)
        planet_name_str = planet_name.name if planet_name else f"Planet {self.planet_in_sign.planet.id}"
        sign_name_str = sign_name.name if sign_name else f"Sign {self.planet_in_sign.sign.id}"
        return f"{planet_name_str} in {sign_name_str} ({self.get_language_display()})"

class PlanetInHouse(TranslatableMixin, models.Model):
    """Gezegenlerin evlerdeki konumlarının yorumları"""
    system = models.ForeignKey(AstrologicalSystem, on_delete=models.CASCADE, related_name='planet_house_interpretations', verbose_name="Astrolojik Sistem")
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='house_interpretations', verbose_name="Gezegen")
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='planet_interpretations', verbose_name="Ev")
    # Yeni alanlar
    birth_chart = models.ForeignKey('BirthChart', null=True, blank=True, on_delete=models.CASCADE, related_name='planet_houses', verbose_name="Doğum Haritası")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Ekliptik Boylam")
    chart_position = models.CharField(max_length=50, null=True, blank=True, default='natal', verbose_name="Harita Konumu")
    
    def __str__(self):
        planet_trans = self.planet.get_translation()
        if planet_trans:
            return f"{planet_trans.name} in {self.house.number}. Ev ({self.system.name})"
        return f"Planet {self.planet.id} in {self.house.number}. Ev ({self.system.name})"
    
    class Meta:
        unique_together = ('system', 'planet', 'house', 'birth_chart')
        verbose_name = "Gezegen Ev Yorumu"
        verbose_name_plural = "Gezegen Ev Yorumları"

class PlanetInHouseTranslation(models.Model):
    """Gezegen ev yorumu çevirileri için model"""
    planet_in_house = models.ForeignKey(PlanetInHouse, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=[('tr', 'Türkçe'), ('en', 'English')], verbose_name="Dil")
    
    general_interpretation = models.TextField(verbose_name="Genel Yorum")
    life_areas_affected = models.TextField(blank=True, verbose_name="Etkilenen Yaşam Alanları")
    challenges = models.TextField(blank=True, verbose_name="Zorluklar")
    opportunities = models.TextField(blank=True, verbose_name="Fırsatlar")
    advice = models.TextField(blank=True, verbose_name="Tavsiyeler")
    
    class Meta:
        unique_together = ('planet_in_house', 'language')
        verbose_name = "Gezegen Ev Yorumu Çevirisi"
        verbose_name_plural = "Gezegen Ev Yorumu Çevirileri"
    
    def __str__(self):
        planet_name = self.planet_in_house.planet.get_translation(self.language)
        planet_name_str = planet_name.name if planet_name else f"Planet {self.planet_in_house.planet.id}"
        return f"{planet_name_str} in {self.planet_in_house.house.number}. Ev ({self.get_language_display()})"

class PlanetAspect(TranslatableMixin, models.Model):
    """Gezegenler arası açıların yorumları"""
    system = models.ForeignKey(AstrologicalSystem, on_delete=models.CASCADE, related_name='planet_aspect_interpretations', verbose_name="Astrolojik Sistem")
    planet1 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='aspects_as_first', verbose_name="1. Gezegen")
    planet2 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='aspects_as_second', verbose_name="2. Gezegen")
    aspect = models.ForeignKey(Aspect, on_delete=models.CASCADE, related_name='planet_interpretations', verbose_name="Açı")
    # Yeni alanlar
    birth_chart = models.ForeignKey('BirthChart', null=True, blank=True, on_delete=models.CASCADE, related_name='aspects', verbose_name="Doğum Haritası")
    orb = models.FloatField(null=True, blank=True, verbose_name="Orb Değeri")
    is_applying = models.BooleanField(default=False, verbose_name="Yaklaşıyor mu?")
    is_exact = models.BooleanField(default=False, verbose_name="Tam mı?")
    is_separating = models.BooleanField(default=False, verbose_name="Uzaklaşıyor mu?")
    chart_position = models.CharField(max_length=50, null=True, blank=True, default='natal', verbose_name="Harita Konumu")
    
    def __str__(self):
        planet1_trans = self.planet1.get_translation()
        planet2_trans = self.planet2.get_translation()
        aspect_trans = self.aspect.get_translation()
        
        planet1_name = planet1_trans.name if planet1_trans else f"Planet {self.planet1.id}"
        planet2_name = planet2_trans.name if planet2_trans else f"Planet {self.planet2.id}"
        aspect_name = aspect_trans.name if aspect_trans else f"Aspect {self.aspect.degrees}°"
        
        return f"{planet1_name} {aspect_name} {planet2_name} ({self.system.name})"
    
    class Meta:
        unique_together = ('system', 'planet1', 'planet2', 'aspect', 'birth_chart')
        verbose_name = "Gezegen Açı Yorumu"
        verbose_name_plural = "Gezegen Açı Yorumları"

class PlanetAspectTranslation(models.Model):
    """Gezegen açı yorumu çevirileri için model"""
    planet_aspect = models.ForeignKey(PlanetAspect, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=[('tr', 'Türkçe'), ('en', 'English')], verbose_name="Dil")
    
    general_interpretation = models.TextField(verbose_name="Genel Yorum")
    personality_traits = models.TextField(blank=True, verbose_name="Kişilik Özellikleri")
    challenges = models.TextField(blank=True, verbose_name="Zorluklar")
    opportunities = models.TextField(blank=True, verbose_name="Fırsatlar")
    relationship_impact = models.TextField(blank=True, verbose_name="İlişkilere Etkisi")
    advice = models.TextField(blank=True, verbose_name="Tavsiyeler")
    
    class Meta:
        unique_together = ('planet_aspect', 'language')
        verbose_name = "Gezegen Açı Yorumu Çevirisi"
        verbose_name_plural = "Gezegen Açı Yorumu Çevirileri"
    
    def __str__(self):
        planet1_name = self.planet_aspect.planet1.get_translation(self.language)
        planet2_name = self.planet_aspect.planet2.get_translation(self.language)
        aspect_name = self.planet_aspect.aspect.get_translation(self.language)
        
        planet1_str = planet1_name.name if planet1_name else f"Planet {self.planet_aspect.planet1.id}"
        planet2_str = planet2_name.name if planet2_name else f"Planet {self.planet_aspect.planet2.id}"
        aspect_str = aspect_name.name if aspect_name else f"Aspect {self.planet_aspect.aspect.degrees}°"
        
        return f"{planet1_str} {aspect_str} {planet2_str} ({self.get_language_display()})"

class BirthChart(TranslatableMixin, models.Model):
    """Kullanıcıların kaydedilen doğum haritaları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='birth_charts', verbose_name="Kullanıcı")
    name = models.CharField(max_length=100, verbose_name="Harita Adı")
    system = models.ForeignKey(AstrologicalSystem, on_delete=models.CASCADE, related_name='birth_charts', verbose_name="Astrolojik Sistem")
    birth_date = models.DateField(verbose_name="Doğum Tarihi")
    birth_time = models.TimeField(null=True, blank=True, verbose_name="Doğum Saati")
    is_birth_time_known = models.BooleanField(default=True, verbose_name="Doğum Saati Biliniyor")
    birth_latitude = models.FloatField(verbose_name="Enlem")
    birth_longitude = models.FloatField(verbose_name="Boylam")
    birth_place = models.CharField(max_length=255, verbose_name="Doğum Yeri")
    notes = models.TextField(blank=True, verbose_name="Notlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")
    house_system = models.CharField(max_length=50, default='placidus', verbose_name="Ev Sistemi")
    
    # Önbelleğe alınan harita bilgileri
    ascendant_sign = models.ForeignKey(Sign, null=True, blank=True, on_delete=models.SET_NULL, related_name='ascendant_charts', verbose_name="Yükselen Burç")
    mc_sign = models.ForeignKey(Sign, null=True, blank=True, on_delete=models.SET_NULL, related_name='mc_charts', verbose_name="MC Burcu")
    chart_data = models.JSONField(null=True, blank=True, verbose_name="Harita Verileri")
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    class Meta:
        verbose_name = "Doğum Haritası"
        verbose_name_plural = "Doğum Haritaları"

class BirthChartTranslation(models.Model):
    """Doğum haritası çevirileri için model"""
    birth_chart = models.ForeignKey(BirthChart, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=[('tr', 'Türkçe'), ('en', 'English')], verbose_name="Dil")
    
    name = models.CharField(max_length=100, verbose_name="Harita Adı")
    birth_place = models.CharField(max_length=255, verbose_name="Doğum Yeri")
    notes = models.TextField(blank=True, verbose_name="Notlar")
    
    class Meta:
        unique_together = ('birth_chart', 'language')
        verbose_name = "Doğum Haritası Çevirisi"
        verbose_name_plural = "Doğum Haritası Çevirileri"
    
    def __str__(self):
        return f"{self.name} - {self.birth_chart.user.username} ({self.get_language_display()})"