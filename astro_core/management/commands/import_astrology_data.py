import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from astro_core.models import (
    AstrologicalSystem, AstrologicalSystemTranslation,
    Sign, SignTranslation, 
    Planet, PlanetTranslation,
    House, HouseTranslation,
    Aspect, AspectTranslation,
    PlanetInSign, PlanetInSignTranslation,
    PlanetInHouse, PlanetInHouseTranslation,
    PlanetAspect, PlanetAspectTranslation
)


class Command(BaseCommand):
    help = 'Batı Astrolojisi verilerini JSON dosyalarından içe aktar'

    def add_arguments(self, parser):
        parser.add_argument('--data-dir', type=str, default='data', help='JSON dosyalarının bulunduğu dizin')
        parser.add_argument('--only', type=str, help='Sadece belirli bir veri türünü içe aktar (signs, planets, houses, aspects, planet_signs, planet_houses, planet_aspects)')

    def handle(self, *args, **options):
        data_dir = options['data_dir']
        only_type = options.get('only')
        
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f'Dizin bulunamadı: {data_dir}'))
            return
        
        # Batı Astrolojisi sistemini oluştur veya al
        astro_system, created = AstrologicalSystem.objects.get_or_create(name="Batı Astrolojisi")
        
        if created:
            self.stdout.write(self.style.SUCCESS('Batı Astrolojisi sistemi oluşturuldu'))
            # Sistem çevirisini ekle
            AstrologicalSystemTranslation.objects.create(
                system=astro_system,
                language="tr",
                name="Batı Astrolojisi",
                description="Batı Astrolojisi, Zodyak burçları sistemine dayanan ve Batı dünyasında yaygın olarak kullanılan astroloji sistemidir."
            )
            AstrologicalSystemTranslation.objects.create(
                system=astro_system,
                language="en",
                name="Western Astrology",
                description="Western Astrology is an astrological system based on the Zodiac signs widely used in the Western world."
            )
        
        # Hangi veri türlerinin içe aktarılacağını belirle
        data_types = ['signs', 'planets', 'houses', 'aspects', 
                     'planet_signs', 'planet_houses', 'planet_aspects']
        
        if only_type and only_type in data_types:
            data_types = [only_type]
        
        # Import işlemleri
        for data_type in data_types:
            file_path = os.path.join(data_dir, f'{data_type}.json')
            
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f'Dosya bulunamadı, atlanıyor: {file_path}'))
                continue
            
            self.stdout.write(self.style.NOTICE(f'{data_type.capitalize()} verilerini içe aktarma...'))
            
            # İlgili import fonksiyonunu çağır
            if data_type == 'signs':
                self.import_signs(file_path, astro_system)
            elif data_type == 'planets':
                self.import_planets(file_path, astro_system)
            elif data_type == 'houses':
                self.import_houses(file_path, astro_system)
            elif data_type == 'aspects':
                self.import_aspects(file_path, astro_system)
            elif data_type == 'planet_signs':
                self.import_planet_signs(file_path, astro_system)
            elif data_type == 'planet_houses':
                self.import_planet_houses(file_path, astro_system)
            elif data_type == 'planet_aspects':
                self.import_planet_aspects(file_path, astro_system)
            
        self.stdout.write(self.style.SUCCESS('Tüm veriler başarıyla içe aktarıldı!'))
    
    def import_signs(self, file_path, astro_system):
        """Burçları içe aktar"""
        with open(file_path, 'r', encoding='utf-8') as file:
            signs_data = json.load(file)
            
        # Element ve modalite / nitelik (quality) seçenekleri 
        element_choices = {
            'Ateş': 'fire',
            'Toprak': 'earth',
            'Hava': 'air',
            'Su': 'water',
            
            'Fire': 'fire',
            'Earth': 'earth',
            'Air': 'air',
            'Water': 'water'
        }
        
        modality_choices = {
            'Öncü': 'cardinal',
            'Sabit': 'fixed',
            'Değişken': 'mutable',
            
            'Cardinal': 'cardinal',
            'Fixed': 'fixed',
            'Mutable': 'mutable'
        }
        
        # Her burç için verileri işle
        for sign_data in signs_data:
            # Burç başlangıç ve bitiş tarihlerini formatlama
            start_date = sign_data.get('date_start', '').split(' ')
            end_date = sign_data.get('date_end', '').split(' ')
            
            if len(start_date) >= 2:
                start_date = f"{start_date[0]}/{self.get_month_number(start_date[1])}"
            else:
                start_date = ""
                
            if len(end_date) >= 2:
                end_date = f"{end_date[0]}/{self.get_month_number(end_date[1])}"
            else:
                end_date = ""
            
            # Element ve nitelik değerlerini alın
            element_tr = sign_data.get('element', {}).get('tr', '')
            element_value = element_choices.get(element_tr, '')
            
            quality_tr = sign_data.get('quality', {}).get('tr', '')
            modality_value = modality_choices.get(quality_tr, '')
            
            # Burç nesnesini oluştur veya güncelle
            sign, sign_created = Sign.objects.update_or_create(
                system=astro_system,
                start_date=start_date,
                end_date=end_date,
                defaults={
                    'element': element_value,
                    'modality': modality_value,
                    'ruling_planet': sign_data.get('ruler', {}).get('tr', '')
                }
            )
            
            # Türkçe çeviri
            keywords_tr = ', '.join(sign_data.get('keywords_tr', []))
            positive_traits_tr = ', '.join(sign_data.get('positive_traits_tr', []))
            negative_traits_tr = ', '.join(sign_data.get('negative_traits_tr', []))
            
            SignTranslation.objects.update_or_create(
                sign=sign,
                language='tr',
                defaults={
                    'name': sign_data.get('name_tr', ''),
                    'symbol': sign_data.get('symbol', ''),
                    'keywords': keywords_tr,
                    'description': sign_data.get('description_tr', ''),
                    'positive_traits': positive_traits_tr,
                    'negative_traits': negative_traits_tr
                }
            )
            
            # İngilizce çeviri
            keywords_en = ', '.join(sign_data.get('keywords_en', []))
            positive_traits_en = ', '.join(sign_data.get('positive_traits_en', []))
            negative_traits_en = ', '.join(sign_data.get('negative_traits_en', []))
            
            SignTranslation.objects.update_or_create(
                sign=sign,
                language='en',
                defaults={
                    'name': sign_data.get('name_en', ''),
                    'symbol': sign_data.get('symbol', ''),
                    'keywords': keywords_en,
                    'description': sign_data.get('description_en', ''),
                    'positive_traits': positive_traits_en,
                    'negative_traits': negative_traits_en
                }
            )
            
            action = 'Güncellendi' if not sign_created else 'Oluşturuldu'
            self.stdout.write(self.style.SUCCESS(f'Burç {sign_data.get("name_tr", "")}: {action}'))
        
        self.stdout.write(self.style.SUCCESS(f'{len(signs_data)} burç verisi başarıyla içe aktarıldı!'))
        
    def import_planets(self, file_path, astro_system):
        """Gezegenleri içe aktar"""
        with open(file_path, 'r', encoding='utf-8') as file:
            planets_data = json.load(file)
        
        for planet_data in planets_data:
            # Gezegen nesnesini oluştur veya güncelle
            planet = Planet.objects.create(
                system=astro_system,)
            
            # Türkçe çeviri
            PlanetTranslation.objects.create(
            planet=planet,
            language='tr',
            name=planet_data.get('name_tr', ''),
            symbol=planet_data.get('symbol', ''),
            keywords=', '.join(planet_data.get('keywords_tr', [])),
            description=planet_data.get('description_tr', '')
        )
            
            # İngilizce çeviri
            PlanetTranslation.objects.create(
            planet=planet,
            language='en',
            name=planet_data.get('name_en', ''),
            symbol=planet_data.get('symbol', ''),
            keywords=', '.join(planet_data.get('keywords_en', [])),
            description=planet_data.get('description_en', '')
        )
            
        self.stdout.write(self.style.SUCCESS(f'Gezegen {planet_data.get("name_tr", "")} (ID: {planet.id}): Oluşturuldu'))

            
            # Yönettiği burçlar, yüceldiği burç vb. ilişkiler daha sonra eklenecek
            # Bunun için önce burçların içe aktarılması gerekir
            
        # Toplam gezegen sayısını kontrol et
        planet_count = Planet.objects.filter(system=astro_system).count()
        self.stdout.write(self.style.SUCCESS(f'{planet_count} gezegen verisi başarıyla içe aktarıldı!'))
    
    def import_houses(self, file_path, astro_system):
        """Evleri içe aktar"""
        with open(file_path, 'r', encoding='utf-8') as file:
            houses_data = json.load(file)
        
        for house_data in houses_data:
            house_number = house_data.get('house_number', 0)
            
            # Ev nesnesini oluştur veya güncelle
            house, house_created = House.objects.update_or_create(
                system=astro_system,
                number=house_number,
                defaults={}
            )
            
            # Türkçe çeviri
            HouseTranslation.objects.update_or_create(
                house=house,
                language='tr',
                defaults={
                    'name': house_data.get('name_tr', ''),
                    'keywords': ', '.join(house_data.get('keywords_tr', [])),
                    'description': house_data.get('description_tr', ''),
                    'ruled_areas': ', '.join(house_data.get('ruled_areas_tr', []))
                }
            )
            
            # İngilizce çeviri
            HouseTranslation.objects.update_or_create(
                house=house,
                language='en',
                defaults={
                    'name': house_data.get('name_en', ''),
                    'keywords': ', '.join(house_data.get('keywords_en', [])),
                    'description': house_data.get('description_en', ''),
                    'ruled_areas': ', '.join(house_data.get('ruled_areas_en', []))
                }
            )
            
            # Doğal burç ilişkisi daha sonra eklenecek
            
            action = 'Güncellendi' if not house_created else 'Oluşturuldu'
            self.stdout.write(self.style.SUCCESS(f'Ev {house_number}: {action}'))
        
        self.stdout.write(self.style.SUCCESS(f'{len(houses_data)} ev verisi başarıyla içe aktarıldı!'))
    
    def import_aspects(self, file_path, astro_system):
        """Açıları içe aktar"""
        with open(file_path, 'r', encoding='utf-8') as file:
            aspects_data = json.load(file)
        
        for aspect_data in aspects_data:
            degrees = aspect_data.get('degree', 0)
            
            # Açı nesnesini oluştur veya güncelle
            aspect, aspect_created = Aspect.objects.update_or_create(
                system=astro_system,
                degrees=degrees,
                defaults={
                    'orb': aspect_data.get('orb', 5.0)
                }
            )
            
            # Türkçe çeviri
            AspectTranslation.objects.update_or_create(
                aspect=aspect,
                language='tr',
                defaults={
                    'name': aspect_data.get('name_tr', ''),
                    'symbol': aspect_data.get('symbol', ''),
                    'keywords': ', '.join(aspect_data.get('keywords_tr', [])),
                    'description': aspect_data.get('description_tr', ''),
                    'nature': aspect_data.get('nature', {}).get('tr', '')
                }
            )
            
            # İngilizce çeviri
            AspectTranslation.objects.update_or_create(
                aspect=aspect,
                language='en',
                defaults={
                    'name': aspect_data.get('name_en', ''),
                    'symbol': aspect_data.get('symbol', ''),
                    'keywords': ', '.join(aspect_data.get('keywords_en', [])),
                    'description': aspect_data.get('description_en', ''),
                    'nature': aspect_data.get('nature', {}).get('en', '')
                }
            )
            
            action = 'Güncellendi' if not aspect_created else 'Oluşturuldu'
            self.stdout.write(self.style.SUCCESS(f'Açı {aspect_data.get("name_tr", "")}: {action}'))
        
        self.stdout.write(self.style.SUCCESS(f'{len(aspects_data)} açı verisi başarıyla içe aktarıldı!'))
    
    def import_planet_signs(self, file_path, astro_system):
        """Gezegen burç yorumlarını içe aktar"""
        with open(file_path, 'r', encoding='utf-8') as file:
            planet_signs_data = json.load(file)
        
        total_imported = 0
        
        for planet_sign_data in planet_signs_data:
            # JSON dosyasındaki alan adlarına göre değerler alınır
            planet_name = planet_sign_data.get('planet_tr', '')
            sign_name = planet_sign_data.get('sign_tr', '')
            
            try:
                # Esnek arama ile gezegen ve burç bulunur
                planet_query = Planet.objects.filter(
                    translations__name__iexact=planet_name,
                    translations__language='tr',
                    system=astro_system
                )
                
                if not planet_query.exists():
                    self.stdout.write(self.style.ERROR(f'Gezegen bulunamadı: "{planet_name}"'))
                    continue
                    
                planet = planet_query.first()
                
                sign_query = Sign.objects.filter(
                    translations__name__iexact=sign_name,
                    translations__language='tr',
                    system=astro_system
                )
                
                if not sign_query.exists():
                    self.stdout.write(self.style.ERROR(f'Burç bulunamadı: "{sign_name}"'))
                    continue
                    
                sign = sign_query.first()
                
                # PlanetInSign nesnesini oluştur veya güncelle
                planet_in_sign, created = PlanetInSign.objects.update_or_create(
                    system=astro_system,
                    planet=planet,
                    sign=sign,
                    defaults={}
                )
                
                # Türkçe çeviri - JSON'daki alan adlarıyla eşleştirildi
                PlanetInSignTranslation.objects.update_or_create(
                    planet_in_sign=planet_in_sign,
                    language='tr',
                    defaults={
                        'general_interpretation': planet_sign_data.get('general_tr', ''),
                        'personality_traits': planet_sign_data.get('personality_tr', ''),
                        'challenges': planet_sign_data.get('challenges_tr', ''),
                        'opportunities': planet_sign_data.get('opportunities_tr', ''),
                        'relationship_impact': planet_sign_data.get('relationships_tr', ''),
                        'career_impact': planet_sign_data.get('career_tr', ''),
                        'advice': planet_sign_data.get('advice_tr', '')
                    }
                )
                
                # İngilizce çeviri
                PlanetInSignTranslation.objects.update_or_create(
                    planet_in_sign=planet_in_sign,
                    language='en',
                    defaults={
                        'general_interpretation': planet_sign_data.get('general_en', ''),
                        'personality_traits': planet_sign_data.get('personality_en', ''),
                        'challenges': planet_sign_data.get('challenges_en', ''),
                        'opportunities': planet_sign_data.get('opportunities_en', ''),
                        'relationship_impact': planet_sign_data.get('relationships_en', ''),
                        'career_impact': planet_sign_data.get('career_en', ''),
                        'advice': planet_sign_data.get('advice_en', '')
                    }
                )
                
                action = 'Güncellendi' if not created else 'Oluşturuldu'
                self.stdout.write(self.style.SUCCESS(f'{planet_name} {sign_name}: {action}'))
                total_imported += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Hata: {planet_name} {sign_name} - {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'{total_imported} gezegen burç yorumu başarıyla içe aktarıldı!'))
    
    def import_planet_houses(self, file_path, astro_system):
        """Gezegen ev yorumlarını içe aktar"""
        with open(file_path, 'r', encoding='utf-8') as file:
            planet_houses_data = json.load(file)
        
        total_imported = 0
        
        for planet_house_data in planet_houses_data:
            # JSON dosyasındaki alan adlarına göre değerler alınır
            planet_name = planet_house_data.get('planet_tr', '')
            house_number = planet_house_data.get('house_number', 0)
            
            try:
                # Esnek arama ile gezegen ve ev bulunur
                planet_query = Planet.objects.filter(
                    translations__name__iexact=planet_name,
                    translations__language='tr',
                    system=astro_system
                )
                
                if not planet_query.exists():
                    self.stdout.write(self.style.ERROR(f'Gezegen bulunamadı: "{planet_name}"'))
                    continue
                    
                planet = planet_query.first()
                
                house_query = House.objects.filter(
                    number=house_number,
                    system=astro_system
                )
                
                if not house_query.exists():
                    self.stdout.write(self.style.ERROR(f'Ev bulunamadı: Ev {house_number}'))
                    continue
                    
                house = house_query.first()
                
                # PlanetInHouse nesnesini oluştur veya güncelle
                planet_in_house, created = PlanetInHouse.objects.update_or_create(
                    system=astro_system,
                    planet=planet,
                    house=house,
                    defaults={}
                )
                
                # Türkçe çeviri - JSON'daki alan adlarıyla eşleştirildi
                PlanetInHouseTranslation.objects.update_or_create(
                    planet_in_house=planet_in_house,
                    language='tr',
                    defaults={
                        'general_interpretation': planet_house_data.get('general_tr', ''),
                        'life_areas_affected': ', '.join(planet_house_data.get('areas_tr', [])),
                        'challenges': planet_house_data.get('challenges_tr', ''),
                        'opportunities': planet_house_data.get('opportunities_tr', ''),
                        'advice': planet_house_data.get('advice_tr', '')
                    }
                )
                
                # İngilizce çeviri
                PlanetInHouseTranslation.objects.update_or_create(
                    planet_in_house=planet_in_house,
                    language='en',
                    defaults={
                        'general_interpretation': planet_house_data.get('general_en', ''),
                        'life_areas_affected': ', '.join(planet_house_data.get('areas_en', [])),
                        'challenges': planet_house_data.get('challenges_en', ''),
                        'opportunities': planet_house_data.get('opportunities_en', ''),
                        'advice': planet_house_data.get('advice_en', '')
                    }
                )
                
                action = 'Güncellendi' if not created else 'Oluşturuldu'
                self.stdout.write(self.style.SUCCESS(f'{planet_name} Ev {house_number}: {action}'))
                total_imported += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Hata: {planet_name} Ev {house_number} - {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'{total_imported} gezegen ev yorumu başarıyla içe aktarıldı!'))
    
    def import_planet_aspects(self, file_path, astro_system):
        """Gezegen açı yorumlarını içe aktar"""
        with open(file_path, 'r', encoding='utf-8') as file:
            planet_aspects_data = json.load(file)
        
        total_imported = 0
        
        for planet_aspect_data in planet_aspects_data:
            # JSON dosyasındaki alan adlarına göre değerler alınır
            planet1_name = planet_aspect_data.get('planet1_tr', '')
            planet2_name = planet_aspect_data.get('planet2_tr', '')
            aspect_name = planet_aspect_data.get('aspect_tr', '')
            
            try:
                # Esnek arama ile gezegenler ve açı bulunur
                planet1_query = Planet.objects.filter(
                    translations__name__iexact=planet1_name,
                    translations__language='tr',
                    system=astro_system
                )
                
                if not planet1_query.exists():
                    self.stdout.write(self.style.ERROR(f'Gezegen 1 bulunamadı: "{planet1_name}"'))
                    continue
                    
                planet1 = planet1_query.first()
                
                planet2_query = Planet.objects.filter(
                    translations__name__iexact=planet2_name,
                    translations__language='tr',
                    system=astro_system
                )
                
                if not planet2_query.exists():
                    self.stdout.write(self.style.ERROR(f'Gezegen 2 bulunamadı: "{planet2_name}"'))
                    continue
                    
                planet2 = planet2_query.first()
                
                aspect_query = Aspect.objects.filter(
                    translations__name__iexact=aspect_name,
                    translations__language='tr',
                    system=astro_system
                )
                
                if not aspect_query.exists():
                    self.stdout.write(self.style.ERROR(f'Açı bulunamadı: "{aspect_name}"'))
                    continue
                    
                aspect = aspect_query.first()
                
                # PlanetAspect nesnesini oluştur veya güncelle
                planet_aspect, created = PlanetAspect.objects.update_or_create(
                    system=astro_system,
                    planet1=planet1,
                    planet2=planet2,
                    aspect=aspect,
                    defaults={}
                )
                
                # Türkçe çeviri - JSON'daki alan adlarıyla eşleştirildi
                PlanetAspectTranslation.objects.update_or_create(
                    planet_aspect=planet_aspect,
                    language='tr',
                    defaults={
                        'general_interpretation': planet_aspect_data.get('general_tr', ''),
                        'personality_traits': planet_aspect_data.get('personality_tr', ''),
                        'challenges': planet_aspect_data.get('challenges_tr', ''),
                        'opportunities': planet_aspect_data.get('opportunities_tr', ''),
                        'relationship_impact': planet_aspect_data.get('relationships_tr', ''),
                        'advice': planet_aspect_data.get('advice_tr', '')
                    }
                )
                
                # İngilizce çeviri
                PlanetAspectTranslation.objects.update_or_create(
                    planet_aspect=planet_aspect,
                    language='en',
                    defaults={
                        'general_interpretation': planet_aspect_data.get('general_en', ''),
                        'personality_traits': planet_aspect_data.get('personality_en', ''),
                        'challenges': planet_aspect_data.get('challenges_en', ''),
                        'opportunities': planet_aspect_data.get('opportunities_en', ''),
                        'relationship_impact': planet_aspect_data.get('relationships_en', ''),
                        'advice': planet_aspect_data.get('advice_en', '')
                    }
                )
                
                action = 'Güncellendi' if not created else 'Oluşturuldu'
                self.stdout.write(self.style.SUCCESS(f'{planet1_name} {aspect_name} {planet2_name}: {action}'))
                total_imported += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Hata: {planet1_name} {aspect_name} {planet2_name} - {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'{total_imported} gezegen açı yorumu başarıyla içe aktarıldı!'))
    
    def get_month_number(self, month_name):
        """Ay adını ay numarasına dönüştürür"""
        months_tr = {
            'Ocak': '01',
            'Şubat': '02',
            'Mart': '03',
            'Nisan': '04',
            'Mayıs': '05',
            'Haziran': '06',
            'Temmuz': '07',
            'Ağustos': '08',
            'Eylül': '09',
            'Ekim': '10',
            'Kasım': '11',
            'Aralık': '12'
        }
        
        months_en = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12'
        }
        
        return months_tr.get(month_name, months_en.get(month_name, ''))