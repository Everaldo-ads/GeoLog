import haversine as hs
from ..types import Location

class GeolocationService:

    def calculate_distance(self, location1: Location, location2: Location):
        return hs.haversine(
            (location1.latitude, location1.longitude),
            (location2.latitude, location2.longitude)
        )