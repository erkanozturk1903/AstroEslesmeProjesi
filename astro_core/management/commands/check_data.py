from django.core.management.base import BaseCommand
from astro_core.models import *

class Command(BaseCommand):
    help = 'Veritabanındaki astrolojik verileri kontrol et'

    def handle(self, *args, **options):
        # Temel veriler
        systems = AstrologicalSystem.objects.all()
        self.stdout.write(f"Toplam sistem sayısı: {systems.count()}")

        planets = Planet.objects.all()
        self.stdout.write(f"Toplam gezegen sayısı: {planets.count()}")

        signs = Sign.objects.all()
        self.stdout.write(f"Toplam burç sayısı: {signs.count()}")

        houses = House.objects.all()
        self.stdout.write(f"Toplam ev sayısı: {houses.count()}")

        aspects = Aspect.objects.all()
        self.stdout.write(f"Toplam açı sayısı: {aspects.count()}")

        # İlişkisel veriler
        planet_signs = PlanetInSign.objects.all()
        self.stdout.write(f"Toplam gezegen-burç ilişkisi: {planet_signs.count()}")

        planet_houses = PlanetInHouse.objects.all()
        self.stdout.write(f"Toplam gezegen-ev ilişkisi: {planet_houses.count()}")

        planet_aspects = PlanetAspect.objects.all()
        self.stdout.write(f"Toplam gezegen-açı ilişkisi: {planet_aspects.count()}")