# astro_core/services/birth_chart.py

from django.db import transaction
from django.utils import timezone
import datetime
from astro_core.models.user import User
import math
import json

from astro_core.models import (
    BirthChart, AstrologicalSystem, Planet, Sign, House, Aspect,
    PlanetInSign, PlanetInHouse, PlanetAspect, 
)
from .ephemeris import EphemerisCalculator
from .houses import HouseCalculator
from .aspects import AspectCalculator

class BirthChartService:
    """
    Doğum haritası hesaplama, saklama ve yorumlama servisi.
    """
    def __init__(self):
        """
        Servisi başlatır ve gerekli hesaplayıcıları yükler.
        """
        self.ephemeris_calculator = EphemerisCalculator()
        self.house_calculator = HouseCalculator()
        self.aspect_calculator = AspectCalculator()
    
    @transaction.atomic
    def generate_birth_chart(self, user, name, birth_date, birth_time, latitude, longitude, birth_place, system_id=1, house_system="placidus"):
        """
        Doğum haritası hesaplar ve veritabanına kaydeder.
        
        Args:
            user: Kullanıcı nesnesi (User)
            name: Harita için isim (str)
            birth_date: Doğum tarihi (datetime.date)
            birth_time: Doğum saati (datetime.time)
            latitude: Enlem (float)
            longitude: Boylam (float)
            birth_place: Doğum yeri (str)
            system_id: Astrolojik sistem ID (int, varsayılan: 1 - Batı Astrolojisi)
            house_system: Ev sistemi (str, varsayılan: "placidus")
            
        Returns:
            BirthChart: Oluşturulan doğum haritası nesnesi
        """
        # Astrolojik sistemi al
        try:
            system = AstrologicalSystem.objects.get(id=system_id)
        except AstrologicalSystem.DoesNotExist:
            # Varsayılan sistem (Batı Astrolojisi) yoksa oluştur
            system = AstrologicalSystem.objects.create(
                name_tr="Batı Astrolojisi",
                name_en="Western Astrology",
                description_tr="Klasik Batı astrolojisi sistemi",
                description_en="Classical Western astrology system"
            )
        
        # Gezegen konumlarını hesapla
        planet_positions = self.ephemeris_calculator.calculate_planet_positions(
            birth_date, birth_time, latitude, longitude)
        
        # Evleri hesapla
        if house_system.lower() == "placidus":
            houses = self.house_calculator.calculate_houses_placidus(
                birth_date, birth_time, latitude, longitude)
        elif house_system.lower() == "koch":
            houses = self.house_calculator.calculate_houses_koch(
                birth_date, birth_time, latitude, longitude)
        elif house_system.lower() == "whole_sign":
            houses = self.house_calculator.calculate_houses_whole_sign(
                birth_date, birth_time, latitude, longitude)
        else:
            # Varsayılan olarak Placidus kullan
            houses = self.house_calculator.calculate_houses_placidus(
                birth_date, birth_time, latitude, longitude)
        
        # Açıları hesapla
        aspects = self.aspect_calculator.calculate_aspects(planet_positions)
        
        # Doğum haritası nesnesini oluştur
        chart = BirthChart()
        
        # Temel bilgileri doldur
        chart.user = user
        chart.name = name
        chart.system = system
        chart.birth_date = birth_date
        chart.birth_time = birth_time
        chart.birth_latitude = latitude
        chart.birth_longitude = longitude
        chart.birth_place = birth_place
        chart.house_system = house_system
        chart.created_at = timezone.now()
        
        # Yükselen burcu belirle (1. ev)
        # planet_positions içinde hesaplanmış ascendant bilgisi varsa al
        if 'ascendant' in planet_positions:
            asc_sign_num = planet_positions['ascendant']['sign_num']
        else:
            # Houses'dan al, ID'ler 1'den başlar
            asc_sign_num = houses[1]['sign_num']
        
        # MC (Medium Coeli) burcu belirle (10. ev)
        if 'mc' in planet_positions:
            mc_sign_num = planet_positions['mc']['sign_num']
        else:
            mc_sign_num = houses[10]['sign_num']
        
        # Bulunan sign_num değerlerini veritabanı ID'sine çevir
        try:
            # Burçları start_date'e göre sıralayıp indeksle alıyoruz
            signs = list(Sign.objects.filter(system=system).order_by('start_date'))
            chart.ascendant_sign = signs[asc_sign_num - 1] if 0 < asc_sign_num <= len(signs) else None
        except (IndexError, Exception):
            # Burcun ID'si bulunamadı, log tutulmalı
            chart.ascendant_sign = None
        
        try:
            # Burçları start_date'e göre sıralayıp indeksle alıyoruz
            signs = list(Sign.objects.filter(system=system).order_by('start_date'))
            chart.mc_sign = signs[mc_sign_num - 1] if 0 < mc_sign_num <= len(signs) else None
        except (IndexError, Exception):
            chart.mc_sign = None
        
        # Ay fazını ve lunar günü hesapla
        lunar_phase = self.ephemeris_calculator.calculate_lunar_phase(
            birth_date, birth_time, latitude, longitude)
        
        # JSON formatında tüm hesaplanmış verileri sakla
        chart_data = {
            'planet_positions': planet_positions,
            'houses': houses,
            'aspects': aspects,
            'lunar_phase': lunar_phase
        }
        
        # chart_data'yı JSON'a çevir
        chart.chart_data = json.dumps(chart_data, default=str)
        
        # Kaydet
        chart.save()
        
        # İlişkili nesneleri (planet_in_sign, planet_in_house, planet_aspect) oluştur
        self._create_related_objects(chart, planet_positions, houses, aspects)
        
        return chart
    
    def _create_related_objects(self, chart, planet_positions, houses, aspects):
        """
        Doğum haritası ile ilişkili nesneleri (gezegen-burç, gezegen-ev, açılar) oluşturur.
        
        Args:
            chart: Doğum haritası nesnesi
            planet_positions: Gezegen konumları
            houses: Ev konumları
            aspects: Açılar
        """
        system = chart.system
        
        # 1. Gezegen-Burç ilişkileri oluştur
        for planet_name, data in planet_positions.items():
            # Sadece gezegenler için işlem yap (özel noktaları atla)
            if planet_name in ['ramc', 'obliquity']:
                continue
                
            if 'sign_num' in data:
                sign_num = data['sign_num']
                degree = data.get('degree_in_sign', 0.0)
                
                try:
                    # Gezegen ve burcu veritabanından bul
                    planet = Planet.objects.filter(
                        translations__language='en',
                        translations__name__iexact=planet_name,
                        system=system
                    ).first()

                    if not planet: 
                        # Gezegen bulunamadı, sonraki gezegene geç
                        continue
                    
                    # Burcu sırasına göre al
                    signs = list(Sign.objects.filter(system=system).order_by('start_date'))
                    sign = signs[sign_num - 1] if 0 < sign_num <= len(signs) else None
                    
                    if sign:
                        # Gezegen-Burç ilişkisi oluştur
                        PlanetInSign.objects.create(
                            birth_chart=chart,
                            planet=planet,
                            sign=sign,
                            degree=degree,
                            is_retrograde=data.get('is_retrograde', False),
                            chart_position='natal'  # Doğum haritası için varsayılan
                        )
                except (Planet.DoesNotExist, IndexError, Exception):
                    # Veritabanında bulunamayan gezegen veya burç olabilir
                    # Log tutulmalı
                    pass
        
        # 2. Gezegen-Ev ilişkileri oluştur
        for planet_name, data in planet_positions.items():
            # Sadece gezegenler için işlem yap (özel noktaları atla)
            if planet_name in ['ramc', 'obliquity'] or not isinstance(data, dict) or 'longitude' not in data:
                continue
            
            planet_lon = data['longitude']
            
            # Bu gezegenin hangi evde olduğunu bul
            house_num = self._find_house_for_position(planet_lon, houses)
            
            if house_num is not None:
                try:
                    # Gezegen ve evi veritabanından bul
                    planet = Planet.objects.filter(
                        translations__language='en',
                        translations__name__iexact=planet_name,
                        system=system
                    ).first()
                    house = House.objects.get(number=house_num, system=system)
                    
                    # Gezegen-Ev ilişkisi oluştur
                    PlanetInHouse.objects.create(
                        birth_chart=chart,
                        planet=planet,
                        house=house,
                        longitude=planet_lon,
                        chart_position='natal'  # Doğum haritası için varsayılan
                    )
                except (Planet.DoesNotExist, House.DoesNotExist):
                    # Veritabanında bulunamayan gezegen veya ev olabilir
                    # Log tutulmalı
                    pass
        
        # 3. Açı ilişkileri oluştur
        for aspect_data in aspects:
            planet1_name = aspect_data['planet1']
            planet2_name = aspect_data['planet2']
            aspect_type = aspect_data['aspect_type']
            orb = aspect_data['orb']
            
            try:
                # Gezegenler ve açı türünü veritabanından bul
                # Şununla değiştirin:
                planet1 = Planet.objects.filter(
                    translations__language='en', 
                    translations__name__iexact=planet1_name, 
                    system=system
                ).first()

                planet2 = Planet.objects.filter(
                    translations__language='en', 
                    translations__name__iexact=planet2_name, 
                    system=system
                ).first()

                aspect = Aspect.objects.filter(
                    translations__language='en', 
                    translations__name__iexact=aspect_type, 
                    system=system
                ).first()

                if not planet1 or not planet2 or not aspect:
                    # Gezegenlerden biri veya açı bulunamadı, sonraki açıya geç
                    continue
                
                # Açı ilişkisi oluştur
                PlanetAspect.objects.create(
                    birth_chart=chart,
                    planet1=planet1,
                    planet2=planet2,
                    aspect=aspect,
                    orb=orb,
                    is_applying=aspect_data.get('is_applying', False),
                    is_exact=aspect_data.get('is_exact', False),
                    is_separating=aspect_data.get('is_separating', False),
                    chart_position='natal'  # Doğum haritası için varsayılan
                )
            except (Planet.DoesNotExist, Aspect.DoesNotExist):
                # Veritabanında bulunamayan gezegen veya açı olabilir
                # Log tutulmalı
                pass
    
    def _find_house_for_position(self, longitude, houses):
        """
        Belirli bir ekliptik boylam için hangi evde olduğunu bulur.
        
        Args:
            longitude (float): Ekliptik boylam
            houses (dict): Ev konumları
            
        Returns:
            int: Evin numarası veya None (ev bulunamazsa)
        """
        # Saat yönünde evleri kontrol et (12. evden 1. eve)
        for i in range(12, 0, -1):
            # Şu anki ev ve bir sonraki ev
            current_house = houses.get(i)
            next_house = houses.get(i % 12 + 1)  # 12'den sonra 1 gelir
            
            if current_house is None or next_house is None:
                continue
            
            current_cusp = current_house['cusp_longitude']
            next_cusp = next_house['cusp_longitude']
            
            # Ekliptik çemberi üzerinde kontrol (0-360 derece çevrimi)
            if next_cusp < current_cusp:  # 0 derece geçişi var
                if longitude >= current_cusp or longitude < next_cusp:
                    return i
            else:  # Normal durum
                if current_cusp <= longitude < next_cusp:
                    return i
        
        # Bir şeyler yanlış gitti, ev bulunamadı
        return None
    
    def get_chart_with_interpretations(self, chart_id):
        """
        Doğum haritası ve yorumlarını bir araya getirir.
        
        Args:
            chart_id (int): Doğum haritası ID'si
            
        Returns:
            dict: Harita ve yorumları içeren sözlük veya None (harita bulunamazsa)
        """
        try:
            birth_chart = BirthChart.objects.get(id=chart_id)
        except BirthChart.DoesNotExist:
            return None
        
        # JSON verilerini yükle
        chart_data = json.loads(birth_chart.chart_data)
        
        # Sonuç için temel yapı oluştur
        result = {
            'id': birth_chart.id,
            'name': birth_chart.name,
            'birth_date': birth_chart.birth_date,
            'birth_time': birth_chart.birth_time,
            'birth_place': birth_chart.birth_place,
            'birth_latitude': birth_chart.birth_latitude,
            'birth_longitude': birth_chart.birth_longitude,
            'house_system': birth_chart.house_system,
            'created_at': birth_chart.created_at,
            'planets': {},
            'houses': {},
            'aspects': [],
            'special_points': {},
            'lunar_phase': chart_data.get('lunar_phase', {})
        }
        
        # Yükselen ve MC burcunu ekle
        if birth_chart.ascendant_sign:
            result['ascendant'] = {
                'sign_id': birth_chart.ascendant_sign.id,
                'sign_name_tr': birth_chart.ascendant_sign.name_tr,
                'sign_name_en': birth_chart.ascendant_sign.name_en,
                'sign_symbol': birth_chart.ascendant_sign.symbol
            }
        
        if birth_chart.mc_sign:
            result['mc'] = {
                'sign_id': birth_chart.mc_sign.id,
                'sign_name_tr': birth_chart.mc_sign.name_tr,
                'sign_name_en': birth_chart.mc_sign.name_en,
                'sign_symbol': birth_chart.mc_sign.symbol
            }
        
        # 1. Gezegen-Burç yorumlarını ekle
        # PlanetInSign nesnelerini çek (ilişkili modellerle birlikte)
        planet_in_signs = PlanetInSign.objects.filter(birth_chart=birth_chart)\
            .select_related('planet', 'sign')
        
        for pis in planet_in_signs:
            # Gezegen adı
            planet_name = pis.planet.name_en.lower()
            
            # Bu gezegen için temel bilgiler
            result['planets'][planet_name] = {
                'id': pis.planet.id,
                'name_tr': pis.planet.name_tr,
                'name_en': pis.planet.name_en,
                'symbol': pis.planet.symbol,
                'sign': {
                    'id': pis.sign.id,
                    'name_tr': pis.sign.name_tr,
                    'name_en': pis.sign.name_en,
                    'symbol': pis.sign.symbol,
                    'element': pis.sign.element,
                    'modality': pis.sign.modality
                },
                'degree': pis.degree,
                'is_retrograde': pis.is_retrograde,
                'interpretation': {}
            }
            
            # Yorumları ekle (veritabanında varsa)
            try:
                # Gezegen-Burç yorumunu bul
                planet_sign_interp = PlanetInSign.objects.get(
                    planet=pis.planet,
                    sign=pis.sign,
                    birth_chart=None  # Veritabanındaki genel yorum
                )
                
                result['planets'][planet_name]['interpretation'] = {
                    'general_tr': planet_sign_interp.general_tr,
                    'general_en': planet_sign_interp.general_en,
                    'personality_tr': planet_sign_interp.personality_tr,
                    'personality_en': planet_sign_interp.personality_en,
                    'challenges_tr': planet_sign_interp.challenges_tr,
                    'challenges_en': planet_sign_interp.challenges_en,
                    'opportunities_tr': planet_sign_interp.opportunities_tr,
                    'opportunities_en': planet_sign_interp.opportunities_en
                }
            except PlanetInSign.DoesNotExist:
                # Yorum bulunamadı, boş bırak
                pass
        
        # 2. Gezegen-Ev yorumlarını ekle
        planet_in_houses = PlanetInHouse.objects.filter(birth_chart=birth_chart)\
            .select_related('planet', 'house')
        
        # Önce tüm evleri sonuçlara ekle
        for house_num in range(1, 13):
            result['houses'][house_num] = {
                'planets': [],
                'interpretation': {}
            }
        
        # Şimdi her bir gezegen-ev ilişkisini işle
        for pih in planet_in_houses:
            planet_name = pih.planet.name_en.lower()
            house_num = pih.house.number
            
            # Ev bilgisine gezegeni ekle
            result['houses'][house_num]['planets'].append(planet_name)
            
            # Gezegen bilgisine evi ekle
            if planet_name in result['planets']:
                result['planets'][planet_name]['house'] = {
                    'number': house_num,
                    'name_tr': pih.house.name_tr,
                    'name_en': pih.house.name_en
                }
            
            # Yorumları ekle (veritabanında varsa)
            try:
                # Gezegen-Ev yorumunu bul
                planet_house_interp = PlanetInHouse.objects.get(
                    planet=pih.planet,
                    house=pih.house,
                    birth_chart=None  # Veritabanındaki genel yorum
                )
                
                if planet_name in result['planets']:
                    result['planets'][planet_name]['house_interpretation'] = {
                        'general_tr': planet_house_interp.general_tr,
                        'general_en': planet_house_interp.general_en,
                        'areas_affected_tr': planet_house_interp.areas_affected_tr,
                        'areas_affected_en': planet_house_interp.areas_affected_en,
                        'challenges_tr': planet_house_interp.challenges_tr,
                        'challenges_en': planet_house_interp.challenges_en,
                        'opportunities_tr': planet_house_interp.opportunities_tr,
                        'opportunities_en': planet_house_interp.opportunities_en
                    }
            except PlanetInHouse.DoesNotExist:
                # Yorum bulunamadı, boş bırak
                pass
        
        # 3. Açı yorumlarını ekle
        planet_aspects = PlanetAspect.objects.filter(birth_chart=birth_chart)\
            .select_related('planet1', 'planet2', 'aspect')
        
        for pa in planet_aspects:
            planet1_name = pa.planet1.name_en.lower()
            planet2_name = pa.planet2.name_en.lower()
            aspect_name = pa.aspect.name_en.lower()
            
            aspect_data = {
                'id': pa.id,
                'planet1': {
                    'id': pa.planet1.id,
                    'name_tr': pa.planet1.name_tr,
                    'name_en': pa.planet1.name_en,
                    'symbol': pa.planet1.symbol
                },
                'planet2': {
                    'id': pa.planet2.id,
                    'name_tr': pa.planet2.name_tr,
                    'name_en': pa.planet2.name_en,
                    'symbol': pa.planet2.symbol
                },
                'aspect': {
                    'id': pa.aspect.id,
                    'name_tr': pa.aspect.name_tr,
                    'name_en': pa.aspect.name_en,
                    'symbol': pa.aspect.symbol,
                    'angle': pa.aspect.angle,
                    'orb': pa.aspect.orb,
                    'nature': pa.aspect.nature
                },
                'orb': pa.orb,
                'is_applying': pa.is_applying,
                'is_exact': pa.is_exact,
                'is_separating': pa.is_separating,
                'interpretation': {}
            }
            
            # Açı yorumunu ekle (veritabanında varsa)
            try:
                # İlk 5 ana gezegen için özel yorumları ara
                if planet1_name in ['sun', 'moon', 'mercury', 'venus', 'mars'] and \
                   planet2_name in ['sun', 'moon', 'mercury', 'venus', 'mars']:
                    aspect_interp = PlanetAspect.objects.get(
                        planet1=pa.planet1,
                        planet2=pa.planet2,
                        aspect=pa.aspect,
                        birth_chart=None  # Veritabanındaki genel yorum
                    )
                
                    aspect_data['interpretation'] = {
                        'general_tr': aspect_interp.general_tr,
                        'general_en': aspect_interp.general_en,
                        'personality_tr': aspect_interp.personality_tr,
                        'personality_en': aspect_interp.personality_en,
                        'challenges_tr': aspect_interp.challenges_tr,
                        'challenges_en': aspect_interp.challenges_en,
                        'opportunities_tr': aspect_interp.opportunities_tr,
                        'opportunities_en': aspect_interp.opportunities_en
                    }
            except PlanetAspect.DoesNotExist:
                # Yorum bulunamadı, boş bırak
                pass
            
            # Aspect'i sonuçlara ekle
            result['aspects'].append(aspect_data)
        
        # 4. Özel noktaları ekle (Kuzey Düğümü, Part of Fortune vb.)
        for special_point in ['north_node', 'south_node', 'part_of_fortune', 'ascendant', 'mc']:
            if special_point in chart_data.get('planet_positions', {}):
                result['special_points'][special_point] = chart_data['planet_positions'][special_point]
        
        return result
    
    def calculate_transits(self, birth_chart_id, transit_date=None, transit_time=None):
        """
        Doğum haritası üzerindeki transit gezegen konumlarını ve açılarını hesaplar.
        
        Args:
            birth_chart_id (int): Doğum haritasının ID'si
            transit_date (datetime.date, optional): Transit tarihi (None ise bugün)
            transit_time (datetime.time, optional): Transit saati (None ise şu an)
            
        Returns:
            dict: Transit bilgileri ve açıları
        """
        try:
            birth_chart = BirthChart.objects.get(id=birth_chart_id)
        except BirthChart.DoesNotExist:
            return None
        
        # Transit tarihi ve zamanı belirle
        if transit_date is None:
            transit_date = datetime.date.today()
        
        if transit_time is None:
            now = datetime.datetime.now()
            transit_time = datetime.time(now.hour, now.minute, now.second)
        
        # Doğum haritası verilerini al
        natal_data = json.loads(birth_chart.chart_data)
        natal_positions = natal_data.get('planet_positions', {})
        
        # Transit gezegen konumlarını hesapla
        # Varsayılan olarak doğum yerini kullan (özelleştirilebilir)
        transit_positions = self.ephemeris_calculator.calculate_planet_positions(
            transit_date, 
            transit_time, 
            birth_chart.birth_latitude, 
            birth_chart.birth_longitude
        )
        
        # Transit-Natal açılarını hesapla
        # Ephemeris sonuçlarından sadece gezegenler için bir sözlük oluştur
        natal_planet_positions = {}
        transit_planet_positions = {}
        
        # Natal gezegen konumları
        for planet, data in natal_positions.items():
            if planet not in ['ramc', 'obliquity'] and isinstance(data, dict) and 'longitude' in data:
                natal_planet_positions[planet] = data
        
        # Transit gezegen konumları
        for planet, data in transit_positions.items():
            if planet not in ['ramc', 'obliquity'] and isinstance(data, dict) and 'longitude' in data:
                transit_planet_positions[planet] = data
        
        # Transit-Natal açılarını hesaplayacak özel bir fonksiyon
        transit_aspects = []
        for t_planet, t_data in transit_planet_positions.items():
            t_lon = t_data['longitude']
            
            for n_planet, n_data in natal_planet_positions.items():
                n_lon = n_data['longitude']
                
                # Açı farkı (0-180 arası)
                angle_diff = abs(t_lon - n_lon) % 360
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                
                # Açı tipini belirle
                aspect_type = None
                orb = 0.0
                
                # Transit açıları için daha sıkı orb değerleri kullan
                if abs(angle_diff) <= 8.0:  # Kavuşum (Conjunction)
                    aspect_type = "conjunction"
                    orb = abs(angle_diff)
                elif abs(angle_diff - 180) <= 8.0:  # Karşıt (Opposition)
                    aspect_type = "opposition"
                    orb = abs(angle_diff - 180)
                elif abs(angle_diff - 90) <= 6.0:  # Kare (Square)
                    aspect_type = "square"
                    orb = abs(angle_diff - 90)
                elif abs(angle_diff - 120) <= 6.0:  # Üçgen (Trine)
                    aspect_type = "trine"
                    orb = abs(angle_diff - 120)
                elif abs(angle_diff - 60) <= 4.0:  # Altmışlık (Sextile)
                    aspect_type = "sextile"
                    orb = abs(angle_diff - 60)
                elif abs(angle_diff - 150) <= 4.0:  # Yüzellilik (Quincunx)
                    aspect_type = "quincunx"
                    orb = abs(angle_diff - 150)
                elif abs(angle_diff - 30) <= 2.0:  # Otuzluk (Semi-sextile)
                    aspect_type = "semi_sextile"
                    orb = abs(angle_diff - 30)
                
                # Açı bulunduysa listeye ekle
                if aspect_type:
                    # Açının doğasını belirle
                    nature = "neutral"
                    if aspect_type in ["trine", "sextile"]:
                        nature = "harmonious"
                    elif aspect_type in ["opposition", "square", "quincunx"]:
                        nature = "challenging"
                    
                    # Kavuşum açısının doğası özel durumdur
                    if aspect_type == "conjunction":
                        # Zorlu gezegenler kavuşumda zorlu etki yapar
                        if t_planet in ["mars", "saturn", "uranus", "pluto"] or n_planet in ["mars", "saturn", "uranus", "pluto"]:
                            nature = "challenging"
                        # Uyumlu gezegenler kavuşumda uyumlu etki yapar
                        elif t_planet in ["venus", "jupiter"] or n_planet in ["venus", "jupiter"]:
                            nature = "harmonious"
                    
                    # Transit açısı yaklaşıyor mu uzaklaşıyor mu?
                    # Transit gezegenin hızına bak
                    speed = t_data.get('daily_motion', 1.0)  # Varsayılan 1 derece/gün
                    is_retrograde = t_data.get('is_retrograde', False)
                    
                    # İkinci açı için hedef değer
                    target_angle = self.aspect_calculator.aspect_types[aspect_type]
                    
                    # Açının yaklaşan veya uzaklaşan olduğunu kontrol et
                    # Basit yaklaşım: Retrograde durumuna bak
                    if aspect_type == "conjunction":  # Kavuşum için
                        is_applying = (not is_retrograde and t_lon < n_lon) or (is_retrograde and t_lon > n_lon)
                    else:
                        # Diğer açılar için karmaşık hesaplama gerekir
                        # Basitleştirilmiş yaklaşım
                        is_applying = not is_retrograde
                    
                    # Açıyı listeye ekle
                    # Açıyı listeye ekle
                    transit_aspects.append({
                        'transit_planet': t_planet,
                        'natal_planet': n_planet,
                        'aspect_type': aspect_type,
                        'angle': angle_diff,
                        'orb': orb,
                        'nature': nature,
                        'is_applying': is_applying,
                        'is_exact': orb < 0.5,  # 0.5 dereceden az fark varsa tam kabul et
                        'is_separating': not is_applying
                    })
        
        # Açıları önemine göre sırala
        # 1. Tam açılar (exact)
        # 2. Yaklaşan açılar (applying)
        # 3. Uzaklaşan açılar (separating)
        # 4. Her kategori içinde orbuna (küçükten büyüğe) göre sırala
        transit_aspects.sort(key=lambda x: (
           0 if x['is_exact'] else (1 if x['is_applying'] else 2),  # Önce tam, sonra yaklaşan, sonra uzaklaşan
           x['orb']  # Orbu küçük olanlar önce
       ))
       
        # Sonuç sözlüğü oluştur
        result = {
           'birth_chart_id': birth_chart_id,
           'birth_chart_name': birth_chart.name,
           'transit_date': transit_date,
           'transit_time': transit_time,
           'transit_positions': transit_planet_positions,
           'transit_aspects': transit_aspects
       }
       
        return result
   
    def calculate_secondary_progressions(self, birth_chart_id, target_date=None):
       """
       İkincil ilerleme (secondary progression) gezegen konumlarını hesaplar.
       
       Args:
           birth_chart_id (int): Doğum haritasının ID'si
           target_date (datetime.date, optional): Hedef tarih (None ise bugün)
           
       Returns:
           dict: İlerleme bilgileri ve doğum haritasıyla açıları
       """
       try:
           birth_chart = BirthChart.objects.get(id=birth_chart_id)
       except BirthChart.DoesNotExist:
           return None
       
       # Hedef tarihi belirle
       if target_date is None:
           target_date = datetime.date.today()
       
       # Doğum tarihi ve hedef tarih arasındaki gün sayısını hesapla
       birth_date = birth_chart.birth_date
       days_diff = (target_date - birth_date).days
       
       # İkincil ilerleme: 1 gün = 1 yıl (365.25 gün)
       progression_days = days_diff / 365.25
       
       # İlerleme tarihini hesapla
       progression_date = birth_date + datetime.timedelta(days=progression_days)
       
       # İlerleme saatini doğum saati olarak kullan
       progression_time = birth_chart.birth_time
       
       # İlerlemiş gezegen konumlarını hesapla
       progressed_positions = self.ephemeris_calculator.calculate_planet_positions(
           progression_date, 
           progression_time, 
           birth_chart.birth_latitude, 
           birth_chart.birth_longitude
       )
       
       # Doğum haritası verilerini al
       natal_data = json.loads(birth_chart.chart_data)
       natal_positions = natal_data.get('planet_positions', {})
       
       # İlerleme-Natal açılarını hesapla
       # Sadece gezegenler için bir sözlük oluştur
       natal_planet_positions = {}
       progressed_planet_positions = {}
       
       # Natal gezegen konumları
       for planet, data in natal_positions.items():
           if planet not in ['ramc', 'obliquity'] and isinstance(data, dict) and 'longitude' in data:
               natal_planet_positions[planet] = data
       
       # İlerleme gezegen konumları
       for planet, data in progressed_positions.items():
           if planet not in ['ramc', 'obliquity'] and isinstance(data, dict) and 'longitude' in data:
               progressed_planet_positions[planet] = data
       
       # İlerleme-Natal açılarını hesapla
       progressed_aspects = self.aspect_calculator.calculate_aspects(
           {**progressed_planet_positions, **natal_planet_positions},
           include_minor_aspects=False
       )
       
       # Sadece ilerleme-natal açılarını filtrele (ilerleme-ilerleme ve natal-natal açılarını çıkar)
       filtered_aspects = []
       for aspect in progressed_aspects:
           planet1 = aspect['planet1']
           planet2 = aspect['planet2']
           
           # Bir gezegen ilerleme, diğeri natal ise ekle
           if (planet1 in progressed_planet_positions and planet2 in natal_planet_positions) or \
              (planet1 in natal_planet_positions and planet2 in progressed_planet_positions):
               # Açının progressed_planet ve natal_planet olarak yeniden etiketlenmesi
               if planet1 in progressed_planet_positions:
                   aspect['progressed_planet'] = planet1
                   aspect['natal_planet'] = planet2
               else:
                   aspect['progressed_planet'] = planet2
                   aspect['natal_planet'] = planet1
               
               filtered_aspects.append(aspect)
       
       # Sonuç sözlüğü oluştur
       result = {
           'birth_chart_id': birth_chart_id,
           'birth_chart_name': birth_chart.name,
           'progression_date': progression_date,
           'years_progressed': days_diff / 365.25,
           'progressed_positions': progressed_planet_positions,
           'progressed_aspects': filtered_aspects
       }
       
       return result
   
    def calculate_solar_return(self, birth_chart_id, year=None):
       """
       Belirli bir yıl için güneş dönüşü (solar return) haritasını hesaplar.
       
       Args:
           birth_chart_id (int): Doğum haritasının ID'si
           year (int, optional): Güneş dönüşü yılı (None ise şu anki yıl)
           
       Returns:
           dict: Güneş dönüşü haritası bilgileri
       """
       try:
           birth_chart = BirthChart.objects.get(id=birth_chart_id)
       except BirthChart.DoesNotExist:
           return None
       
       # Güneş dönüşü yılını belirle
       if year is None:
           year = datetime.date.today().year
       
       # Güneş dönüşü tarihini hesapla
       solar_return_datetime = self.ephemeris_calculator.calculate_solar_return(
           birth_chart.birth_date, year)
       
       # Sonuçları ayrıştır
       solar_return_date = solar_return_datetime.date()
       solar_return_time = solar_return_datetime.time()
       
       # Güneş dönüşü haritasını hesapla (doğum yeri için)
       solar_positions = self.ephemeris_calculator.calculate_planet_positions(
           solar_return_date, 
           solar_return_time, 
           birth_chart.birth_latitude, 
           birth_chart.birth_longitude
       )
       
       # Güneş dönüşü evlerini hesapla
       solar_houses = self.house_calculator.calculate_houses_placidus(
           solar_return_date, 
           solar_return_time, 
           birth_chart.birth_latitude, 
           birth_chart.birth_longitude
       )
       
       # Güneş dönüşü açılarını hesapla
       solar_aspects = self.aspect_calculator.calculate_aspects(solar_positions)
       
       # Doğum haritası verilerini al
       natal_data = json.loads(birth_chart.chart_data)
       natal_positions = natal_data.get('planet_positions', {})
       
       # Solar-Natal açılarını hesapla
       # Sadece gezegenler için bir sözlük oluştur
       natal_planet_positions = {}
       solar_planet_positions = {}
       
       # Natal gezegen konumları
       for planet, data in natal_positions.items():
           if planet not in ['ramc', 'obliquity'] and isinstance(data, dict) and 'longitude' in data:
               natal_planet_positions[planet] = data
       
       # Solar gezegen konumları
       for planet, data in solar_positions.items():
           if planet not in ['ramc', 'obliquity'] and isinstance(data, dict) and 'longitude' in data:
               solar_planet_positions[planet] = data
       
       # Solar-Natal açılarını hesapla
       solar_natal_aspects = []
       for s_planet, s_data in solar_planet_positions.items():
           s_lon = s_data['longitude']
           
           for n_planet, n_data in natal_planet_positions.items():
               n_lon = n_data['longitude']
               
               # Açı farkı (0-180 arası)
               angle_diff = abs(s_lon - n_lon) % 360
               if angle_diff > 180:
                   angle_diff = 360 - angle_diff
               
               # Açı tipini belirle (sadece majör açıları kontrol et)
               aspect_type = None
               orb = 0.0
               
               # Solar-Natal açıları için orta orb değerleri kullan
               if abs(angle_diff) <= 7.0:  # Kavuşum (Conjunction)
                   aspect_type = "conjunction"
                   orb = abs(angle_diff)
               elif abs(angle_diff - 180) <= 7.0:  # Karşıt (Opposition)
                   aspect_type = "opposition"
                   orb = abs(angle_diff - 180)
               elif abs(angle_diff - 90) <= 5.0:  # Kare (Square)
                   aspect_type = "square"
                   orb = abs(angle_diff - 90)
               elif abs(angle_diff - 120) <= 5.0:  # Üçgen (Trine)
                   aspect_type = "trine"
                   orb = abs(angle_diff - 120)
               elif abs(angle_diff - 60) <= 3.0:  # Altmışlık (Sextile)
                   aspect_type = "sextile"
                   orb = abs(angle_diff - 60)
               
               # Açı bulunduysa listeye ekle
               if aspect_type:
                   # Açının doğasını belirle
                   nature = "neutral"
                   if aspect_type in ["trine", "sextile"]:
                       nature = "harmonious"
                   elif aspect_type in ["opposition", "square"]:
                       nature = "challenging"
                   
                   # Kavuşum açısının doğası özel durumdur
                   if aspect_type == "conjunction":
                       # Zorlu gezegenler kavuşumda zorlu etki yapar
                       if s_planet in ["mars", "saturn", "uranus", "pluto"] or n_planet in ["mars", "saturn", "uranus", "pluto"]:
                           nature = "challenging"
                       # Uyumlu gezegenler kavuşumda uyumlu etki yapar
                       elif s_planet in ["venus", "jupiter"] or n_planet in ["venus", "jupiter"]:
                           nature = "harmonious"
                   
                   # Açıyı listeye ekle
                   solar_natal_aspects.append({
                       'solar_planet': s_planet,
                       'natal_planet': n_planet,
                       'aspect_type': aspect_type,
                       'angle': angle_diff,
                       'orb': orb,
                       'nature': nature
                   })
       
       # Açıları orbuna göre sırala (küçükten büyüğe)
       solar_natal_aspects.sort(key=lambda x: x['orb'])
       
       # Sonuç sözlüğü oluştur
       result = {
           'birth_chart_id': birth_chart_id,
           'birth_chart_name': birth_chart.name,
           'solar_return_date': solar_return_date,
           'solar_return_time': solar_return_time,
           'year': year,
           'positions': solar_planet_positions,
           'houses': solar_houses,
           'aspects': solar_aspects,
           'solar_natal_aspects': solar_natal_aspects
       }
       
       return result
   
    def calculate_compatibility(self, chart1_id, chart2_id):
       """
       İki doğum haritası arasındaki uyumluluğu hesaplar.
       
       Args:
           chart1_id (int): Birinci doğum haritasının ID'si
           chart2_id (int): İkinci doğum haritasının ID'si
           
       Returns:
           dict: Uyumluluk bilgilerini ve puanlarını içeren sözlük
       """
       try:
           chart1 = BirthChart.objects.get(id=chart1_id)
           chart2 = BirthChart.objects.get(id=chart2_id)
       except BirthChart.DoesNotExist:
           return None
       
       # Doğum haritası verilerini al
       chart1_data = json.loads(chart1.chart_data)
       chart2_data = json.loads(chart2.chart_data)
       
       chart1_positions = chart1_data.get('planet_positions', {})
       chart2_positions = chart2_data.get('planet_positions', {})
       
       # Sadece gezegenler için pozisyonları filtrele
       chart1_planet_positions = {}
       chart2_planet_positions = {}
       
       # Natal gezegen konumları - Chart 1
       for planet, data in chart1_positions.items():
           if planet not in ['ramc', 'obliquity'] and isinstance(data, dict) and 'longitude' in data:
               chart1_planet_positions[planet] = data
       
       # Natal gezegen konumları - Chart 2
       for planet, data in chart2_positions.items():
           if planet not in ['ramc', 'obliquity'] and isinstance(data, dict) and 'longitude' in data:
               chart2_planet_positions[planet] = data
       
       # İki harita arasındaki uyumluluğu hesapla
       compatibility = self.aspect_calculator.calculate_chart_compatibility(
           chart1_planet_positions, chart2_planet_positions)
       
       # İki harita arasındaki sinastri açılarını hesapla
       synastry_aspects = self.aspect_calculator.calculate_composite_aspects(
           chart1_planet_positions, chart2_planet_positions)
       
       # Composite haritasını hesapla
       composite_positions = self._calculate_composite_chart(
           chart1_planet_positions, chart2_planet_positions)
       
       # Composite haritasının açılarını hesapla
       composite_aspects = self.aspect_calculator.calculate_aspects(composite_positions)
       
       # Sonuç sözlüğünü oluştur
       result = {
           'chart1_id': chart1_id,
           'chart1_name': chart1.name,
           'chart2_id': chart2_id,
           'chart2_name': chart2.name,
           'compatibility_scores': compatibility,
           'synastry_aspects': synastry_aspects,
           'composite_positions': composite_positions,
           'composite_aspects': composite_aspects
       }
       
       return result
   
    def _calculate_composite_chart(self, chart1_positions, chart2_positions):
       """
       İki doğum haritasından kompozit (orta nokta) haritasını hesaplar.
       
       Args:
           chart1_positions (dict): Birinci haritanın gezegen konumları
           chart2_positions (dict): İkinci haritanın gezegen konumları
           
       Returns:
           dict: Kompozit haritasının gezegen konumları
       """
       composite_positions = {}
       
       # Ortak gezegenleri bul
       common_planets = set(chart1_positions.keys()).intersection(set(chart2_positions.keys()))
       
       # Her bir ortak gezegen için orta noktayı hesapla
       for planet in common_planets:
           # Gezegenin her iki haritadaki konumunu al
           lon1 = chart1_positions[planet]['longitude']
           lon2 = chart2_positions[planet]['longitude']
           
           # Orta nokta hesaplama (kısa yay yöntemi)
           diff = (lon2 - lon1) % 360
           if diff > 180:
               diff = diff - 360
           
           midpoint = (lon1 + diff/2) % 360
           
           # Burcunu hesapla
           sign_num = (int(midpoint / 30) % 12) + 1
           sign_degree = midpoint % 30
           
           # Kompozit pozisyona ekle
           composite_positions[planet] = {
               'longitude': midpoint,
               'sign_num': sign_num,
               'degree_in_sign': sign_degree,
               'is_composite': True  # Bu bir kompozit hesaplama
           }
       
       return composite_positions
   
    def calculate_lunar_return(self, birth_chart_id, target_date=None):
       """
       Ay dönüşü (lunar return) haritasını hesaplar.
       
       Args:
           birth_chart_id (int): Doğum haritasının ID'si
           target_date (datetime.date, optional): Hedef tarih (None ise bugün)
           
       Returns:
           dict: Ay dönüşü haritası bilgileri
       """
       try:
           birth_chart = BirthChart.objects.get(id=birth_chart_id)
       except BirthChart.DoesNotExist:
           return None
       
       # Hedef tarihi belirle
       if target_date is None:
           target_date = datetime.date.today()
       
       # Ay dönüşü tarihini hesapla
       lunar_return_datetime = self.ephemeris_calculator.calculate_lunar_return(
           birth_chart.birth_date, 
           birth_chart.birth_time, 
           birth_chart.birth_latitude, 
           birth_chart.birth_longitude, 
           target_date
       )
       
       # Sonuçları ayrıştır
       lunar_return_date = lunar_return_datetime.date()
       lunar_return_time = lunar_return_datetime.time()
       
       # Ay dönüşü haritasını hesapla (doğum yeri için)
       lunar_positions = self.ephemeris_calculator.calculate_planet_positions(
           lunar_return_date, 
           lunar_return_time, 
           birth_chart.birth_latitude, 
           birth_chart.birth_longitude
       )
       
       # Ay dönüşü evlerini hesapla
       lunar_houses = self.house_calculator.calculate_houses_placidus(
           lunar_return_date, 
           lunar_return_time, 
           birth_chart.birth_latitude, 
           birth_chart.birth_longitude
       )
       
       # Ay dönüşü açılarını hesapla
       lunar_aspects = self.aspect_calculator.calculate_aspects(lunar_positions)
       
       # Sonuç sözlüğü oluştur
       result = {
           'birth_chart_id': birth_chart_id,
           'birth_chart_name': birth_chart.name,
           'lunar_return_date': lunar_return_date,
           'lunar_return_time': lunar_return_time,
           'positions': lunar_positions,
           'houses': lunar_houses,
           'aspects': lunar_aspects
       }
       
       return result