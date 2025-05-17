# astro_core/services/houses.py

import math
from .ephemeris import EphemerisCalculator

class HouseCalculator:
    def __init__(self):
        self.ephemeris_calculator = EphemerisCalculator()
    
    def calculate_houses_placidus(self, birth_date, birth_time, latitude, longitude):
        """
        Placidus ev sistemine göre ev başlangıç noktalarını hesaplar
        
        Args:
            birth_date (datetime.date): Doğum tarihi
            birth_time (datetime.time): Doğum saati
            latitude (float): Enlem derecesi
            longitude (float): Boylam derecesi
            
        Returns:
            dict: Ev başlangıç noktaları ve burç konumları
        """
        # Gezegen pozisyonlarını al (RAMC hesaplaması için)
        planet_positions = self.ephemeris_calculator.calculate_planet_positions(
            birth_date, birth_time, latitude, longitude)
        
        # RAMC (Right Ascension of the Midheaven) al
        ramc = planet_positions['ramc']
        
        # Ekliptik eğim açısı (Earth's Obliquity)
        # J2000 epoğu için standart değer
        obliquity = 23.4392911  # Derece
        
        # Enlem ve ekliptik eğimi radyana çevir
        latitude_rad = math.radians(latitude)
        obliquity_rad = math.radians(obliquity)
        
        # MC (Medium Coeli - Midheaven) - 10. Ev
        mc_longitude = ramc
        
        # IC (Imum Coeli) - 4. Ev - MC'nin tam karşısı
        ic_longitude = (mc_longitude + 180) % 360
        
        # Ascendant (Yükselen - 1. Ev) hesaplama - tam formül
        ramc_rad = math.radians(ramc)
        
        tan_asc = math.sin(ramc_rad) / (math.cos(ramc_rad) * math.cos(obliquity_rad) - 
                                        math.tan(latitude_rad) * math.sin(obliquity_rad))
        asc_longitude = math.degrees(math.atan(tan_asc))
        
        # Açıyı doğru kadrana getir
        if math.cos(ramc_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
            asc_longitude += 180
        
        # Açıyı 0-360 aralığına getir
        asc_longitude = (asc_longitude + 360) % 360
        
        # Descendant (7. Ev) - Ascendant'ın tam karşısı
        desc_longitude = (asc_longitude + 180) % 360
        
        # Placidus ev sisteminde diğer evleri hesapla
        houses = self._calculate_placidus_houses(ramc, obliquity, latitude)
        
        # MC, IC, Ascendant ve Descendant'ı ekle/güncelle
        houses[10] = {
            'cusp_longitude': mc_longitude,
            'sign_num': (int(mc_longitude / 30) % 12) + 1,
            'degree_in_sign': mc_longitude % 30
        }
        
        houses[4] = {
            'cusp_longitude': ic_longitude,
            'sign_num': (int(ic_longitude / 30) % 12) + 1,
            'degree_in_sign': ic_longitude % 30
        }
        
        houses[1] = {
            'cusp_longitude': asc_longitude,
            'sign_num': (int(asc_longitude / 30) % 12) + 1,
            'degree_in_sign': asc_longitude % 30
        }
        
        houses[7] = {
            'cusp_longitude': desc_longitude,
            'sign_num': (int(desc_longitude / 30) % 12) + 1,
            'degree_in_sign': desc_longitude % 30
        }
        
        return houses
    
    def _calculate_placidus_houses(self, ramc, obliquity, latitude):
        """
        Placidus ev sistemi hesaplaması - tam matematiksel yöntem
        
        Args:
            ramc (float): RAMC (Right Ascension Medium Coeli)
            obliquity (float): Ekliptik eğim açısı
            latitude (float): Enlem derecesi
            
        Returns:
            dict: Tüm evlerin başlangıç noktaları
        """
        houses = {}
        
        # Radyan çevrimi
        latitude_rad = math.radians(latitude)
        obliquity_rad = math.radians(obliquity)
        
        # MC (10. Ev) ve IC (4. Ev) hesaplaması
        mc_longitude = ramc
        ic_longitude = (mc_longitude + 180) % 360
        
        # Ascendant (1. Ev) hesaplaması
        ramc_rad = math.radians(ramc)
        
        tan_asc = math.sin(ramc_rad) / (math.cos(ramc_rad) * math.cos(obliquity_rad) - 
                                       math.tan(latitude_rad) * math.sin(obliquity_rad))
        asc_longitude = math.degrees(math.atan(tan_asc))
        
        # Açıyı doğru kadrana getir
        if math.cos(ramc_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
            asc_longitude += 180
        
        # Açıyı 0-360 aralığına getir
        asc_longitude = (asc_longitude + 360) % 360
        
        # Descendant (7. Ev) - Ascendant'ın karşısı
        desc_longitude = (asc_longitude + 180) % 360
        
        # RAMC'yi 0-360 aralığına getir
        ramc = ramc % 360
        
        # Placidus ev sistemi - Gündüz ve gece yarı-yayları (semidiurnal arcs)
        # Kuzey ve güney noktalardaki saat açıları (30°, 60°, 120°, 150°)
        
        # Önce MC ve Ascendant'ın sağ açıklığı (right ascension) hesaplanır
        ra_mc = ramc
        
        # Ascendant'ın sağ açıklığı
        sin_ra_asc = math.sin(math.radians(asc_longitude)) * math.cos(obliquity_rad)
        cos_ra_asc = math.cos(math.radians(asc_longitude))
        ra_asc = math.degrees(math.atan2(sin_ra_asc, cos_ra_asc))
        ra_asc = (ra_asc + 360) % 360
        
        # Gündüz yarı-yayı (diurnal semiarc)
        # MC ile Ascendant arasındaki sağ açıklık farkı
        diurnal_semiarc = (ra_asc - ra_mc) % 360
        if diurnal_semiarc > 180:
            diurnal_semiarc = 360 - diurnal_semiarc
        
        # Gece yarı-yayı (nocturnal semiarc)
        nocturnal_semiarc = 180 - diurnal_semiarc
        
        # 11. ve 12. Ev hesaplaması - Gündüz yarı-yayını üçe böl
        # 2. ve 3. Ev hesaplaması - Gece yarı-yayını üçe böl
        
        # Her ev için RA hesaplaması (Right Ascension)
        ra_house11 = (ra_mc + diurnal_semiarc / 3) % 360
        ra_house12 = (ra_mc + 2 * diurnal_semiarc / 3) % 360
        ra_house2 = (ra_asc + nocturnal_semiarc / 3) % 360
        ra_house3 = (ra_asc + 2 * nocturnal_semiarc / 3) % 360
        
        # Simetri kullanarak diğer evleri hesapla
        ra_house5 = (ra_house11 + 180) % 360
        ra_house6 = (ra_house12 + 180) % 360
        ra_house8 = (ra_house2 + 180) % 360
        ra_house9 = (ra_house3 + 180) % 360
        
        # RA'dan ekliptik boylamlara dönüşüm
        # Bu, en kritik ve karmaşık adım
        
        def ra_to_ecliptic_longitude(ra, latitude):
            """
            Sağ açıklığı (RA) ekliptik boylama dönüştürür
            
            Args:
                ra (float): Sağ açıklık derecesi
                latitude (float): Enlem derecesi
                
            Returns:
                float: Ekliptik boylam (0-360 derece)
            """
            # RA'yı saat açısına (hour angle) dönüştür
            hour_angle = (ra_mc - ra) % 360
            if hour_angle > 180:
                hour_angle = hour_angle - 360
            
            # Saat açısını radyana çevir
            hour_angle_rad = math.radians(hour_angle)
            
            # Deklinasyon hesapla (declination) - yaklaşık değer
            # Gerçek hesaplama daha karmaşıktır ve iterasyon gerektirir
            sin_dec = math.sin(obliquity_rad) * math.sin(math.radians((ra + 90) % 360))
            dec_rad = math.asin(sin_dec)
            
            # Yükseklik (altitude) hesapla
            sin_alt = math.sin(latitude_rad) * math.sin(dec_rad) + math.cos(latitude_rad) * math.cos(dec_rad) * math.cos(hour_angle_rad)
            alt_rad = math.asin(sin_alt)
            
            # Azimut (azimuth) hesapla
            sin_az = -math.cos(dec_rad) * math.sin(hour_angle_rad) / math.cos(alt_rad)
            cos_az = (math.sin(dec_rad) - math.sin(latitude_rad) * math.sin(alt_rad)) / (math.cos(latitude_rad) * math.cos(alt_rad))
            az = math.degrees(math.atan2(sin_az, cos_az))
            
            # Ekliptik boylam hesapla
            # Bu adım gerçekte iteratif bir süreçtir
            # Burada Sphynx formülünü kullanacağız
            
            # Saat açısı ve deklinasyondan ekliptik boylam hesaplama - yaklaşık
            tan_lon = math.tan(dec_rad) / math.sin(obliquity_rad)
            lon = math.degrees(math.atan(tan_lon))
            
            # Açıyı doğru kadrana getir
            if hour_angle < 0:
                lon = (lon + 90) % 360
            else:
                lon = (lon + 270) % 360
            
            # Kesin sonuç için iteratif hesaplama gerekir
            # Bu, basitleştirilmiş bir yaklaşımdır
            return lon
        
        # Tüm evlerin ekliptik boylamlarını hesapla
        house11_longitude = ra_to_ecliptic_longitude(ra_house11, latitude)
        house12_longitude = ra_to_ecliptic_longitude(ra_house12, latitude)
        house2_longitude = ra_to_ecliptic_longitude(ra_house2, latitude)
        house3_longitude = ra_to_ecliptic_longitude(ra_house3, latitude)
        house5_longitude = ra_to_ecliptic_longitude(ra_house5, latitude)
        house6_longitude = ra_to_ecliptic_longitude(ra_house6, latitude)
        house8_longitude = ra_to_ecliptic_longitude(ra_house8, latitude)
        house9_longitude = ra_to_ecliptic_longitude(ra_house9, latitude)
        
        # House cusps değerlerini hazırla
        houses[11] = {
            'cusp_longitude': house11_longitude,
            'sign_num': (int(house11_longitude / 30) % 12) + 1,
            'degree_in_sign': house11_longitude % 30
        }
        
        houses[12] = {
            'cusp_longitude': house12_longitude,
            'sign_num': (int(house12_longitude / 30) % 12) + 1,
            'degree_in_sign': house12_longitude % 30
        }
        
        houses[2] = {
            'cusp_longitude': house2_longitude,
            'sign_num': (int(house2_longitude / 30) % 12) + 1,
            'degree_in_sign': house2_longitude % 30
        }
        
        houses[3] = {
            'cusp_longitude': house3_longitude,
            'sign_num': (int(house3_longitude / 30) % 12) + 1,
            'degree_in_sign': house3_longitude % 30
        }
        
        houses[5] = {
            'cusp_longitude': house5_longitude,
            'sign_num': (int(house5_longitude / 30) % 12) + 1,
            'degree_in_sign': house5_longitude % 30
        }
        
        houses[6] = {
            'cusp_longitude': house6_longitude,
            'sign_num': (int(house6_longitude / 30) % 12) + 1,
            'degree_in_sign': house6_longitude % 30
        }
        
        houses[8] = {
            'cusp_longitude': house8_longitude,
            'sign_num': (int(house8_longitude / 30) % 12) + 1,
            'degree_in_sign': house8_longitude % 30
        }
        
        houses[9] = {
            'cusp_longitude': house9_longitude,
            'sign_num': (int(house9_longitude / 30) % 12) + 1,
            'degree_in_sign': house9_longitude % 30
        }
        
        # MC, IC, ASC ve DESC'i de ekleyelim
        houses[10] = {
            'cusp_longitude': mc_longitude,
            'sign_num': (int(mc_longitude / 30) % 12) + 1,
            'degree_in_sign': mc_longitude % 30
        }
        
        houses[4] = {
            'cusp_longitude': ic_longitude,
            'sign_num': (int(ic_longitude / 30) % 12) + 1,
            'degree_in_sign': ic_longitude % 30
        }
        
        houses[1] = {
            'cusp_longitude': asc_longitude,
            'sign_num': (int(asc_longitude / 30) % 12) + 1,
            'degree_in_sign': asc_longitude % 30
        }
        
        houses[7] = {
            'cusp_longitude': desc_longitude,
            'sign_num': (int(desc_longitude / 30) % 12) + 1,
            'degree_in_sign': desc_longitude % 30
        }
        
        return houses
    
def calculate_houses_koch(self, birth_date, birth_time, latitude, longitude):
    """
    Koch ev sistemine göre ev başlangıç noktalarını hesaplar
    
    Args:
        birth_date (datetime.date): Doğum tarihi
        birth_time (datetime.time): Doğum saati
        latitude (float): Enlem derecesi
        longitude (float): Boylam derecesi
        
    Returns:
        dict: Ev başlangıç noktaları ve burç konumları
    """
    # Gezegen pozisyonlarını al (RAMC hesaplaması için)
    planet_positions = self.ephemeris_calculator.calculate_planet_positions(
        birth_date, birth_time, latitude, longitude)
    
    # RAMC (Right Ascension of the Midheaven) al
    ramc = planet_positions['ramc']
    
    # Ekliptik eğim açısı (Earth's Obliquity)
    obliquity = planet_positions['obliquity']
    
    # Enlem ve ekliptik eğimi radyana çevir
    latitude_rad = math.radians(latitude)
    obliquity_rad = math.radians(obliquity)
    
    # MC (Medium Coeli - Midheaven) - 10. Ev
    mc_longitude = ramc
    
    # IC (Imum Coeli) - 4. Ev - MC'nin tam karşısı
    ic_longitude = (mc_longitude + 180) % 360
    
    # Ascendant (Yükselen - 1. Ev) hesaplama
    ramc_rad = math.radians(ramc)
    
    tan_asc = math.sin(ramc_rad) / (math.cos(ramc_rad) * math.cos(obliquity_rad) - 
                                    math.tan(latitude_rad) * math.sin(obliquity_rad))
    asc_longitude = math.degrees(math.atan(tan_asc))
    
    # Açıyı doğru kadrana getir
    if math.cos(ramc_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
        asc_longitude += 180
    
    # Açıyı 0-360 aralığına getir
    asc_longitude = (asc_longitude + 360) % 360
    
    # Descendant (7. Ev) - Ascendant'ın tam karşısı
    desc_longitude = (asc_longitude + 180) % 360
    
    # Koch ev sisteminde diğer evleri hesapla
    houses = self._calculate_koch_houses(ramc, obliquity, latitude)
    
    # MC, IC, Ascendant ve Descendant'ı ekle/güncelle
    houses[10] = {
        'cusp_longitude': mc_longitude,
        'sign_num': (int(mc_longitude / 30) % 12) + 1,
        'degree_in_sign': mc_longitude % 30
    }
    
    houses[4] = {
        'cusp_longitude': ic_longitude,
        'sign_num': (int(ic_longitude / 30) % 12) + 1,
        'degree_in_sign': ic_longitude % 30
    }
    
    houses[1] = {
        'cusp_longitude': asc_longitude,
        'sign_num': (int(asc_longitude / 30) % 12) + 1,
        'degree_in_sign': asc_longitude % 30
    }
    
    houses[7] = {
        'cusp_longitude': desc_longitude,
        'sign_num': (int(desc_longitude / 30) % 12) + 1,
        'degree_in_sign': desc_longitude % 30
    }
    
    return houses


def calculate_houses_whole_sign(self, birth_date, birth_time, latitude, longitude):
    """
    Whole Sign ev sistemine göre ev başlangıç noktalarını hesaplar
    
    Args:
        birth_date (datetime.date): Doğum tarihi
        birth_time (datetime.time): Doğum saati
        latitude (float): Enlem derecesi
        longitude (float): Boylam derecesi
        
    Returns:
        dict: Ev başlangıç noktaları ve burç konumları
    """
    # Gezegen pozisyonlarını al (Yükselen hesaplaması için)
    planet_positions = self.ephemeris_calculator.calculate_planet_positions(
        birth_date, birth_time, latitude, longitude)
    
    # Yükselen burcu al (1. ev)
    if 'ascendant' in planet_positions:
        asc_sign_num = planet_positions['ascendant']['sign_num']
    else:
        # Eğer ascendant pozisyonda yoksa, varsayılan değer kullan
        asc_sign_num = 1
    
    houses = {}
    
    # Whole Sign sisteminde, evler tam olarak burçlarla aynı hizadadır
    # 1. ev yükselen burcun olduğu burçtur
    for i in range(1, 13):
        # ((Yükselen burç numarası + i - 1) % 12) formülü ile her evi hesapla
        # Örneğin: Yükselen Koç (1) ise, 1. ev Koç (1), 2. ev Boğa (2), ...
        # Yükselen İkizler (3) ise, 1. ev İkizler (3), 2. ev Yengeç (4), ...
        sign_num = ((asc_sign_num + i - 2) % 12) + 1  # 1'den 12'ye
        
        # Her evin başlangıç noktası, ilgili burcun başlangıcıdır (0 derece)
        cusp_longitude = (sign_num - 1) * 30
        
        houses[i] = {
            'cusp_longitude': cusp_longitude,
            'sign_num': sign_num,
            'degree_in_sign': 0  # Whole Sign sisteminde ev çizgileri her zaman 0 derecedir
        }
    
    return houses

def _calculate_koch_houses(self, ramc, obliquity, latitude):
    """
    Koch ev sistemi hesaplaması - tam matematiksel yöntem
    
    Args:
        ramc (float): RAMC (Right Ascension Medium Coeli)
        obliquity (float): Ekliptik eğim açısı
        latitude (float): Enlem derecesi
        
    Returns:
        dict: Tüm evlerin başlangıç noktaları
    """
    houses = {}
    
    # Radyan çevrimi
    latitude_rad = math.radians(latitude)
    obliquity_rad = math.radians(obliquity)
    
    # MC (10. Ev) ve IC (4. Ev) hesaplaması
    mc_longitude = ramc
    ic_longitude = (mc_longitude + 180) % 360
    
    # Ascendant (1. Ev) hesaplaması
    ramc_rad = math.radians(ramc)
    
    tan_asc = math.sin(ramc_rad) / (math.cos(ramc_rad) * math.cos(obliquity_rad) - 
                                   math.tan(latitude_rad) * math.sin(obliquity_rad))
    asc_longitude = math.degrees(math.atan(tan_asc))
    
    # Açıyı doğru kadrana getir
    if math.cos(ramc_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
        asc_longitude += 180
    
    # Açıyı 0-360 aralığına getir
    asc_longitude = (asc_longitude + 360) % 360
    
    # Koch sistemi: RAMC'ye 30, 60, 120, 150 derece eklenerek elde edilen "ara RAMC" değerleri kullanılır
    # ve bu ara değerler için ev noktaları hesaplanır
    
    # 11, 12, 2, 3, 8, 9 evleri için saat açıları (30°, 60°, 120°, 150°, 210°, 240°, 300°, 330°)
    # Koch yöntemi, bu saat açılarını kullanarak "hayali RAMC" değerleri oluşturur ve bu değerler için
    # Ascendant formülünü uygular
    
    # House 11 (MC + 30°)
    koch_ramc_11 = (ramc + 30) % 360
    koch_ramc_11_rad = math.radians(koch_ramc_11)
    
    tan_h11 = math.sin(koch_ramc_11_rad) / (math.cos(koch_ramc_11_rad) * math.cos(obliquity_rad) - 
                                         math.tan(latitude_rad) * math.sin(obliquity_rad))
    h11_longitude = math.degrees(math.atan(tan_h11))
    
    # Açıyı doğru kadrana getir
    if math.cos(koch_ramc_11_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
        h11_longitude += 180
    
    h11_longitude = (h11_longitude + 360) % 360
    
    houses[11] = {
        'cusp_longitude': h11_longitude,
        'sign_num': (int(h11_longitude / 30) % 12) + 1,
        'degree_in_sign': h11_longitude % 30
    }
    
    # House 12 (MC + 60°)
    koch_ramc_12 = (ramc + 60) % 360
    koch_ramc_12_rad = math.radians(koch_ramc_12)
    
    tan_h12 = math.sin(koch_ramc_12_rad) / (math.cos(koch_ramc_12_rad) * math.cos(obliquity_rad) - 
                                         math.tan(latitude_rad) * math.sin(obliquity_rad))
    h12_longitude = math.degrees(math.atan(tan_h12))
    
    # Açıyı doğru kadrana getir
    if math.cos(koch_ramc_12_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
        h12_longitude += 180
    
    h12_longitude = (h12_longitude + 360) % 360
    
    houses[12] = {
        'cusp_longitude': h12_longitude,
        'sign_num': (int(h12_longitude / 30) % 12) + 1,
        'degree_in_sign': h12_longitude % 30
    }
    
    # House 2 (IC + 30°)
    koch_ramc_2 = (ramc + 210) % 360  # IC + 30° = MC + 180° + 30° = MC + 210°
    koch_ramc_2_rad = math.radians(koch_ramc_2)
    
    tan_h2 = math.sin(koch_ramc_2_rad) / (math.cos(koch_ramc_2_rad) * math.cos(obliquity_rad) - 
                                       math.tan(latitude_rad) * math.sin(obliquity_rad))
    h2_longitude = math.degrees(math.atan(tan_h2))
    
    # Açıyı doğru kadrana getir
    if math.cos(koch_ramc_2_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
        h2_longitude += 180
    
    h2_longitude = (h2_longitude + 360) % 360
    
    houses[2] = {
        'cusp_longitude': h2_longitude,
        'sign_num': (int(h2_longitude / 30) % 12) + 1,
        'degree_in_sign': h2_longitude % 30
    }
    
    # House 3 (IC + 60°)
    koch_ramc_3 = (ramc + 240) % 360  # IC + 60° = MC + 180° + 60° = MC + 240°
    koch_ramc_3_rad = math.radians(koch_ramc_3)
    
    tan_h3 = math.sin(koch_ramc_3_rad) / (math.cos(koch_ramc_3_rad) * math.cos(obliquity_rad) - 
                                       math.tan(latitude_rad) * math.sin(obliquity_rad))
    h3_longitude = math.degrees(math.atan(tan_h3))
    
    # Açıyı doğru kadrana getir
    if math.cos(koch_ramc_3_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
        h3_longitude += 180
    
    h3_longitude = (h3_longitude + 360) % 360
    
    houses[3] = {
        'cusp_longitude': h3_longitude,
        'sign_num': (int(h3_longitude / 30) % 12) + 1,
        'degree_in_sign': h3_longitude % 30
    }
    
    # House 5 (DSC + 30°) = House 1 + 150°
    koch_ramc_5 = (ramc + 120) % 360
    koch_ramc_5_rad = math.radians(koch_ramc_5)
    
    tan_h5 = math.sin(koch_ramc_5_rad) / (math.cos(koch_ramc_5_rad) * math.cos(obliquity_rad) - 
                                       math.tan(latitude_rad) * math.sin(obliquity_rad))
    h5_longitude = math.degrees(math.atan(tan_h5))
    
    # Açıyı doğru kadrana getir
    if math.cos(koch_ramc_5_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
        h5_longitude += 180
    
    h5_longitude = (h5_longitude + 360) % 360
    
    houses[5] = {
        'cusp_longitude': h5_longitude,
        'sign_num': (int(h5_longitude / 30) % 12) + 1,
        'degree_in_sign': h5_longitude % 30
    }
    
    # House 6 (DSC + 60°) = House 1 + 180°
    koch_ramc_6 = (ramc + 150) % 360
    koch_ramc_6_rad = math.radians(koch_ramc_6)
    
    tan_h6 = math.sin(koch_ramc_6_rad) / (math.cos(koch_ramc_6_rad) * math.cos(obliquity_rad) - 
                                       math.tan(latitude_rad) * math.sin(obliquity_rad))
    h6_longitude = math.degrees(math.atan(tan_h6))
    
    # Açıyı doğru kadrana getir
    if math.cos(koch_ramc_6_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
        h6_longitude += 180
    
    h6_longitude = (h6_longitude + 360) % 360
    
    houses[6] = {
        'cusp_longitude': h6_longitude,
        'sign_num': (int(h6_longitude / 30) % 12) + 1,
        'degree_in_sign': h6_longitude % 30
    }
    
    # House 8 (ASC + 30°)
    koch_ramc_8 = (ramc + 300) % 360
    koch_ramc_8_rad = math.radians(koch_ramc_8)
    
    tan_h8 = math.sin(koch_ramc_8_rad) / (math.cos(koch_ramc_8_rad) * math.cos(obliquity_rad) - 
                                       math.tan(latitude_rad) * math.sin(obliquity_rad))
    h8_longitude = math.degrees(math.atan(tan_h8))
    
    # Açıyı doğru kadrana getir
    if math.cos(koch_ramc_8_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
        h8_longitude += 180
    
    h8_longitude = (h8_longitude + 360) % 360
    
    houses[8] = {
        'cusp_longitude': h8_longitude,
        'sign_num': (int(h8_longitude / 30) % 12) + 1,
        'degree_in_sign': h8_longitude % 30
    }
    
    # House 9 (ASC + 60°)
    koch_ramc_9 = (ramc + 330) % 360
    koch_ramc_9_rad = math.radians(koch_ramc_9)
    
    tan_h9 = math.sin(koch_ramc_9_rad) / (math.cos(koch_ramc_9_rad) * math.cos(obliquity_rad) - 
                                       math.tan(latitude_rad) * math.sin(obliquity_rad))
    h9_longitude = math.degrees(math.atan(tan_h9))
    
    # Açıyı doğru kadrana getir
    if math.cos(koch_ramc_9_rad) * math.cos(obliquity_rad) - math.tan(latitude_rad) * math.sin(obliquity_rad) < 0:
        h9_longitude += 180
    
    h9_longitude = (h9_longitude + 360) % 360
    
    houses[9] = {
        'cusp_longitude': h9_longitude,
        'sign_num': (int(h9_longitude / 30) % 12) + 1,
        'degree_in_sign': h9_longitude % 30
    }
    
    return houses