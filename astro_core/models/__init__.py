from .user import UserProfile
from django.db import models

from .astrology import (
    Sign, SignTranslation,
    Planet, PlanetTranslation,
    House, HouseTranslation,
    Aspect, AspectTranslation,
    PlanetInSign, PlanetInSignTranslation,
    PlanetInHouse, PlanetInHouseTranslation,
    PlanetAspect, PlanetAspectTranslation,
    BirthChart, BirthChartTranslation,
    AstrologicalSystem, AstrologicalSystemTranslation
)

from .tarot import (
    TarotCard, TarotDeck, TarotSpread, TarotReading, TarotCardPosition
)

from .numerology import (
    NumerologyProfile, LifePathNumber, DestinyNumber, PersonalYearNumber,
    NumberMeaning
)

from .compatibility import (
    CompatibilityScore, RelationshipAspect, SignCompatibility
)

