import pytest

from app.services.geolocation import GeolocationService
from app.types import Location


def test_distancia_no_mesmo_ponto():
    ponto = Location(latitude=-7.115, longitude=-34.873)
    assert GeolocationService().calculate_distance(ponto, ponto) == 0


def test_distancia_em_quilometros():
    a = Location(latitude=0, longitude=0)
    b = Location(latitude=0, longitude=1)
    service = GeolocationService()
    assert service.calculate_distance(a, b) == pytest.approx(111.2, abs=0.1)
    assert service.calculate_distance(a, b) == service.calculate_distance(b, a)
