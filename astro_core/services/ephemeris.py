# astro_core/services/ephemeris.py

import logging
from skyfield.api import load, Topos
from skyfield.units import Angle
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
import datetime
import pytz
import math
import os
import numpy as np
from skyfield.searchlib import find_maxima, find_minima
from skyfield.nutationlib import iau2000b
#from skyfield.positionlib import ICRS_to_J2000

# Loglama yapılandırması
logger = logging.getLogger(__name__)

class EphemerisCalculator:
    def __init__(self):
        # Skyfield veri dosyaları için dizin
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Gezegen verilerini yükle - hassas DE440 verileri, yoksa indir
        self.eph_file = os.path.join(data_dir, 'de440s.bsp')
        if not os.path.exists(self.eph_file):
            print("Ephemeris verileri indiriliyor... Bu işlem biraz zaman alabilir.")
            self.planets = load('de440s.bsp')
            print("Ephemeris verileri indirildi.")
        else:
            self.planets = load(self.eph_file)
        
        # Zaman ölçeği yükle
        self.ts = load.timescale()
        self.earth = self.planets['earth']
        
        # Gezegen referansları - standart gezegenler ve astrolojik noktalar
        self.planet_objects = {
            'sun': self.planets['sun'],
            'moon': self.planets['moon'],
            'mercury': self.planets['mercury barycenter'],
            'venus': self.planets['venus barycenter'],
            'mars': self.planets['mars barycenter'],
            'jupiter': self.planets['jupiter barycenter'],
            'saturn': self.planets['saturn barycenter'],
            'uranus': self.planets['uranus barycenter'],
            'neptune': self.planets['neptune barycenter'],
            'pluto': self.planets['pluto barycenter']
        }
        
        # Burç bilgileri (ID'ler 1'den başlar)
        self.zodiac_signs = {
            1: {'name_tr': 'Koç', 'name_en': 'Aries', 'symbol': '♈', 'element': 'fire', 'modality': 'cardinal'},
            2: {'name_tr': 'Boğa', 'name_en': 'Taurus', 'symbol': '♉', 'element': 'earth', 'modality': 'fixed'},
            3: {'name_tr': 'İkizler', 'name_en': 'Gemini', 'symbol': '♊', 'element': 'air', 'modality': 'mutable'},
            4: {'name_tr': 'Yengeç', 'name_en': 'Cancer', 'symbol': '♋', 'element': 'water', 'modality': 'cardinal'},
            5: {'name_tr': 'Aslan', 'name_en': 'Leo', 'symbol': '♌', 'element': 'fire', 'modality': 'fixed'},
            6: {'name_tr': 'Başak', 'name_en': 'Virgo', 'symbol': '♍', 'element': 'earth', 'modality': 'mutable'},
            7: {'name_tr': 'Terazi', 'name_en': 'Libra', 'symbol': '♎', 'element': 'air', 'modality': 'cardinal'},
            8: {'name_tr': 'Akrep', 'name_en': 'Scorpio', 'symbol': '♏', 'element': 'water', 'modality': 'fixed'},
            9: {'name_tr': 'Yay', 'name_en': 'Sagittarius', 'symbol': '♐', 'element': 'fire', 'modality': 'mutable'},
            10: {'name_tr': 'Oğlak', 'name_en': 'Capricorn', 'symbol': '♑', 'element': 'earth', 'modality': 'cardinal'},
            11: {'name_tr': 'Kova', 'name_en': 'Aquarius', 'symbol': '♒', 'element': 'air', 'modality': 'fixed'},
            12: {'name_tr': 'Balık', 'name_en': 'Pisces', 'symbol': '♓', 'element': 'water', 'modality': 'mutable'}
        }
        
        # Gezegenler için hız ortalamaları (günlük hareket, derece)
        self.planet_average_speeds = {
            'sun': 1.0,
            'moon': 13.2,
            'mercury': 1.4,
            'venus': 1.2,
            'mars': 0.5,
            'jupiter': 0.08,
            'saturn': 0.03,
            'uranus': 0.01,
            'neptune': 0.006,
            'pluto': 0.004
        }
    
    def calculate_planet_positions(self, birth_date, birth_time, latitude, longitude):
        """
        Belirli bir doğum tarihi, saati ve konumu için gezegen konumlarını ve astrolojik noktaları hesaplar
        
        Args:
            birth_date (datetime.date): Doğum tarihi
            birth_time (datetime.time): Doğum saati
            latitude (float): Enlem derecesi
            longitude (float): Boylam derecesi
            
        Returns:
            dict: Gezegen konumları ve burç pozisyonları
        """
        # Yerel zamanı doğru zaman dilimine çevir
        local_tz = self._get_timezone_from_coordinates(longitude, latitude)
        local_datetime = datetime.datetime.combine(birth_date, birth_time)
        
        # Python 3.6 için uyumluluk kontrolü
        if hasattr(local_tz, 'localize'):
            local_datetime = local_tz.localize(local_datetime)
        else:
            local_datetime = local_datetime.replace(tzinfo=local_tz)
        
        utc_datetime = local_datetime.astimezone(pytz.UTC)
        
        # GAST (Greenwich Apparent Sidereal Time) hesaplaması için UTC
        utc_year = utc_datetime.year
        utc_month = utc_datetime.month
        utc_day = utc_datetime.day
        utc_hour = utc_datetime.hour
        utc_minute = utc_datetime.minute
        utc_second = utc_datetime.second
        
        # Skyfield zaman nesnesini oluştur
        t = self.ts.utc(utc_year, utc_month, utc_day, utc_hour, utc_minute, utc_second)
        
        # Gözlemci konumunu belirle
        observer = self.earth + Topos(latitude_degrees=latitude, longitude_degrees=longitude)
        
        # GAST (Greenwich Apparent Sidereal Time) hesapla
        gast = t.gast  # Saat cinsinden
        
        # RAMC (Right Ascension Medium Coeli) hesapla
        ramc = (gast * 15.0 + longitude) % 360  # 15 derece/saat çevirimi
        
        # Ekliptik eğimi (obliquity) hesapla - J2000 standart değeri
        # Daha hassas hesaplama için t.tt (Terrestrial Time) kullanılarak dinamik hesaplanabilir
        try:
            # Skyfield 1.53 için uyumlu yöntem
            from skyfield.elementslib import osculating_elements_of

            # Dünya'nın ekliptik eğimini hesapla
            earth_orbit = osculating_elements_of(self.earth.at(t))
            obliquity_degrees = earth_orbit.inclination.degrees
        except Exception as e:
            # Fallback: J2000 standart obliquity değeri
            logger.warning(f"Ekliptik eğimi hesaplanamadı, varsayılan değer kullanılıyor: {e}")
            obliquity_degrees = 23.4392811

        obliquity = math.radians(obliquity_degrees)        
        
        # Gezegen konumlarını hesapla
        results = {}
        
        # Retrograde hesaplaması için zaman aralıkları (günler)
        time_delta = 1.0  # 1 gün öncesi ve sonrası
        
        # Retrograde hesaplama için zaman nesnelerini oluştur
        t_before = self.ts.utc(utc_year, utc_month, utc_day, utc_hour, utc_minute, utc_second - time_delta * 24 * 60 * 60)
        t_after = self.ts.utc(utc_year, utc_month, utc_day, utc_hour, utc_minute, utc_second + time_delta * 24 * 60 * 60)
        
        for planet_name, planet_obj in self.planet_objects.items():
            # Gezegenin gözlemciye göre konumunu hesapla
            astrometric = observer.at(t).observe(planet_obj)
            
            # Ekliptik koordinatlarını al (burç hesaplaması için)
            # Skyfield 1.53 ile uyumlu hale getirme
            apparent = astrometric.apparent()
            ecliptic = apparent.ecliptic_latlon(epoch='date')
            
            # Ekliptik boylam (burç derecesi) ve enlem
            lon = ecliptic[1].degrees
            lat = ecliptic[0].degrees
            
            # Burcun hesaplanması (1-12 arası burç numarası)
            zodiac_sign_num = int(lon / 30) % 12 + 1  # 1=Koç, 2=Boğa, vb.
            zodiac_degree = lon % 30
            
            # Retrograde durumunu hesapla
            is_retrograde = False
            daily_motion = 0.0
            
            if planet_name != 'sun':  # Astrolojide Güneş retrograde kabul edilmez
                # Bir gün önceki ve sonraki konumu hesapla
                astrometric_before = observer.at(t_before).observe(planet_obj)
                astrometric_after = observer.at(t_after).observe(planet_obj)
                
                # Skyfield 1.53 ile uyumlu hale getirme
                apparent_before = astrometric_before.apparent()
                ecliptic_before = apparent_before.ecliptic_latlon(epoch='date')
                
                apparent_after = astrometric_after.apparent()
                ecliptic_after = apparent_after.ecliptic_latlon(epoch='date')
                
                lon_before = ecliptic_before[1].degrees
                lon_after = ecliptic_after[1].degrees
                
                # Normal hareket doğu yönünde (artan boylam), retrograde batı yönünde (azalan boylam)
                # Burç sınırlarındaki 360-0 geçişlerini ele almak için özel kontrol
                if abs(lon_after - lon_before) > 180:
                    # 360-0 geçişi var
                    if lon_before > 270 and lon_after < 90:
                        # Doğuya doğru 360-0 geçişi
                        daily_motion = (lon_after + 360 - lon_before) / (2 * time_delta)
                    else:
                        # Batıya doğru 0-360 geçişi
                        daily_motion = (lon_after - lon_before - 360) / (2 * time_delta)
                else:
                    daily_motion = (lon_after - lon_before) / (2 * time_delta)
                
                is_retrograde = daily_motion < 0
            
            # Retrograde değilse ve Güneş veya Ay ise ortalama hızını kullan
            if not is_retrograde and (planet_name == 'sun' or planet_name == 'moon'):
                daily_motion = self.planet_average_speeds[planet_name]
            
            # Burç bilgilerini ekle
            sign_info = self.zodiac_signs[zodiac_sign_num]
            
            # Deklinasyon hesapla (gezegen gökyüzündeki "yükseklik" açısı)
            # Bu, ev hesaplamaları ve diğer analizler için faydalıdır
            apparent = astrometric.apparent()
            dec = apparent.altaz()[0].degrees
            
            # Sağ Açıklık (Right Ascension) hesapla
            ra = apparent.radec(epoch='date')[0].hours
            
            results[planet_name] = {
                'longitude': lon,
                'latitude': lat,
                'declination': dec,
                'right_ascension': ra * 15,  # Saati dereceye çevir (15 derece/saat)
                'sign_num': zodiac_sign_num,
                'sign_name_tr': sign_info['name_tr'],
                'sign_name_en': sign_info['name_en'],
                'sign_symbol': sign_info['symbol'],
                'sign_element': sign_info['element'],
                'sign_modality': sign_info['modality'],
                'degree_in_sign': zodiac_degree,
                'is_retrograde': is_retrograde,
                'speed': abs(daily_motion),
                'daily_motion': daily_motion
            }
        
        # Kuzey Ay Düğümü (North Node) hesaplama
        # Gerçek hesaplama: Ay'ın yörüngesinin ekliptik ile kesişimi
        
        # Ay'ın yörünge düzleminin normal vektörünü hesapla
        # Bu, Ay'ın gerçek anndaki konumu ve hızından elde edilebilir
        
        # 1. Ay'ın ICRS (International Celestial Reference System) koordinatlarını al
        try:
            moon_pos_t = self.earth.at(t).observe(self.planets['moon']).position.au
            moon_pos_before = self.earth.at(t_before).observe(self.planets['moon']).position.au
            moon_pos_after = self.earth.at(t_after).observe(self.planets['moon']).position.au

            # Ay'ın hızını hesapla
            moon_velocity = (moon_pos_after - moon_pos_before) / (2 * time_delta * 86400)  # saniyeye çevir

            # Ay'ın yörünge düzleminin normal vektörünü hesapla
            moon_normal = np.cross(moon_pos_t, moon_velocity)

            # Ekliptik düzlemi normal vektörü [0, 0, 1]
            ecliptic_normal = np.array([0, 0, 1])


            # İki düzlemin kesişim çizgisi hesapla
            intersection_line = np.cross(moon_normal, ecliptic_normal)

            # Normalizasyon
            intersection_line = intersection_line / np.linalg.norm(intersection_line)

            # Kuzey Ay Düğümü'nün yönünü belirle
            sun_pos = self.earth.at(t).observe(self.planets['sun']).position.au
            sun_dir = sun_pos / np.linalg.norm(sun_pos)


            # İki olası kesişim yönü vardır: Kuzey ve Güney
            dot_product = np.dot(intersection_line, sun_dir)
            if dot_product < 0:
                intersection_line = -intersection_line

            # Boylam hesaplaması
            north_node_lon = math.degrees(math.atan2(intersection_line[1], intersection_line[0]))
            north_node_lon = (north_node_lon + 360) % 360

            # 9. Burcun hesaplanması
            north_node_sign_num = int(north_node_lon / 30) % 12 + 1
            north_node_sign_info = self.zodiac_signs[north_node_sign_num]


            # North Node verisini ekle
            results['north_node'] = {
                'longitude': north_node_lon,
                'sign_num': north_node_sign_num,
                'sign_name_tr': north_node_sign_info['name_tr'],
                'sign_name_en': north_node_sign_info['name_en'],
                'sign_symbol': north_node_sign_info['symbol'],
                'degree_in_sign': north_node_lon % 30,
                'is_retrograde': True  # Ay Düğümleri her zaman retrograde hareket eder
            }


            # South Node (Güney Ay Düğümü) - North Node'un tam karşısı
            south_node_lon = (north_node_lon + 180) % 360
            south_node_sign_num = int(south_node_lon / 30) % 12 + 1
            south_node_sign_info = self.zodiac_signs[south_node_sign_num]

            results['south_node'] = {
                'longitude': south_node_lon,
                'sign_num': south_node_sign_num,
                'sign_name_tr': south_node_sign_info['name_tr'],
                'sign_name_en': south_node_sign_info['name_en'],
                'sign_symbol': south_node_sign_info['symbol'],
                'degree_in_sign': south_node_lon % 30,
                'is_retrograde': True  # Ay Düğümleri her zaman retrograde hareket eder
            }

        except Exception as e:
            logger.warning(f"Ay Düğümü hesaplanamadı: {e}")
            # Ay Düğümleri hesaplanamadığında, sonuçlara eklemiyoruz
            # veya varsayılan bir değer kullanabilirsiniz
            results['north_node'] = {
                'longitude': 0,
                'sign_num': 1,
                'sign_name_tr': 'Koç',
                'sign_name_en': 'Aries',
                'sign_symbol': '♈',
                'degree_in_sign': 0,
                'is_retrograde': True,
                'is_estimated': True  # Bu, tahmini bir değer olduğunu gösterir
            }
    
            results['south_node'] = {
                'longitude': 180,
                'sign_num': 7,
                'sign_name_tr': 'Terazi',
                'sign_name_en': 'Libra',
                'sign_symbol': '♎',
                'degree_in_sign': 0,
                'is_retrograde': True,
                'is_estimated': True  # Bu, tahmini bir değer olduğunu gösterir
            }

        
        # Yükselen (Ascendant) hesaplama
        # Formül: arctan(sin(RAMC) / (cos(RAMC) * cos(obliquity) - tan(latitude) * sin(obliquity)))
        ramc_rad = math.radians(ramc)
        obliquity_rad = math.radians(obliquity_degrees)
        latitude_rad = math.radians(latitude)
        
        tan_asc = math.sin(ramc_rad) / (math.cos(ramc_rad) * math.cos(obliquity_rad) - 
                                      math.tan(latitude_rad) * math.sin(obliquity_rad))
        asc_longitude = math.degrees(math.atan(tan_asc))
        
        # Açıyı doğru kadrana getir
        if math.cos(ramc_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
            asc_longitude += 180
        
        # Açıyı 0-360 aralığına getir
        asc_longitude = (asc_longitude + 360) % 360
        
        # Yükselen burcu hesapla
        asc_sign_num = int(asc_longitude / 30) % 12 + 1
        asc_sign_info = self.zodiac_signs[asc_sign_num]
        
        # Yükselen noktasını sonuçlara ekle
        results['ascendant'] = {
            'longitude': asc_longitude,
            'sign_num': asc_sign_num,
            'sign_name_tr': asc_sign_info['name_tr'],
            'sign_name_en': asc_sign_info['name_en'],
            'sign_symbol': asc_sign_info['symbol'],
            'degree_in_sign': asc_longitude % 30
        }
        
        # MC (Medium Coeli - Midheaven) hesaplama
        # MC, RAMC'nin ekliptik koordinatlarıdır
        mc_longitude = ramc
        mc_sign_num = int(mc_longitude / 30) % 12 + 1
        mc_sign_info = self.zodiac_signs[mc_sign_num]
        
        # MC noktasını sonuçlara ekle
        results['mc'] = {
            'longitude': mc_longitude,
            'sign_num': mc_sign_num,
            'sign_name_tr': mc_sign_info['name_tr'],
            'sign_name_en': mc_sign_info['name_en'],
            'sign_symbol': mc_sign_info['symbol'],
            'degree_in_sign': mc_longitude % 30
        }
        
        # Part of Fortune hesaplama
        # Formül: ASC + Moon - Sun (gündüz doğumu)
        # Formül: ASC + Sun - Moon (gece doğumu)
        sun_longitude = results['sun']['longitude']
        moon_longitude = results['moon']['longitude']
        
        # Gündüz/gece doğumu kontrol et
        # Güneş MC ile ASC arasında (günün ilk yarısı) veya
        # Güneş IC ile DSC arasında (günün ikinci yarısı) ise gündüz doğumudur
        mc_longitude = results['mc']['longitude']
        asc_longitude = results['ascendant']['longitude']
        ic_longitude = (mc_longitude + 180) % 360
        dsc_longitude = (asc_longitude + 180) % 360
        
        # Güneş'in MC-ASC veya IC-DSC arasında olup olmadığını kontrol et
        # Not: Bu, açıların 0-360 aralığında olduğunu varsayar
        is_daytime = False
        
        # MC-ASC arasını kontrol et
        if mc_longitude <= asc_longitude:
            is_daytime = mc_longitude <= sun_longitude <= asc_longitude
        else:  # MC>ASC durumu (0 dereceden geçiş var)
            is_daytime = sun_longitude >= mc_longitude or sun_longitude <= asc_longitude
        
        # IC-DSC arasını kontrol et
        if not is_daytime:
            if ic_longitude <= dsc_longitude:
                is_daytime = ic_longitude <= sun_longitude <= dsc_longitude
            else:  # IC>DSC durumu (0 dereceden geçiş var)
                is_daytime = sun_longitude >= ic_longitude or sun_longitude <= dsc_longitude
        
        # Part of Fortune hesapla
        if is_daytime:
            fortune_longitude = (asc_longitude + moon_longitude - sun_longitude) % 360
        else:
            fortune_longitude = (asc_longitude + sun_longitude - moon_longitude) % 360
        
        fortune_sign_num = int(fortune_longitude / 30) % 12 + 1
        fortune_sign_info = self.zodiac_signs[fortune_sign_num]
        
        # Part of Fortune'u sonuçlara ekle
        results['part_of_fortune'] = {
            'longitude': fortune_longitude,
            'sign_num': fortune_sign_num,
            'sign_name_tr': fortune_sign_info['name_tr'],
            'sign_name_en': fortune_sign_info['name_en'],
            'sign_symbol': fortune_sign_info['symbol'],
            'degree_in_sign': fortune_longitude % 30,
            'is_daytime_formula': is_daytime
        }
        
        # RAMC değerini ekleyelim (ev hesaplamaları için)
        results['ramc'] = ramc
        results['obliquity'] = obliquity_degrees
        
        return results
    
    def _get_timezone_from_coordinates(self, longitude, latitude):
        """
        Coğrafi koordinatlara göre en yakın zaman dilimini belirler
        
        Args:
            longitude (float): Boylam
            latitude (float): Enlem
            
        Returns:
            pytz.timezone: Zaman dilimi nesnesi
        """
        # Yaklaşık zaman dilimi hesaplama (UTC)
        # Her 15 derece boylam 1 saatlik zaman farkıdır
        utc_offset = round(longitude / 15)
        
        # Basitleştirilmiş yaklaşım: En yakın tam saatlik zaman dilimini kullan
        if utc_offset > 0:
            tz_name = f"Etc/GMT-{utc_offset}"  # Dikkat: pytz'de pozitif offset için negatif kullanılır
        elif utc_offset < 0:
            tz_name = f"Etc/GMT+{abs(utc_offset)}"  # Negatif offset için pozitif kullanılır
        else:
            tz_name = "Etc/GMT"  # UTC
        
        try:
            return pytz.timezone(tz_name)
        except pytz.exceptions.UnknownTimeZoneError:
            # Hata durumunda UTC kullan
            return pytz.UTC
    
    def calculate_lunar_phase(self, birth_date, birth_time, latitude, longitude):
        """
        Ay fazını hesaplar
        
        Args:
            birth_date (datetime.date): Doğum tarihi
            birth_time (datetime.time): Doğum saati
            latitude (float): Enlem derecesi
            longitude (float): Boylam derecesi
            
        Returns:
            dict: Ay fazı bilgileri
        """
        # Gezegen pozisyonlarını al
        planet_positions = self.calculate_planet_positions(birth_date, birth_time, latitude, longitude)
        
        # Güneş ve Ay konumları
        sun_longitude = planet_positions['sun']['longitude']
        moon_longitude = planet_positions['moon']['longitude']
        
        # Ay fazı açısı (Ay-Güneş arası açı)
        lunar_phase_angle = (moon_longitude - sun_longitude) % 360
        
        # Ay fazı yüzdesi (0: Yeni Ay, 50: İlk/Son Dördün, 100: Dolunay)
        if lunar_phase_angle <= 180:
            phase_percent = lunar_phase_angle / 180 * 100
        else:
            phase_percent = (360 - lunar_phase_angle) / 180 * 100
        
        # Ay fazı adı
        if 0 <= lunar_phase_angle < 45:
            phase_name_tr = "Yeni Ay"
            phase_name_en = "New Moon"
        elif 45 <= lunar_phase_angle < 90:
            phase_name_tr = "Hilal"
            phase_name_en = "Waxing Crescent"
        elif 90 <= lunar_phase_angle < 135:
            phase_name_tr = "İlk Dördün"
            phase_name_en = "First Quarter"
        elif 135 <= lunar_phase_angle < 180:
            phase_name_tr = "Şişkin Ay"
            phase_name_en = "Waxing Gibbous"
        elif 180 <= lunar_phase_angle < 225:
            phase_name_tr = "Dolunay"
            phase_name_en = "Full Moon"
        elif 225 <= lunar_phase_angle < 270:
            phase_name_tr = "Küçülen Ay"
            phase_name_en = "Waning Gibbous"
        elif 270 <= lunar_phase_angle < 315:
            phase_name_tr = "Son Dördün"
            phase_name_en = "Last Quarter"
        else:
            phase_name_tr = "Hilal (Küçülen)"
            phase_name_en = "Waning Crescent"
        
        return {
            'angle': lunar_phase_angle,
            'percent': phase_percent,
            'phase_name_tr': phase_name_tr,
            'phase_name_en': phase_name_en,
            'is_waxing': lunar_phase_angle <= 180,  # Büyüyen ay
            'is_waning': lunar_phase_angle > 180,   # Küçülen ay
        }
    
    def find_next_lunar_phase(self, start_date, target_phase="full_moon"):
        """
        Belirli bir tarihten sonraki ilk belirli Ay fazını bulur
    
        Args:
            start_date (datetime.date): Başlangıç tarihi
            target_phase (str): Hedef faz (new_moon, first_quarter, full_moon, last_quarter)
        
        Returns:
            datetime.datetime: Hedef fazın tarihi ve saati
        """
        # Başlangıç tarihini UTC olarak ayarla
        start_datetime = datetime.datetime.combine(start_date, datetime.time(0, 0, 0))
        start_datetime = pytz.UTC.localize(start_datetime)
    
        # Skyfield zaman nesnesi oluştur
        t0 = self.ts.from_datetime(start_datetime)
    
        # İki haftalık bir zaman dilimi (yeterli olmalı)
        t1 = self.ts.from_datetime(start_datetime + datetime.timedelta(days=30))
    
        # Hedef faza göre işlevi belirle
        earth, sun, moon = self.earth, self.planets['sun'], self.planets['moon']
    
        if target_phase == "new_moon":
            # Yeni Ay: Ay ve Güneş aynı yönde
            def elongation_at_time(t):
                e = earth.at(t)
                s = e.observe(sun).apparent()
                m = e.observe(moon).apparent()
                return s.separation_from(m).degrees
        
            times, elongations = find_minima(t0, t1, elongation_at_time, 0.5)
        
        elif target_phase == "full_moon":
            # Dolunay: Ay ve Güneş zıt yönlerde
            def elongation_at_time(t):
                e = earth.at(t)
                s = e.observe(sun).apparent()
                m = e.observe(moon).apparent()
                return 180 - s.separation_from(m).degrees
        
            times, elongations = find_minima(t0, t1, elongation_at_time, 0.5)
        
        elif target_phase == "first_quarter" or target_phase == "last_quarter":
            # İlk ve Son Dördün: Ay ve Güneş 90 derece açıda
            def elongation_at_time(t):
                e = earth.at(t)
                s = e.observe(sun).apparent()
                m = e.observe(moon).apparent()
                separation = s.separation_from(m).degrees
                return abs(separation - 90)
        
            times, elongations = find_minima(t0, t1, elongation_at_time, 0.5)
        
            # Birden fazla sonuç varsa, doğru çeyreği seç
        if len(times) > 1:
            # İlk ve Son Dördünü ayırt et
            for i, t in enumerate(times):
                e = earth.at(t)
                s = e.observe(sun).apparent()
                m = e.observe(moon).apparent()
                
                # Ekliptik boylamları hesapla
                # Skyfield 1.53 ile uyumlu hale getirme
                s_apparent = s.apparent()
                s_ecliptic = s_apparent.ecliptic_latlon(epoch='date')
                s_lon = s_ecliptic[1].degrees
                
                m_apparent = m.apparent()
                m_ecliptic = m_apparent.ecliptic_latlon(epoch='date')
                m_lon = m_ecliptic[1].degrees
                
                # Ay-Güneş açısı
                angle = (m_lon - s_lon) % 360
                
                if target_phase == "first_quarter" and 45 <= angle <= 135:
                    return t.utc_datetime()
                elif target_phase == "last_quarter" and (angle >= 225 and angle <= 315):
                    return t.utc_datetime()
    
            # Sonuç yoksa None döndür
        if len(times) == 0:
            return None
    
        # İlk sonucu döndür
        return times[0].utc_datetime()
    
    def calculate_solar_return(self, birth_date, year):
        """
        Belirli bir yıl için güneş dönüşü (solar return) tarihini hesaplar
        
        Args:
            birth_date (datetime.date): Doğum tarihi
            year (int): Güneş dönüşü hesaplanacak yıl
            
        Returns:
            datetime.datetime: Güneş dönüşü tarihi ve saati
        """
        # Doğum tarihindeki güneş konumunu hesapla
        birth_datetime = datetime.datetime.combine(birth_date, datetime.time(12, 0, 0))  # Öğlen UTC
        birth_datetime = pytz.UTC.localize(birth_datetime)
        
        t_birth = self.ts.from_datetime(birth_datetime)
        e_birth = self.earth.at(t_birth)
        # Skyfield 1.53 ile uyumlu hale getirme
        sun_birth_obj = e_birth.observe(self.planets['sun'])
        sun_birth_app = sun_birth_obj.apparent()
        sun_birth = sun_birth_app.ecliptic_latlon(epoch='date')
        birth_sun_lon = sun_birth[1].degrees
        
        # Hedef yılın başlangıcını ve sonunu belirle
        year_start = datetime.datetime(year, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        year_end = datetime.datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        
        # Doğum günü civarını hedefle (daha verimli)
        target_month = birth_date.month
        target_day = birth_date.day
        
        # Tahmini solar return tarihi
        estimated_date = datetime.datetime(year, target_month, min(target_day, 28), 12, 0, 0, tzinfo=pytz.UTC)
        
        # Önce/sonra 7 gün aralığını kontrol et
        start_time = max(year_start, estimated_date - datetime.timedelta(days=7))
        end_time = min(year_end, estimated_date + datetime.timedelta(days=7))
        
        t0 = self.ts.from_datetime(start_time)
        t1 = self.ts.from_datetime(end_time)
        
        # Güneş konumu ve hedef konum arasındaki farkı minimize ederek güneş dönüşünü bul
        def sun_lon_diff(t):
            e = self.earth.at(t)
            # Skyfield 1.53 ile uyumlu hale getirme
            sun_pos_obj = e.observe(self.planets['sun'])
            sun_pos_app = sun_pos_obj.apparent()
            sun_pos = sun_pos_app.ecliptic_latlon(epoch='date')
            sun_lon = sun_pos[1].degrees
            diff = abs((sun_lon - birth_sun_lon) % 360)
            if diff > 180:
                diff = 360 - diff
            return diff
        
        # En yakın noktaları bul
        times, _ = find_minima(t0, t1, sun_lon_diff, 1.0/24)  # 1 saatlik hassasiyet
        
        if not times:
            # Arama aralığını genişlet
            t0 = self.ts.from_datetime(estimated_date - datetime.timedelta(days=30))
            t1 = self.ts.from_datetime(estimated_date + datetime.timedelta(days=30))
            times, _ = find_minima(t0, t1, sun_lon_diff, 1.0/24)
        
        if times:
            return times[0].utc_datetime()
        else:
            # Hesaplama başarısız olursa yaklaşık değeri döndür
            return estimated_date
            
    def calculate_lunar_return(self, birth_date, birth_time, latitude, longitude, target_date):
        """
        Belirli bir tarih civarında ay dönüşü (lunar return) tarihini hesaplar
        
        Args:
            birth_date (datetime.date): Doğum tarihi
            birth_time (datetime.time): Doğum saati
            latitude (float): Doğum yeri enlemi
            longitude (float): Doğum yeri boylamı
            target_date (datetime.date): Hedef tarih (ay dönüşünün aranacağı tarih)
            
        Returns:
            datetime.datetime: Ay dönüşü tarihi ve saati
        """
        # Doğum anındaki ay konumunu hesapla
        birth_positions = self.calculate_planet_positions(birth_date, birth_time, latitude, longitude)
        birth_moon_lon = birth_positions['moon']['longitude']
        
        # Hedef tarihin başlangıcını ve yaklaşık bir ay sonrasını belirle
        target_datetime = datetime.datetime.combine(target_date, datetime.time(0, 0, 0))
        target_datetime = pytz.UTC.localize(target_datetime)
        
        # Ay dönüşü genellikle 27-29 gün arasında gerçekleşir (siderik ay dönüşü ~27.3 gün)
        search_start = target_datetime - datetime.timedelta(days=3)  # Birkaç gün önce başla
        search_end = target_datetime + datetime.timedelta(days=33)   # Yaklaşık bir ay sonra bitir
        
        t0 = self.ts.from_datetime(search_start)
        t1 = self.ts.from_datetime(search_end)
        
        # Ay konumu ve hedef konum arasındaki farkı minimize ederek ay dönüşünü bul
        def moon_lon_diff(t):
            # Verilen t anında Ay'ın konumunu hesapla
            e = self.earth.at(t)
            # Skyfield 1.53 ile uyumlu hale getirme
            moon_pos_obj = e.observe(self.planets['moon'])
            moon_pos_app = moon_pos_obj.apparent()
            moon_pos = moon_pos_app.ecliptic_latlon(epoch='date')
            moon_lon = moon_pos[1].degrees
            
            # Doğum anındaki Ay konumu ile farkını hesapla
            diff = abs((moon_lon - birth_moon_lon) % 360)
            if diff > 180:
                diff = 360 - diff
                
            return diff
        
        # En yakın noktaları bul (her 60 dakikada bir kontrol et)
        times, _ = find_minima(t0, t1, moon_lon_diff, 1.0/24)
        
        if not times:
            # Arama aralığını genişlet veya hassasiyeti azalt
            times, _ = find_minima(t0, t1, moon_lon_diff, 1.0/12)  # 2 saatlik hassasiyet
        
        if times:
            # Ay dönüşü tarihini döndür
            return times[0].utc_datetime()
        else:
            # Hesaplama başarısız olursa hedef tarihi döndür
            return target_datetime
    
    def calculate_progressions(self, birth_date, birth_time, latitude, longitude, target_date):
        """
        Belirli bir tarih için ilerlemiş (progressed) gezegen konumlarını hesaplar
        
        Args:
            birth_date (datetime.date): Doğum tarihi
            birth_time (datetime.time): Doğum saati
            latitude (float): Doğum yeri enlemi
            longitude (float): Doğum yeri boylamı
            target_date (datetime.date): Hedef tarih (ilerlemelerin hesaplanacağı tarih)
            
        Returns:
            dict: İlerlemiş gezegen konumları
        """
        # Doğum tarihi ile hedef tarih arasındaki yıl farkını hesapla
        birth_datetime = datetime.datetime.combine(birth_date, birth_time)
        target_datetime = datetime.datetime.combine(target_date, birth_time)  # Aynı saati kullan
        
        # İkincil ilerleme: 1 gün = 1 yıl
        days_diff = (target_datetime - birth_datetime).days
        years_diff = days_diff / 365.25
        
        # İlerleme tarihini hesapla
        progression_datetime = birth_datetime + datetime.timedelta(days=days_diff)
        
        # İlerlemiş gezegen konumlarını hesapla
        # Burada, ilerleme tarihindeki gerçek gezegen konumlarını kullanıyoruz
        progression_date = progression_datetime.date()
        progression_time = progression_datetime.time()
        
        progressed_positions = self.calculate_planet_positions(
            progression_date, progression_time, latitude, longitude)
        
        # Sonuçlara ilerleme bilgilerini ekle
        for planet in progressed_positions:
            if isinstance(progressed_positions[planet], dict) and 'longitude' in progressed_positions[planet]:
                progressed_positions[planet]['progression_years'] = years_diff
        
        return progressed_positions
    
    def calculate_transits(self, birth_date, birth_time, latitude, longitude, transit_date, transit_time):
        """
        Doğum haritası üzerindeki transit gezegen konumlarını hesaplar
        
        Args:
            birth_date (datetime.date): Doğum tarihi
            birth_time (datetime.time): Doğum saati
            latitude (float): Doğum yeri enlemi
            longitude (float): Doğum yeri boylamı
            transit_date (datetime.date): Transit tarihi
            transit_time (datetime.time): Transit saati
            
        Returns:
            dict: Transit gezegen konumları ve doğum haritasıyla ilişkileri
        """
        # Doğum haritası gezegen konumlarını hesapla
        natal_positions = self.calculate_planet_positions(birth_date, birth_time, latitude, longitude)
        
        # Transit anındaki gezegen konumlarını hesapla
        transit_positions = self.calculate_planet_positions(transit_date, transit_time, latitude, longitude)
        
        # Transit-Natal açılarını hesapla
        transit_aspects = {}
        
        # Her bir transit gezegeni için
        for transit_planet in self.planet_objects.keys():
            # Transit gezegenin konumu
            if transit_planet not in transit_positions:
                continue
                
            transit_lon = transit_positions[transit_planet]['longitude']
            
            # Bu transit gezegenin doğum haritasındaki gezegenlerle açıları
            planet_aspects = []
            
            # Her bir natal gezegen için
            for natal_planet in self.planet_objects.keys():
                # Natal gezegenin konumu
                if natal_planet not in natal_positions:
                    continue
                    
                natal_lon = natal_positions[natal_planet]['longitude']
                
                # Açı farkını hesapla
                angle_diff = abs(transit_lon - natal_lon) % 360
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                
                # Açı tiplerini kontrol et
                for aspect_name, aspect_angle in [
                    ('conjunction', 0),   # Kavuşum: 0 derece
                    ('opposition', 180),  # Karşıt: 180 derece
                    ('trine', 120),       # Üçgen: 120 derece
                    ('square', 90),       # Kare: 90 derece
                    ('sextile', 60),      # Altmışlık: 60 derece
                ]:
                    # Açı toleransı (orb)
                    orb = 2.0  # 2 derecelik orb
                    
                    # Transit açıları için daha geniş orb kullanılabilir
                    if aspect_name == 'conjunction':  # Kavuşum
                        orb = 8.0
                    elif aspect_name in ['opposition', 'trine', 'square']:  # Karşıt, Üçgen, Kare
                        orb = 6.0
                    elif aspect_name == 'sextile':  # Altmışlık
                        orb = 4.0
                    
                    # Açı, beklenen değere orb değeri içinde yakınsa
                    if abs(angle_diff - aspect_angle) <= orb:
                        planet_aspects.append({
                            'natal_planet': natal_planet,
                            'aspect_type': aspect_name,
                            'orb': abs(angle_diff - aspect_angle)
                        })
            
            # Bu transit gezegen için açıları sonuçlara ekle
            transit_aspects[transit_planet] = planet_aspects
        
        # Sonuçları birleştir
        return {
            'natal_positions': natal_positions,
            'transit_positions': transit_positions,
            'transit_aspects': transit_aspects
        }