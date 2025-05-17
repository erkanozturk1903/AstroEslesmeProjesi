# astro_core/models/mixins.py

class TranslatableMixin:
    """Çevirisi olan modeller için mixin sınıfı"""
    
    def get_translation(self, language_code='tr'):
        """
        Belirtilen dildeki çeviriyi döndürür. 
        Yoksa sırasıyla tr, en veya ilk çeviriyi döndürür.
        """
        try:
            # Belirtilen dilde çeviri ara
            translation = self.translations.filter(language=language_code).first()
            if translation:
                return translation
                
            # Türkçe çeviri dene
            tr_translation = self.translations.filter(language='tr').first()
            if tr_translation:
                return tr_translation
                
            # İngilizce çeviri dene
            en_translation = self.translations.filter(language='en').first()
            if en_translation:
                return en_translation
                
            # Herhangi bir çeviri
            return self.translations.first()
                
        except (AttributeError, Exception):
            # Hiçbir çeviri yoksa veya hata durumunda None yerine boş bir çeviri nesnesi döndür
            # Bu, admin panelindeki hataları önler
            return self._get_empty_translation()
    
    def _get_empty_translation(self):
        """Boş bir çeviri nesnesi döndürür"""
        class EmptyTranslation:
            def __init__(self):
                self.name = f"{self.__class__.__name__} #{getattr(self, 'id', 'New')}"
                self.description = ""
                self.keywords = ""
                # Diğer olası çeviri alanları...
                
            def __bool__(self):
                return False  # Bu nesne if koşullarında False olarak değerlendirilir
                
        return EmptyTranslation()