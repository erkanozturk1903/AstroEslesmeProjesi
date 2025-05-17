from django.core.management.base import BaseCommand
from astro_core.models import Planet, PlanetTranslation

class Command(BaseCommand):
    help = 'Veritabanındaki gezegenleri listele'

    def handle(self, *args, **options):
        planets = Planet.objects.all()
        self.stdout.write(f"Toplam {planets.count()} gezegen bulundu.")
        
        for planet in planets:
            translations = PlanetTranslation.objects.filter(planet=planet)
            for trans in translations:
                self.stdout.write(f"ID: {planet.id}, Dil: {trans.language}, İsim: '{trans.name}'")