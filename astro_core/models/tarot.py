from django.db import models
from django.contrib.auth.models import User

class TarotDeck(models.Model):
    """Tarot deste modeli"""
    name = models.CharField(max_length=100, verbose_name="Deste Adı")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    creator = models.CharField(max_length=100, blank=True, verbose_name="Yaratıcı")
    year_created = models.IntegerField(null=True, blank=True, verbose_name="Yaratılış Yılı")
    image = models.ImageField(upload_to='tarot_decks/', null=True, blank=True, verbose_name="Deste Görseli")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Tarot Destesi"
        verbose_name_plural = "Tarot Desteleri"

class TarotCard(models.Model):
    """Tarot kartları için model"""
    CARD_TYPES = [
        ('major', 'Büyük Arkana'),
        ('wands', 'Değnekler'),
        ('cups', 'Kupalar'),
        ('swords', 'Kılıçlar'),
        ('pentacles', 'Pentakller'),
    ]
    
    deck = models.ForeignKey(TarotDeck, on_delete=models.CASCADE, related_name='cards', verbose_name="Deste")
    name = models.CharField(max_length=100, verbose_name="Kart Adı")
    card_type = models.CharField(max_length=20, choices=CARD_TYPES, verbose_name="Kart Tipi")
    number = models.IntegerField(null=True, blank=True, verbose_name="Numara")
    keywords = models.CharField(max_length=255, blank=True, verbose_name="Anahtar Kelimeler")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    upright_meaning = models.TextField(blank=True, verbose_name="Dik Anlamı")
    reversed_meaning = models.TextField(blank=True, verbose_name="Ters Anlamı")
    image = models.ImageField(upload_to='tarot_cards/', null=True, blank=True, verbose_name="Görsel")
    astrological_correspondence = models.CharField(max_length=100, blank=True, verbose_name="Astrolojik Karşılık")
    element = models.CharField(max_length=50, blank=True, verbose_name="Element")
    numerological_correspondence = models.CharField(max_length=50, blank=True, verbose_name="Numerolojik Karşılık")
    
    class Meta:
        verbose_name = "Tarot Kartı"
        verbose_name_plural = "Tarot Kartları"
        unique_together = ('deck', 'name')
        ordering = ['card_type', 'number']
        
    def __str__(self):
        return f"{self.name} ({self.get_card_type_display()}) - {self.deck.name}"

class TarotSpread(models.Model):
    """Tarot açılım şablonları için model"""
    name = models.CharField(max_length=100, verbose_name="Açılım Adı")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    num_cards = models.IntegerField(verbose_name="Kart Sayısı")
    image = models.ImageField(upload_to='tarot_spreads/', null=True, blank=True, verbose_name="Açılım Görseli")
    
    def __str__(self):
        return f"{self.name} ({self.num_cards} kart)"
    
    class Meta:
        verbose_name = "Tarot Açılımı"
        verbose_name_plural = "Tarot Açılımları"

class TarotCardPosition(models.Model):
    """Tarot açılımındaki kart pozisyonları için model"""
    spread = models.ForeignKey(TarotSpread, on_delete=models.CASCADE, related_name='positions', verbose_name="Açılım")
    position_number = models.IntegerField(verbose_name="Pozisyon Numarası")
    name = models.CharField(max_length=100, verbose_name="Pozisyon Adı")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    x_position = models.IntegerField(default=0, verbose_name="X Koordinatı")
    y_position = models.IntegerField(default=0, verbose_name="Y Koordinatı")
    
    def __str__(self):
        return f"{self.spread.name} - {self.position_number}. {self.name}"
    
    class Meta:
        verbose_name = "Tarot Kart Pozisyonu"
        verbose_name_plural = "Tarot Kart Pozisyonları"
        unique_together = ('spread', 'position_number')
        ordering = ['spread', 'position_number']

class TarotReading(models.Model):
    """Kullanıcının tarot okumaları için model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tarot_readings', verbose_name="Kullanıcı")
    deck = models.ForeignKey(TarotDeck, on_delete=models.CASCADE, related_name='readings', verbose_name="Deste")
    spread = models.ForeignKey(TarotSpread, on_delete=models.CASCADE, related_name='readings', verbose_name="Açılım")
    name = models.CharField(max_length=100, verbose_name="Okuma Adı")
    question = models.TextField(blank=True, verbose_name="Soru")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    notes = models.TextField(blank=True, verbose_name="Notlar")
    
    def __str__(self):
        return f"{self.name} - {self.user.username} ({self.date_created.strftime('%d/%m/%Y')})"
    
    class Meta:
        verbose_name = "Tarot Okuması"
        verbose_name_plural = "Tarot Okumaları"

class TarotCardInReading(models.Model):
    """Bir tarot okumasındaki kartlar için model"""
    reading = models.ForeignKey(TarotReading, on_delete=models.CASCADE, related_name='cards', verbose_name="Okuma")
    position = models.ForeignKey(TarotCardPosition, on_delete=models.CASCADE, related_name='readings', verbose_name="Pozisyon")
    card = models.ForeignKey(TarotCard, on_delete=models.CASCADE, related_name='readings', verbose_name="Kart")
    is_reversed = models.BooleanField(default=False, verbose_name="Ters mi?")
    notes = models.TextField(blank=True, verbose_name="Notlar")
    
    def __str__(self):
        return f"{self.reading.name} - {self.position.name}: {self.card.name} {'(Ters)' if self.is_reversed else ''}"
    
    class Meta:
        verbose_name = "Okumadaki Tarot Kartı"
        verbose_name_plural = "Okumadaki Tarot Kartları"
        unique_together = ('reading', 'position')