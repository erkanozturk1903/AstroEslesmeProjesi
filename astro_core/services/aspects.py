# astro_core/services/aspects.py

import math

class AspectCalculator:
    def __init__(self):
        # Varsayılan orb değerleri (açı toleransı)
        self.default_orbs = {
            'conjunction': 10.0,  # Kavuşum - Güneş/Ay için daha geniş
            'opposition': 10.0,   # Karşıt
            'trine': 8.0,         # Üçgen
            'square': 8.0,        # Kare
            'sextile': 6.0,       # Altmışlık
            'quincunx': 5.0,      # Yüzellilik
            'semi_sextile': 3.0,  # Otuzluk
            'semi_square': 3.0,   # Yarım kare
            'sesquiquadrate': 3.0, # Bir buçuk kare
            'quintile': 2.0,      # Beşli (72 derece)
            'bi_quintile': 2.0,   # İki Beşli (144 derece)
            'septile': 1.5,       # Yedili (51.4 derece)
            'novile': 1.5,        # Dokuzlu (40 derece)
            'parallel': 1.0,      # Paralel (deklinasyon)
            'contra_parallel': 1.0 # Karşıt Paralel (deklinasyon)
        }
        
        # Açı tipleri ve dereceleri
        self.aspect_types = {
            'conjunction': 0,     # Kavuşum
            'opposition': 180,    # Karşıt
            'trine': 120,         # Üçgen
            'square': 90,         # Kare
            'sextile': 60,        # Altmışlık
            'quincunx': 150,      # Yüzellilik
            'semi_sextile': 30,   # Otuzluk
            'semi_square': 45,    # Yarım kare
            'sesquiquadrate': 135, # Bir buçuk kare
            'quintile': 72,       # Beşli
            'bi_quintile': 144,   # İki Beşli
            'septile': 51.4,      # Yedili
            'novile': 40,         # Dokuzlu
            'parallel': 0,        # Paralel (özel hesaplama)
            'contra_parallel': 180 # Karşıt Paralel (özel hesaplama)
        }
        
        # Her bir açı tipinin doğası
        self.aspect_natures = {
            'conjunction': 'neutral',    # Kavuşum - Gezegenin doğasına bağlı
            'opposition': 'challenging',  # Karşıt - Zorlayıcı
            'trine': 'harmonious',       # Üçgen - Uyumlu
            'square': 'challenging',     # Kare - Zorlayıcı
            'sextile': 'harmonious',     # Altmışlık - Uyumlu
            'quincunx': 'challenging',   # Yüzellilik - Zorlayıcı
            'semi_sextile': 'neutral',   # Otuzluk - Nötr
            'semi_square': 'challenging', # Yarım kare - Zorlayıcı
            'sesquiquadrate': 'challenging', # Bir buçuk kare - Zorlayıcı
            'quintile': 'harmonious',    # Beşli - Uyumlu
            'bi_quintile': 'harmonious', # İki Beşli - Uyumlu
            'septile': 'mystical',       # Yedili - Mistik
            'novile': 'spiritual',       # Dokuzlu - Spiritüel
            'parallel': 'neutral',       # Paralel - Nötr
            'contra_parallel': 'challenging' # Karşıt Paralel - Zorlayıcı
        }
        
        # Açıların gücünü belirleyen katsayılar (1.0 en güçlü, 0.1 en zayıf)
        self.aspect_strengths = {
            'conjunction': 1.0,    # Kavuşum - En güçlü
            'opposition': 0.9,     # Karşıt
            'trine': 0.8,          # Üçgen
            'square': 0.7,         # Kare
            'sextile': 0.6,        # Altmışlık
            'quincunx': 0.4,       # Yüzellilik
            'semi_sextile': 0.3,   # Otuzluk
            'semi_square': 0.3,    # Yarım kare
            'sesquiquadrate': 0.3, # Bir buçuk kare
            'quintile': 0.2,       # Beşli
            'bi_quintile': 0.2,    # İki Beşli
            'septile': 0.1,        # Yedili
            'novile': 0.1,         # Dokuzlu
            'parallel': 0.3,       # Paralel
            'contra_parallel': 0.3 # Karşıt Paralel
        }
        
        # Gezegen bazlı ek orb ayarlamaları (özelleştirme için)
        self.planet_orb_modifiers = {
            'sun': 2.0,       # Güneş için daha geniş orb
            'moon': 2.0,      # Ay için daha geniş orb
            'mercury': 0.0,   # Merkür için standart orb
            'venus': 0.0,     # Venüs için standart orb
            'mars': 0.0,      # Mars için standart orb
            'jupiter': 1.0,   # Jüpiter için biraz daha geniş orb
            'saturn': 1.0,    # Satürn için biraz daha geniş orb
            'uranus': -0.5,   # Uranüs için daha dar orb
            'neptune': -0.5,  # Neptün için daha dar orb
            'pluto': -0.5,    # Plüton için daha dar orb
            'north_node': -1.0, # Kuzey Düğüm için daha dar orb
            'south_node': -1.0, # Güney Düğüm için daha dar orb
            'ascendant': 1.0,   # Yükselen için daha geniş orb
            'mc': 1.0,          # MC için daha geniş orb
            'part_of_fortune': -0.5  # Part of Fortune için daha dar orb
        }
        
        # Majör ve minör açılar ayırımı
        self.major_aspects = ['conjunction', 'opposition', 'trine', 'square', 'sextile']
        self.minor_aspects = ['quincunx', 'semi_sextile', 'semi_square', 'sesquiquadrate',
                             'quintile', 'bi_quintile', 'septile', 'novile']
        self.declination_aspects = ['parallel', 'contra_parallel']
    
    def calculate_aspects(self, planet_positions, custom_orbs=None, include_minor_aspects=True, include_dec_aspects=False):
        """
        Gezegenler arasındaki açıları hesaplar
        
        Args:
            planet_positions (dict): Gezegen konumları (ephemeris_calculator'dan alınan)
            custom_orbs (dict, optional): Özel orb değerleri. Varsayılan olarak None.
            include_minor_aspects (bool): Minör açıları hesaplamaya dahil et. Varsayılan True.
            include_dec_aspects (bool): Deklinasyon açılarını hesaplamaya dahil et. Varsayılan False.
            
        Returns:
            list: Hesaplanan açı listesi
        """
        # Eğer özel orb değerleri verilmişse onları kullan, değilse varsayılanları kullan
        orbs = custom_orbs if custom_orbs else self.default_orbs
        
        aspects = []
        
        # Dahil edilecek açı tiplerini belirle
        aspect_types_to_include = self.major_aspects.copy()
        if include_minor_aspects:
            aspect_types_to_include.extend(self.minor_aspects)
        if include_dec_aspects:
            aspect_types_to_include.extend(self.declination_aspects)
        
        # Tüm gezegen çiftleri için açıları hesapla
        planets = list(planet_positions.keys())
        for i, planet1 in enumerate(planets):
            if not isinstance(planet_positions[planet1], dict) or 'longitude' not in planet_positions[planet1]:
                continue  # Geçersiz gezegen verisi, atla
                
            for planet2 in planets[i+1:]:  # Aynı gezegen kombinasyonlarını önlemek için i+1'den başla
                if not isinstance(planet_positions[planet2], dict) or 'longitude' not in planet_positions[planet2]:
                    continue  # Geçersiz gezegen verisi, atla
                
                # İki gezegen arasındaki açıyı hesapla
                lon1 = planet_positions[planet1]['longitude']
                lon2 = planet_positions[planet2]['longitude']
                
                # Açı farkı (0-180 arası)
                angle_diff = abs(lon1 - lon2) % 360
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                
                # Hangi açı tipini oluşturduğunu kontrol et
                for aspect_name in aspect_types_to_include:
                    # Deklinasyon açıları için özel kontrol
                    if aspect_name in self.declination_aspects:
                        if not include_dec_aspects:
                            continue
                        
                        # Deklinasyon açıları için değerleri kontrol et
                        if 'declination' not in planet_positions[planet1] or 'declination' not in planet_positions[planet2]:
                            continue
                        
                        dec1 = planet_positions[planet1]['declination']
                        dec2 = planet_positions[planet2]['declination']
                        
                        # Paralel: İki gezegen aynı deklinasyon tarafında, yakın değerlerde
                        # Karşıt Paralel: İki gezegen zıt deklinasyon taraflarında, ancak mutlak değerce yakın
                        if aspect_name == 'parallel':
                            # Aynı yönde (kuzey veya güney) ve yakın değerlerde olmalı
                            if (dec1 * dec2 > 0) and abs(abs(dec1) - abs(dec2)) <= orbs.get(aspect_name, 1.0):
                                aspects.append({
                                    'planet1': planet1,
                                    'planet2': planet2,
                                    'aspect_type': aspect_name,
                                    'angle': 0,  # Paralel için açı 0 kabul edilir
                                    'orb': abs(abs(dec1) - abs(dec2)),
                                    'nature': self.aspect_natures[aspect_name],
                                    'strength': self.aspect_strengths[aspect_name],
                                    'is_applying': self._is_applying_declination(planet_positions, planet1, planet2, True),
                                    'is_exact': abs(abs(dec1) - abs(dec2)) < 0.1,  # 0.1 dereceden az fark varsa tam kabul et
                                    'is_separating': not self._is_applying_declination(planet_positions, planet1, planet2, True)
                                })
                                
                        elif aspect_name == 'contra_parallel':
                            # Zıt yönlerde (biri kuzey, biri güney) ve mutlak değerce yakın olmalı
                            if (dec1 * dec2 < 0) and abs(abs(dec1) - abs(dec2)) <= orbs.get(aspect_name, 1.0):
                                aspects.append({
                                    'planet1': planet1,
                                    'planet2': planet2,
                                    'aspect_type': aspect_name,
                                    'angle': 180,  # Karşıt Paralel için açı 180 kabul edilir
                                    'orb': abs(abs(dec1) - abs(dec2)),
                                    'nature': self.aspect_natures[aspect_name],
                                    'strength': self.aspect_strengths[aspect_name],
                                    'is_applying': self._is_applying_declination(planet_positions, planet1, planet2, False),
                                    'is_exact': abs(abs(dec1) - abs(dec2)) < 0.1,  # 0.1 dereceden az fark varsa tam kabul et
                                    'is_separating': not self._is_applying_declination(planet_positions, planet1, planet2, False)
                                })
                        
                        continue  # Deklinasyon açısı kontrolü tamamlandı, diğer açılara geç
                    
                    # Standart ekliptik açılar için devam et
                    aspect_angle = self.aspect_types[aspect_name]
                    
                    # Bu açı tipi için orb değerini hesapla
                    # Gezegen bazlı modifikatörleri uygula
                    orb = orbs.get(aspect_name, 2.0)  # Varsayılan olarak 2 derecelik orb
                    
                    # Gezegen modifikatörlerini uygula
                    planet1_modifier = self.planet_orb_modifiers.get(planet1, 0.0)
                    planet2_modifier = self.planet_orb_modifiers.get(planet2, 0.0)
                    
                    # Modifikatörlerin ortalamasını al
                    combined_modifier = (planet1_modifier + planet2_modifier) / 2.0
                    
                    # Orb değerini ayarla
                    adjusted_orb = orb + combined_modifier
                    
                    # Minör açılar için daha küçük orb kullan
                    if aspect_name in self.minor_aspects:
                        adjusted_orb *= 0.7  # %70 azalt
                    
                    # Açı, beklenen değere orb değeri içinde yakınsa
                    if abs(angle_diff - aspect_angle) <= adjusted_orb:
                        # Gezegen hızlarını al
                        speed1 = planet_positions[planet1].get('daily_motion', 1.0)  # Varsayılan 1 derece/gün
                        speed2 = planet_positions[planet2].get('daily_motion', 1.0)
                        
                        # Açının yaklaşan veya uzaklaşan olduğunu belirle
                        is_applying = self._is_applying(planet_positions, planet1, planet2, angle_diff, aspect_angle)
                        
                        # Açının gücünü hesapla
                        # Formül: Temel güç * (1 - (orb / maksimum orb))
                        aspect_strength = self.aspect_strengths.get(aspect_name, 0.5)
                        orb_ratio = abs(angle_diff - aspect_angle) / adjusted_orb
                        power_factor = 1.0 - orb_ratio
                        final_strength = aspect_strength * power_factor
                        
                        # Açıyı listeye ekle
                        aspects.append({
                            'planet1': planet1,
                            'planet2': planet2,
                            'aspect_type': aspect_name,
                            'angle': aspect_angle,
                            'orb': abs(angle_diff - aspect_angle),
                            'nature': self.aspect_natures.get(aspect_name, 'neutral'),
                            'strength': final_strength,
                            'is_applying': is_applying,
                            'is_exact': abs(angle_diff - aspect_angle) < 0.1,  # 0.1 dereceden az fark varsa tam kabul et
                            'is_separating': not is_applying
                        })
                        break  # Bir açı bulduysak diğer açı tiplerine bakmaya gerek yok
        
        # Açıları güçlerine göre sırala (en güçlüden en zayıfa)
        aspects.sort(key=lambda x: x['strength'], reverse=True)
        
        return aspects
    
    def _is_applying(self, planet_positions, planet1, planet2, current_angle, aspect_angle):
        """
        Açının yaklaşan mı yoksa uzaklaşan mı olduğunu belirler
        
        Args:
            planet_positions (dict): Gezegen konumları
            planet1 (str): Birinci gezegen adı
            planet2 (str): İkinci gezegen adı
            current_angle (float): Şu anki açı değeri
            aspect_angle (float): Hedef açı değeri (örn: 0, 60, 90, 120, 180)
            
        Returns:
            bool: Eğer açı yaklaşıyorsa True, uzaklaşıyorsa False
        """
        # Gezegenlerin hızlarını (günlük hareket) al
        if 'daily_motion' not in planet_positions[planet1] or 'daily_motion' not in planet_positions[planet2]:
            return False  # Veriler eksikse varsayılan olarak uzaklaşıyor kabul et
        
        speed1 = planet_positions[planet1]['daily_motion']
        speed2 = planet_positions[planet2]['daily_motion']
        
        # Retrograde durumlarını kontrol et
        is_retrograde1 = planet_positions[planet1].get('is_retrograde', False)
        is_retrograde2 = planet_positions[planet2].get('is_retrograde', False)
        
        # Retrograde gezegenler için hızı negatif işaretle
        if is_retrograde1:
            speed1 = -abs(speed1)
        
        if is_retrograde2:
            speed2 = -abs(speed2)
        
        # İki gezegenin göreceli hızı
        relative_speed = speed1 - speed2
        
        # Eğer göreceli hız sıfıra çok yakınsa, açı sabit kabul edilir
        if abs(relative_speed) < 0.01:
            return False  # Uzaklaşıyor kabul et
        
        # Gezegenlerin boylam konumları
        lon1 = planet_positions[planet1]['longitude']
        lon2 = planet_positions[planet2]['longitude']
        
        # Gercek açı farkı (0-360 arası)
        actual_diff = (lon1 - lon2) % 360
        
        # Hedef açı değerine göre yaklaşma veya uzaklaşma durumu
        if aspect_angle == 0:  # Kavuşum için
            # Göreceli hız negatifse, gezegen1 gezegen2'ye yaklaşıyor demektir
            return (actual_diff <= 180 and relative_speed < 0) or (actual_diff > 180 and relative_speed > 0)
            
        elif aspect_angle == 180:  # Karşıt için
            # 180 derece hedefleniyorsa, açı farkı 180'e yaklaşmalı
            return (actual_diff < 180 and relative_speed > 0) or (actual_diff > 180 and relative_speed < 0)
            
        else:  # Diğer açılar için (60, 90, 120, vb.)
            # Açı farkının hedef açıya göre konumu
            diff_to_target = abs(actual_diff - aspect_angle)
            diff_to_target = min(diff_to_target, 360 - diff_to_target)
            
            # Göreceli hızın etkisi
            # Açı büyüyorsa ve hedef açı küçükse, açı uzaklaşıyor
            # Açı küçülüyorsa ve hedef açı büyükse, açı uzaklaşıyor
            if (actual_diff < aspect_angle and relative_speed < 0) or (actual_diff > aspect_angle and relative_speed > 0):
                return True
            else:
                return False
                
        return False  # Varsayılan durumda uzaklaşıyor kabul et
    
    def _is_applying_declination(self, planet_positions, planet1, planet2, is_parallel):
        """
        Deklinasyon açısının yaklaşan mı yoksa uzaklaşan mı olduğunu belirler
        
        Args:
            planet_positions (dict): Gezegen konumları
            planet1 (str): Birinci gezegen adı
            planet2 (str): İkinci gezegen adı
            is_parallel (bool): Paralel açı mı (True) yoksa karşıt paralel mi (False)
            
        Returns:
            bool: Eğer açı yaklaşıyorsa True, uzaklaşıyorsa False
        """
        # Deklinasyon değerlerini al
        if 'declination' not in planet_positions[planet1] or 'declination' not in planet_positions[planet2]:
            return False
        
        dec1 = planet_positions[planet1]['declination']
        dec2 = planet_positions[planet2]['declination']
        
        # Gezegenlerin hızlarını al (varsayılan değerler)
        speed1 = planet_positions[planet1].get('declination_speed', 0.0)
        speed2 = planet_positions[planet2].get('declination_speed', 0.0)
        
        # Göreceli hız
        relative_speed = speed1 - speed2
        
        # Eğer göreceli hız sıfıra çok yakınsa, açı sabit kabul edilir
        if abs(relative_speed) < 0.001:
            return False
        
        # Paralel açı için (aynı yönde deklinasyon)
        if is_parallel:
            # Aynı yönde (ikisi de kuzey veya ikisi de güney)
            if (dec1 * dec2 > 0):
                # Deklinasyonlar birbirine yaklaşıyor mu?
                return (abs(dec1) > abs(dec2) and speed1 < speed2) or (abs(dec1) < abs(dec2) and speed1 > speed2)
        
        # Karşıt paralel için (zıt yönlerde deklinasyon)
        else:
            # Zıt yönlerde (biri kuzey, biri güney)
            if (dec1 * dec2 < 0):
                # Deklinasyonların mutlak değerleri birbirine yaklaşıyor mu?
                return (abs(dec1) > abs(dec2) and speed1 < 0) or (abs(dec1) < abs(dec2) and speed1 > 0)
        
        return False
    
    def calculate_aspect_grid(self, planet_positions, custom_orbs=None, include_minor_aspects=True):
        """
        Tüm gezegenler arasındaki açıları içeren bir ızgara (grid) oluşturur
        
        Args:
            planet_positions (dict): Gezegen konumları
            custom_orbs (dict, optional): Özel orb değerleri. Varsayılan olarak None.
            include_minor_aspects (bool): Minör açıları dahil et. Varsayılan True.
            
        Returns:
            dict: Gezegen çiftleri için açı ızgarası
        """
        # Tüm açıları hesapla
        all_aspects = self.calculate_aspects(planet_positions, custom_orbs, include_minor_aspects)
        
        # Gezegen listesini al
        planets = [p for p in planet_positions.keys() if isinstance(planet_positions[p], dict) and 'longitude' in planet_positions[p]]
        
        # Boş ızgarayı oluştur
        grid = {}
        for p1 in planets:
            grid[p1] = {}
            for p2 in planets:
                grid[p1][p2] = None  # Başlangıçta tüm çiftler için açı yok
        
        # Izgara için hesaplanan açıları yerleştir
        for aspect in all_aspects:
            p1 = aspect['planet1']
            p2 = aspect['planet2']
            
            # Her iki yönde de aynı açıyı kaydet
            grid[p1][p2] = aspect
            
            # Diğer yönde de ayın açıyı kaydet (simetrik)
            reverse_aspect = aspect.copy()
            reverse_aspect['planet1'] = p2
            reverse_aspect['planet2'] = p1
            grid[p2][p1] = reverse_aspect
        
        return grid
    
    def calculate_composite_aspects(self, chart1_positions, chart2_positions, custom_orbs=None):
        """
        İki doğum haritası arasındaki kompozit açıları hesaplar
        
        Args:
            chart1_positions (dict): Birinci haritanın gezegen konumları
            chart2_positions (dict): İkinci haritanın gezegen konumları
            custom_orbs (dict, optional): Özel orb değerleri. Varsayılan olarak None.
            
        Returns:
            list: İki harita arasındaki açı listesi
        """
        # İki harita arasındaki açıları hesaplamak için tüm çiftleri kontrol et
        aspects = []
        
        # Hesaplamaları sadece ekliptik boylamlar için yap
        # Ortak gezegenler için bir liste oluştur
        common_planets = [p for p in chart1_positions.keys() if p in chart2_positions and
                         isinstance(chart1_positions[p], dict) and isinstance(chart2_positions[p], dict) and
                         'longitude' in chart1_positions[p] and 'longitude' in chart2_positions[p]]
        
        # Her bir gezegen çifti için
        for planet1 in common_planets:
            lon1 = chart1_positions[planet1]['longitude']
            
            for planet2 in common_planets:
                lon2 = chart2_positions[planet2]['longitude']
                
                # Açı farkı (0-180 arası)
                angle_diff = abs(lon1 - lon2) % 360
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                
                # Hangi açı tipini oluşturduğunu kontrol et
                for aspect_name, aspect_angle in self.aspect_types.items():
                    # Deklinasyon açılarını atla
                    if aspect_name in self.declination_aspects:
                        continue
                    
                    # Bu açı tipi için orb değerini hesapla
                    orb = custom_orbs.get(aspect_name, self.default_orbs.get(aspect_name, 2.0))
                    
                    # Gezegen bazlı modifikatörleri uygula
                    planet1_modifier = self.planet_orb_modifiers.get(planet1, 0.0)
                    planet2_modifier = self.planet_orb_modifiers.get(planet2, 0.0)
                    
                    # Modifikatörlerin ortalamasını al
                    combined_modifier = (planet1_modifier + planet2_modifier) / 2.0
                    
                    # Orb değerini ayarla
                    adjusted_orb = orb + combined_modifier
                    
                    # Minör açılar için daha küçük orb kullan
                    if aspect_name in self.minor_aspects:
                        adjusted_orb *= 0.7  # %70 azalt
                    
                    # Açı, beklenen değere orb değeri içinde yakınsa
                    if abs(angle_diff - aspect_angle) <= adjusted_orb:
                        # Açının gücünü hesapla
                        aspect_strength = self.aspect_strengths.get(aspect_name, 0.5)
                        orb_ratio = abs(angle_diff - aspect_angle) / adjusted_orb
                        power_factor = 1.0 - orb_ratio
                        final_strength = aspect_strength * power_factor
                        
                        # Açıyı listeye ekle
                        aspects.append({
                            'chart1_planet': planet1,
                            'chart2_planet': planet2,
                            'aspect_type': aspect_name,
                            'angle': aspect_angle,
                            'orb': abs(angle_diff - aspect_angle),
                            'nature': self.aspect_natures.get(aspect_name, 'neutral'),
                            'strength': final_strength
                        })
                        break  # Bir açı bulduysak diğer açı tiplerine bakmaya gerek yok
        
        # Açıları güçlerine göre sırala (en güçlüden en zayıfa)
        aspects.sort(key=lambda x: x['strength'], reverse=True)
        
        return aspects
    
    def calculate_midpoint_aspects(self, planet_positions, custom_orbs=None):
        """
        Gezegen orta noktaları (midpoints) ve diğer gezegenler arasındaki açıları hesaplar
        
        Args:
            planet_positions (dict): Gezegen konumları
            custom_orbs (dict, optional): Özel orb değerleri. Varsayılan olarak None.
            
        Returns:
            list: Orta nokta açılarının listesi
        """
        midpoint_aspects = []
        
        # Gezegen listesini al
        planets = [p for p in planet_positions.keys() if isinstance(planet_positions[p], dict) and 'longitude' in planet_positions[p]]
        
        # Tüm gezegen çiftleri için orta noktaları hesapla
        midpoints = {}
        for i, p1 in enumerate(planets):
            for p2 in planets[i+1:]:  # p1'den sonraki tüm gezegenler
                lon1 = planet_positions[p1]['longitude']
                lon2 = planet_positions[p2]['longitude']
                
                # Orta nokta hesaplama (kısa yay yöntemi)
                diff = (lon2 - lon1) % 360
                if diff > 180:
                   diff = diff - 360
               
                midpoint = (lon1 + diff/2) % 360
               
               # Orta noktayı kaydet
                midpoint_key = f"{p1}-{p2}"
                midpoints[midpoint_key] = {
                   'longitude': midpoint,
                   'planet1': p1,
                   'planet2': p2
               }
       
       # Orb değeri: Orta noktalar için daha sıkı orb değerleri kullan
        orb_for_midpoints = 1.0  # 1 derecelik orb
       
       # Her bir orta nokta ve gezegen arasındaki açıları kontrol et
        for mp_key, mp_data in midpoints.items():
           mp_lon = mp_data['longitude']
           
           for planet in planets:
               # Orta noktayı oluşturan gezegenleri atla
               if planet == mp_data['planet1'] or planet == mp_data['planet2']:
                   continue
               
               planet_lon = planet_positions[planet]['longitude']
               
               # Açı farkı (0-180 arası)
               angle_diff = abs(mp_lon - planet_lon) % 360
               if angle_diff > 180:
                   angle_diff = 360 - angle_diff
               
               # Orta nokta için sadece bazı açıları kontrol et (genellikle kavuşum, karşıt, kare)
               for aspect_name in ['conjunction', 'opposition', 'square']:
                   aspect_angle = self.aspect_types[aspect_name]
                   
                   # Orta nokta için özel orb değeri (daha sıkı)
                   adjusted_orb = custom_orbs.get(aspect_name, orb_for_midpoints)
                   
                   # Açı, beklenen değere orb değeri içinde yakınsa
                   if abs(angle_diff - aspect_angle) <= adjusted_orb:
                       # Açının gücünü hesapla
                       aspect_strength = self.aspect_strengths.get(aspect_name, 0.5) * 0.8  # %80 güç (orta noktalar daha zayıf etkilidir)
                       
                       # Açıyı listeye ekle
                       midpoint_aspects.append({
                           'midpoint_key': mp_key,
                           'midpoint_planet1': mp_data['planet1'],
                           'midpoint_planet2': mp_data['planet2'],
                           'midpoint_longitude': mp_lon,
                           'planet': planet,
                           'aspect_type': aspect_name,
                           'angle': aspect_angle,
                           'orb': abs(angle_diff - aspect_angle),
                           'nature': self.aspect_natures.get(aspect_name, 'neutral'),
                           'strength': aspect_strength
                       })
                       break  # Bir açı bulduysak diğer açı tiplerine bakmaya gerek yok
       
        # Açıları güçlerine göre sırala
        midpoint_aspects.sort(key=lambda x: x['strength'], reverse=True)
       
        return midpoint_aspects
   
    def calculate_harmonic_aspects(self, planet_positions, harmonic=7, orb=1.0):
       """
       Belirli bir harmonik için açıları hesaplar
       
       Args:
           planet_positions (dict): Gezegen konumları
           harmonic (int): Hesaplanacak harmonik (örn: 7 için septil açıları)
           orb (float): Açı toleransı (derece)
           
       Returns:
           list: Harmonik açıların listesi
       """
       harmonic_aspects = []
       
       # Gezegen listesini al
       planets = [p for p in planet_positions.keys() if isinstance(planet_positions[p], dict) and 'longitude' in planet_positions[p]]
       
       # Harmonik açı hesapla
       harmonic_angle = 360.0 / harmonic
       
       # Tüm gezegen çiftleri için harmonik açıları kontrol et
       for i, planet1 in enumerate(planets):
           for planet2 in planets[i+1:]:  # planet1'den sonraki tüm gezegenler
               lon1 = planet_positions[planet1]['longitude']
               lon2 = planet_positions[planet2]['longitude']
               
               # Açı farkı
               angle_diff = abs(lon1 - lon2) % 360
               
               # Harmonik açı modülü
               harmonic_diff = angle_diff % harmonic_angle
               
               # En yakın harmonik açıyı bul
               if harmonic_diff > harmonic_angle / 2:
                   harmonic_diff = harmonic_angle - harmonic_diff
               
               # Açı toleransı içinde mi?
               if harmonic_diff <= orb:
                   # En yakın harmonik açı değerini hesapla
                   closest_harmonic = int(round(angle_diff / harmonic_angle)) * harmonic_angle
                   closest_harmonic = closest_harmonic % 360
                   
                   # Harmonik açı adını belirle
                   if harmonic == 5:
                       aspect_name = "quintile"
                       if closest_harmonic == 144:
                           aspect_name = "bi_quintile"
                   elif harmonic == 7:
                       aspect_name = "septile"
                   elif harmonic == 9:
                       aspect_name = "novile"
                   else:
                       aspect_name = f"harmonic_{harmonic}"
                   
                   # Açının gücünü hesapla
                   aspect_strength = 0.3 * (1.0 - (harmonic_diff / orb))  # Harmonik açılar daha zayıf
                   
                   # Açıyı listeye ekle
                   harmonic_aspects.append({
                       'planet1': planet1,
                       'planet2': planet2,
                       'aspect_type': aspect_name,
                       'harmonic': harmonic,
                       'harmonic_angle': harmonic_angle,
                       'angle': closest_harmonic,
                       'orb': harmonic_diff,
                       'strength': aspect_strength
                   })
       
       # Açıları güçlerine göre sırala
       harmonic_aspects.sort(key=lambda x: x['strength'], reverse=True)
       
       return harmonic_aspects
   
    def calculate_chart_compatibility(self, chart1_positions, chart2_positions):
       """
       İki doğum haritasının uyumluluğunu hesaplar
       
       Args:
           chart1_positions (dict): Birinci haritanın gezegen konumları
           chart2_positions (dict): İkinci haritanın gezegen konumları
           
       Returns:
           dict: Uyumluluk skorları ve değerlendirmeler
       """
       # İki harita arasındaki tüm açıları hesapla
       aspects = self.calculate_composite_aspects(chart1_positions, chart2_positions)
       
       # Uyumluluk skorlarını hesaplamak için başlangıç değerleri
       total_score = 0.0
       harmony_score = 0.0
       challenge_score = 0.0
       
       # Önemli gezegenler için ayrı skorlar
       sun_score = 0.0
       moon_score = 0.0
       venus_score = 0.0
       mars_score = 0.0
       mercury_score = 0.0
       
       # Açı sayaçları
       total_aspects = len(aspects)
       harmonious_aspects = 0
       challenging_aspects = 0
       
       # Eğer hiç açı yoksa, varsayılan değerleri döndür
       if total_aspects == 0:
           return {
               'total_score': 50.0,  # Orta değer
               'harmony_score': 50.0,
               'challenge_score': 50.0,
               'total_aspects': 0,
               'harmonious_aspects': 0,
               'challenging_aspects': 0,
               'sun_moon_aspects': [],
               'venus_mars_aspects': [],
               'mercury_aspects': [],
               'compatibility_rating': "Belirlenemedi (yeterli açı yok)"
           }
       
       # Önemli açı kombinasyonları
       sun_moon_aspects = []
       venus_mars_aspects = []
       mercury_aspects = []
       
       # Her bir açı için skorları hesapla
       for aspect in aspects:
           planet1 = aspect['chart1_planet']
           planet2 = aspect['chart2_planet']
           aspect_type = aspect['aspect_type']
           aspect_nature = aspect['nature']
           aspect_strength = aspect['strength']
           
           # Açının puanını hesapla
           aspect_score = aspect_strength * 10.0  # 0-10 arası bir değer
           
           # Açı tipine göre skor ayarla
           if aspect_nature == 'harmonious':
               harmony_score += aspect_score
               harmonious_aspects += 1
               
               # Zorlu açıları da biraz ekle (uyumluluk aynı zamanda zorlukları da içerir)
               challenge_score += aspect_score * 0.2
               
           elif aspect_nature == 'challenging':
               challenge_score += aspect_score
               challenging_aspects += 1
               
               # Uyumlu açıları da biraz ekle (zorluklar aynı zamanda büyüme fırsatları da sunar)
               harmony_score += aspect_score * 0.2
               
           elif aspect_nature == 'neutral':
               # Nötr açılar her iki skora da orta düzeyde etki eder
               harmony_score += aspect_score * 0.5
               challenge_score += aspect_score * 0.5
           
           # Toplam skoru güncelle
           total_score += aspect_score
           
           # Önemli gezegen kombinasyonlarını kontrol et
           
           # Güneş-Ay Bağlantıları (Temel uyumluluk)
           if (planet1 == 'sun' and planet2 == 'moon') or (planet1 == 'moon' and planet2 == 'sun'):
               sun_moon_aspects.append(aspect)
               
               # Güneş-Ay açıları 3 kat daha önemli
               sun_score += aspect_score * 3.0
               moon_score += aspect_score * 3.0
               
               if aspect_nature == 'harmonious':
                   total_score += aspect_score * 2.0  # Ekstra puan
               
           # Venüs-Mars Bağlantıları (Romantik/cinsel uyumluluk)
           elif (planet1 == 'venus' and planet2 == 'mars') or (planet1 == 'mars' and planet2 == 'venus'):
               venus_mars_aspects.append(aspect)
               
               # Venüs-Mars açıları 2 kat daha önemli
               venus_score += aspect_score * 2.0
               mars_score += aspect_score * 2.0
               
               if aspect_nature == 'harmonious':
                   total_score += aspect_score * 1.5  # Ekstra puan
               
           # Merkür Bağlantıları (İletişim uyumluluğu)
           elif planet1 == 'mercury' or planet2 == 'mercury':
               mercury_aspects.append(aspect)
               
               # Merkür açıları 1.5 kat daha önemli
               mercury_score += aspect_score * 1.5
           
           # Diğer gezegen kombinasyonları için spesifik skorlar
           if planet1 == 'sun' or planet2 == 'sun':
               sun_score += aspect_score
               
           if planet1 == 'moon' or planet2 == 'moon':
               moon_score += aspect_score
               
           if planet1 == 'venus' or planet2 == 'venus':
               venus_score += aspect_score
               
           if planet1 == 'mars' or planet2 == 'mars':
               mars_score += aspect_score
               
           if planet1 == 'mercury' or planet2 == 'mercury':
               mercury_score += aspect_score
       
       # Skorları normalize et (0-100 arası değerlere)
       max_possible_score = total_aspects * 10.0 * 3.0  # En yüksek olası puan (tüm açılar maksimum güçte ve önemli)
       
       total_score = min(100.0, (total_score / max_possible_score) * 100.0)
       harmony_score = min(100.0, (harmony_score / max_possible_score) * 100.0 * 2.0)
       challenge_score = min(100.0, (challenge_score / max_possible_score) * 100.0 * 2.0)
       
       # Gezegen skorlarını normalize et
       max_planet_score = total_aspects * 10.0 * 3.0 / 5.0  # Gezegen başına maksimum skor
       
       sun_score = min(100.0, (sun_score / max_planet_score) * 100.0)
       moon_score = min(100.0, (moon_score / max_planet_score) * 100.0)
       venus_score = min(100.0, (venus_score / max_planet_score) * 100.0)
       mars_score = min(100.0, (mars_score / max_planet_score) * 100.0)
       mercury_score = min(100.0, (mercury_score / max_planet_score) * 100.0)
       
       # Uyumluluk derecelendirmesini belirle
       compatibility_rating = self._get_compatibility_rating(total_score, harmony_score, challenge_score)
       
       return {
           'total_score': total_score,
           'harmony_score': harmony_score,
           'challenge_score': challenge_score,
           'sun_score': sun_score,
           'moon_score': moon_score,
           'venus_score': venus_score,
           'mars_score': mars_score,
           'mercury_score': mercury_score,
           'total_aspects': total_aspects,
           'harmonious_aspects': harmonious_aspects,
           'challenging_aspects': challenging_aspects,
           'sun_moon_aspects': sun_moon_aspects,
           'venus_mars_aspects': venus_mars_aspects,
           'mercury_aspects': mercury_aspects,
           'compatibility_rating': compatibility_rating
       }
   
    def _get_compatibility_rating(self, total_score, harmony_score, challenge_score):
       """
       Uyumluluk skorlarına göre derecelendirme belirler
       
       Args:
           total_score (float): Toplam uyumluluk skoru
           harmony_score (float): Uyumlu açıların skoru
           challenge_score (float): Zorlu açıların skoru
           
       Returns:
           str: Uyumluluk derecelendirmesi
       """
       # Skorlara göre derecelendirme belirleme
       if total_score >= 80.0:
           rating = "Mükemmel uyumluluk"
       elif total_score >= 70.0:
           rating = "Çok iyi uyumluluk"
       elif total_score >= 60.0:
           rating = "İyi uyumluluk"
       elif total_score >= 50.0:
           rating = "Orta düzey uyumluluk"
       elif total_score >= 40.0:
           rating = "İlginç dinamikler içeren uyumluluk"
       elif total_score >= 30.0:
           rating = "Zorlayıcı uyumluluk"
       else:
           rating = "Zor uyumluluk"
       
       # Uyum ve zorluk dengesine göre ek açıklamalar
       if harmony_score > 75.0 and challenge_score < 30.0:
           rating += " (Çok uyumlu ancak büyüme fırsatları az)"
       elif harmony_score < 30.0 and challenge_score > 75.0:
           rating += " (Yoğun zorluklar içeren, büyüme potansiyeli yüksek)"
       elif harmony_score > 60.0 and challenge_score > 60.0:
           rating += " (Hem uyumlu hem dinamik, dengeli)"
       
       return rating