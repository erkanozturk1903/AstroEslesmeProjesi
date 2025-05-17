from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Kullanıcı profili modeli"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Kullanıcı")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Doğum Tarihi")
    birth_time = models.TimeField(null=True, blank=True, verbose_name="Doğum Saati")
    birth_latitude = models.FloatField(null=True, blank=True, verbose_name="Doğum Yeri Enlemi")
    birth_longitude = models.FloatField(null=True, blank=True, verbose_name="Doğum Yeri Boylamı")
    birth_place = models.CharField(max_length=255, blank=True, verbose_name="Doğum Yeri")
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, verbose_name="Profil Resmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")
    
    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"