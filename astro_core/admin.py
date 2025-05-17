from django.contrib import admin

# Astrology models
try:
    from .models.astrology import (
        AstrologicalSystem, AstrologicalSystemTranslation,
        Sign, SignTranslation,
        Planet, PlanetTranslation,
        House, HouseTranslation,
        Aspect, AspectTranslation,
        PlanetInSign, PlanetInSignTranslation,
        PlanetInHouse, PlanetInHouseTranslation,
        PlanetAspect, PlanetAspectTranslation,
        BirthChart, BirthChartTranslation,
    )
except ImportError:
    # Eğer modeller henüz doğru konumda yapılandırılmadıysa, eski import yöntemiyle deneyin
    from .models import (
        AstrologicalSystem, AstrologicalSystemTranslation,
        Sign, SignTranslation,
        Planet, PlanetTranslation,
        House, HouseTranslation,
        Aspect, AspectTranslation,
        PlanetInSign, PlanetInSignTranslation,
        PlanetInHouse, PlanetInHouseTranslation,
        PlanetAspect, PlanetAspectTranslation,
        BirthChart, BirthChartTranslation,
    )

# Tarot models
try:
    from .models.tarot import (
        TarotDeck, TarotCard, TarotSpread, TarotCardPosition, TarotReading,
    )
except ImportError:
    # Eğer modeller henüz doğru konumda yapılandırılmadıysa
    from .models import (
        TarotDeck, TarotCard, TarotSpread, TarotCardPosition, TarotReading,
    )

# Numerology models
try:
    from .models.numerology import (
        NumberMeaning, NumerologyProfile, LifePathNumber, DestinyNumber,
        PersonalYearNumber,
    )
except ImportError:
    from .models import (
        NumberMeaning, NumerologyProfile, LifePathNumber, DestinyNumber,
        PersonalYearNumber,
    )

# Compatibility models
try:
    from .models.compatibility import (
        SignCompatibility, RelationshipAspect, CompatibilityScore
    )
except ImportError:
    from .models import (
        SignCompatibility, RelationshipAspect, CompatibilityScore
    )

# User models
try:
    from .models.user import UserProfile
except ImportError:
    from .models import UserProfile

# User Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'birth_place')
    search_fields = ('user__username', 'birth_place')

# Translation Inlines
class AstrologicalSystemTranslationInline(admin.TabularInline):
    model = AstrologicalSystemTranslation
    extra = 1
    min_num = 1

class SignTranslationInline(admin.TabularInline):
    model = SignTranslation
    extra = 1
    min_num = 1

class PlanetTranslationInline(admin.TabularInline):
    model = PlanetTranslation
    extra = 1
    min_num = 1

class HouseTranslationInline(admin.TabularInline):
    model = HouseTranslation
    extra = 1
    min_num = 1

class AspectTranslationInline(admin.TabularInline):
    model = AspectTranslation
    extra = 1
    min_num = 1

class PlanetInSignTranslationInline(admin.TabularInline):
    model = PlanetInSignTranslation
    extra = 1
    min_num = 1

class PlanetInHouseTranslationInline(admin.TabularInline):
    model = PlanetInHouseTranslation
    extra = 1
    min_num = 1

class PlanetAspectTranslationInline(admin.TabularInline):
    model = PlanetAspectTranslation
    extra = 1
    min_num = 1

class BirthChartTranslationInline(admin.TabularInline):
    model = BirthChartTranslation
    extra = 1
    min_num = 1

# Astrology Admin
@admin.register(AstrologicalSystem)
class AstrologicalSystemAdmin(admin.ModelAdmin):
    list_display = ('display_name',)
    search_fields = ('translations__name', 'translations__description')
    inlines = [AstrologicalSystemTranslationInline]
    
    def display_name(self, obj):
        try:
            translation = obj.get_translation()
            return translation.name if translation and hasattr(translation, 'name') else f"System #{obj.id}"
        except Exception:
            return f"System #{obj.id}"
    display_name.short_description = "Sistem Adı"

@admin.register(Sign)
class SignAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'system', 'element', 'modality', 'ruling_planet', 'start_date', 'end_date')
    list_filter = ('system', 'element', 'modality')
    search_fields = ('translations__name', 'translations__keywords', 'translations__description')
    inlines = [SignTranslationInline]
    
    def display_name(self, obj):
        try:
            translation = obj.get_translation()
            return translation.name if translation and hasattr(translation, 'name') else f"Sign #{obj.id}"
        except Exception:
            return f"Sign #{obj.id}"
    display_name.short_description = "Burç Adı"
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('system', 'element', 'modality', 'ruling_planet')
        }),
        ('Tarihler', {
            'fields': ('start_date', 'end_date'),
            'description': 'Tarihler GG/AA formatında olmalıdır (örn: 21/03 - 21 Mart)'
        }),
        ('Medya', {
            'fields': ('image',),
            'classes': ('collapse',)  # Bu bölüm varsayılan olarak kapalı olacak
        }),
    )

@admin.register(Planet)
class PlanetAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'system', 'display_symbol')
    list_filter = ('system',)
    search_fields = ('translations__name', 'translations__keywords', 'translations__description')
    inlines = [PlanetTranslationInline]
    
    def display_name(self, obj):
        try:
            translation = obj.get_translation()
            return translation.name if translation and hasattr(translation, 'name') else f"Planet #{obj.id}"
        except Exception:
            return f"Planet #{obj.id}"
    display_name.short_description = "Gezegen Adı"
    
    def display_symbol(self, obj):
        try:
            translation = obj.get_translation()
            return translation.symbol if translation and hasattr(translation, 'symbol') else ""
        except Exception:
            return ""
    display_symbol.short_description = "Sembol"
    
    filter_horizontal = ('rulership', 'detriment')

@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('number', 'display_name', 'system', 'natural_sign')
    list_filter = ('system',)
    search_fields = ('translations__name', 'translations__keywords', 'translations__description')
    inlines = [HouseTranslationInline]
    
    def display_name(self, obj):
        try:
            translation = obj.get_translation()
            return translation.name if translation and hasattr(translation, 'name') else f"House #{obj.id}"
        except Exception:
            return f"House #{obj.id}"
    display_name.short_description = "Ev Adı"

@admin.register(Aspect)
class AspectAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'system', 'degrees', 'orb', 'display_nature')
    list_filter = ('system',)
    search_fields = ('translations__name', 'translations__keywords', 'translations__description')
    inlines = [AspectTranslationInline]
    
    def display_name(self, obj):
        try:
            translation = obj.get_translation()
            return translation.name if translation and hasattr(translation, 'name') else f"Aspect {obj.degrees}°"
        except Exception:
            return f"Aspect {obj.degrees}°"
    display_name.short_description = "Açı Adı"
    
    def display_nature(self, obj):
        try:
            translation = obj.get_translation()
            return translation.nature if translation and hasattr(translation, 'nature') else ""
        except Exception:
            return ""
    display_nature.short_description = "Doğası"

@admin.register(PlanetInSign)
class PlanetInSignAdmin(admin.ModelAdmin):
    list_display = ('display_planet', 'display_sign', 'system')
    list_filter = ('system', 'planet', 'sign')
    search_fields = ('translations__general_interpretation', 'translations__personality_traits')
    inlines = [PlanetInSignTranslationInline]
    
    def display_planet(self, obj):
        try:
            planet_trans = obj.planet.get_translation()
            return planet_trans.name if planet_trans and hasattr(planet_trans, 'name') else f"Planet #{obj.planet.id}"
        except Exception:
            return f"Planet #{obj.planet.id}"
    display_planet.short_description = "Gezegen"
    
    def display_sign(self, obj):
        try:
            sign_trans = obj.sign.get_translation()
            return sign_trans.name if sign_trans and hasattr(sign_trans, 'name') else f"Sign #{obj.sign.id}"
        except Exception:
            return f"Sign #{obj.sign.id}"
    display_sign.short_description = "Burç"

@admin.register(PlanetInHouse)
class PlanetInHouseAdmin(admin.ModelAdmin):
    list_display = ('display_planet', 'house', 'system')
    list_filter = ('system', 'planet', 'house')
    search_fields = ('translations__general_interpretation', 'translations__life_areas_affected')
    inlines = [PlanetInHouseTranslationInline]
    
    def display_planet(self, obj):
        try:
            planet_trans = obj.planet.get_translation()
            return planet_trans.name if planet_trans and hasattr(planet_trans, 'name') else f"Planet #{obj.planet.id}"
        except Exception:
            return f"Planet #{obj.planet.id}"
    display_planet.short_description = "Gezegen"

@admin.register(PlanetAspect)
class PlanetAspectAdmin(admin.ModelAdmin):
    list_display = ('display_planet1', 'display_aspect', 'display_planet2', 'system')
    list_filter = ('system', 'planet1', 'planet2', 'aspect')
    search_fields = ('translations__general_interpretation',)
    inlines = [PlanetAspectTranslationInline]
    
    def display_planet1(self, obj):
        try:
            planet_trans = obj.planet1.get_translation()
            return planet_trans.name if planet_trans and hasattr(planet_trans, 'name') else f"Planet #{obj.planet1.id}"
        except Exception:
            return f"Planet #{obj.planet1.id}"
    display_planet1.short_description = "1. Gezegen"
    
    def display_aspect(self, obj):
        try:
            aspect_trans = obj.aspect.get_translation()
            return aspect_trans.name if aspect_trans and hasattr(aspect_trans, 'name') else f"Aspect {obj.aspect.degrees}°"
        except Exception:
            return f"Aspect {obj.aspect.degrees}°" if hasattr(obj, 'aspect') and hasattr(obj.aspect, 'degrees') else "Aspect"
    display_aspect.short_description = "Açı"
    
    def display_planet2(self, obj):
        try:
            planet_trans = obj.planet2.get_translation()
            return planet_trans.name if planet_trans and hasattr(planet_trans, 'name') else f"Planet #{obj.planet2.id}"
        except Exception:
            return f"Planet #{obj.planet2.id}"
    display_planet2.short_description = "2. Gezegen"

@admin.register(BirthChart)
class BirthChartAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'birth_date', 'display_birth_place', 'system')
    list_filter = ('system',)
    search_fields = ('translations__name', 'user__username', 'translations__birth_place')
    date_hierarchy = 'birth_date'
    inlines = [BirthChartTranslationInline]
    
    def display_name(self, obj):
        try:
            translation = obj.get_translation()
            return translation.name if translation and hasattr(translation, 'name') else obj.name
        except Exception:
            return obj.name if hasattr(obj, 'name') else f"Chart #{obj.id}"
    display_name.short_description = "Harita Adı"
    
    def display_birth_place(self, obj):
        try:
            translation = obj.get_translation()
            return translation.birth_place if translation and hasattr(translation, 'birth_place') else obj.birth_place
        except Exception:
            return obj.birth_place if hasattr(obj, 'birth_place') else ""
    display_birth_place.short_description = "Doğum Yeri"

# Translation models admin
@admin.register(AstrologicalSystemTranslation)
class AstrologicalSystemTranslationAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'system')
    list_filter = ('language', 'system')
    search_fields = ('name', 'description')

@admin.register(SignTranslation)
class SignTranslationAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'sign')
    list_filter = ('language', 'sign__system')
    search_fields = ('name', 'keywords', 'description')

@admin.register(PlanetTranslation)
class PlanetTranslationAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'planet')
    list_filter = ('language', 'planet__system')
    search_fields = ('name', 'keywords', 'description')

@admin.register(HouseTranslation)
class HouseTranslationAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'house')
    list_filter = ('language', 'house__system')
    search_fields = ('name', 'keywords', 'description')

@admin.register(AspectTranslation)
class AspectTranslationAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'aspect')
    list_filter = ('language', 'aspect__system')
    search_fields = ('name', 'keywords', 'description')

# Tarot Admin
@admin.register(TarotDeck)
class TarotDeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'year_created')
    search_fields = ('name', 'creator', 'description')

@admin.register(TarotCard)
class TarotCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'deck', 'card_type', 'number')
    list_filter = ('deck', 'card_type')
    search_fields = ('name', 'keywords', 'description')

@admin.register(TarotSpread)
class TarotSpreadAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_cards')
    search_fields = ('name', 'description')

@admin.register(TarotCardPosition)
class TarotCardPositionAdmin(admin.ModelAdmin):
    list_display = ('spread', 'position_number', 'name')
    list_filter = ('spread',)
    search_fields = ('name', 'description')

@admin.register(TarotReading)
class TarotReadingAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'deck', 'spread', 'date_created')
    list_filter = ('deck', 'spread')
    search_fields = ('name', 'user__username', 'question')
    date_hierarchy = 'date_created'

# Numerology Admin
@admin.register(NumberMeaning)
class NumberMeaningAdmin(admin.ModelAdmin):
    list_display = ('number', 'name')
    search_fields = ('number', 'name', 'keywords', 'general_meaning')

@admin.register(NumerologyProfile)
class NumerologyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_name', 'life_path_number', 'destiny_number')
    search_fields = ('user__username', 'birth_name')

@admin.register(LifePathNumber)
class LifePathNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)
    search_fields = ('number', 'description', 'strengths', 'challenges')

@admin.register(DestinyNumber)
class DestinyNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)
    search_fields = ('number', 'description', 'talents', 'life_lessons')

@admin.register(PersonalYearNumber)
class PersonalYearNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)
    search_fields = ('number', 'description', 'opportunities', 'challenges')

# Compatibility Admin
@admin.register(SignCompatibility)
class SignCompatibilityAdmin(admin.ModelAdmin):
    list_display = ('sign1', 'sign2', 'system', 'compatibility_score')
    list_filter = ('system', 'compatibility_score')
    search_fields = ('overall_compatibility', 'romantic_compatibility')

@admin.register(RelationshipAspect)
class RelationshipAspectAdmin(admin.ModelAdmin):
    list_display = ('planet1', 'aspect', 'planet2', 'system')
    list_filter = ('system', 'planet1', 'planet2', 'aspect')
    search_fields = ('interpretation', 'romantic_impact')

@admin.register(CompatibilityScore)
class CompatibilityScoreAdmin(admin.ModelAdmin):
    list_display = ('chart1', 'chart2', 'overall_score')
    list_filter = ('overall_score',)
    search_fields = ('summary', 'strengths', 'challenges')