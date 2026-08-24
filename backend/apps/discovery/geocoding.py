from dataclasses import dataclass


class GeocodingError(Exception):
    code = "geocoding_error"


class LocationNotFound(GeocodingError):
    code = "location_not_found"


@dataclass(frozen=True)
class GeocodingResult:
    label: str
    latitude: float
    longitude: float


class GeocodingProvider:
    def geocode(self, query: str) -> list[GeocodingResult]:
        raise NotImplementedError


class DemoGeocodingProvider(GeocodingProvider):
    """Deterministic, offline city catalog. Sends no query to a third party."""

    LOCATIONS = {
        "porto alegre": GeocodingResult("Porto Alegre, RS", -30.0346, -51.2177),
        "florianopolis": GeocodingResult("Florianópolis, SC", -27.5949, -48.5482),
        "sao paulo": GeocodingResult("São Paulo, SP", -23.5505, -46.6333),
        "rio de janeiro": GeocodingResult("Rio de Janeiro, RJ", -22.9068, -43.1729),
        "vitoria": GeocodingResult("Vitória, ES", -20.3155, -40.3128),
    }

    def geocode(self, query: str) -> list[GeocodingResult]:
        normalized = query.strip().lower().translate(str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc"))
        result = self.LOCATIONS.get(normalized)
        if not result:
            raise LocationNotFound
        return [result]
