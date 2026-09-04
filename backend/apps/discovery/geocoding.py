import json
import re
from dataclasses import asdict, dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from django.conf import settings


class GeocodingError(Exception):
    code = "geocoding_error"


class LocationNotFound(GeocodingError):
    code = "location_not_found"


class ProviderUnavailable(GeocodingError):
    code = "provider_unavailable"


@dataclass(frozen=True)
class GeocodingResult:
    id: str
    label: str
    latitude: float
    longitude: float
    place_type: str
    city: str = ""
    uf: str = ""
    bbox: tuple[float, float, float, float] | None = None

    def public_dict(self):
        return asdict(self)


class GeocodingProvider:
    code = "ABSTRACT"

    def geocode(self, query: str, *, limit: int = 5) -> list[GeocodingResult]:
        raise NotImplementedError


class MapTilerGeocodingProvider(GeocodingProvider):
    """Backend-only provider adapter; never a source of publication truth."""

    code = "MAPTILER"
    _cep = re.compile(r"^\d{5}-?\d{3}$")

    def __init__(self, *, api_key=None, base_url=None, timeout=None):
        self.api_key = api_key or settings.MAPTILER_API_KEY
        self.base_url = (base_url or settings.MAPTILER_GEOCODING_URL).rstrip("/")
        self.timeout = timeout or settings.GEOCODING_TIMEOUT_SECONDS

    def geocode(self, query: str, *, limit: int = 5) -> list[GeocodingResult]:
        if not self.api_key:
            raise ProviderUnavailable("MapTiler API key is not configured")
        clean = query.strip()
        if self._cep.fullmatch(clean):
            clean = clean if "-" in clean else f"{clean[:5]}-{clean[5:]}"
        params = urlencode(
            {
                "key": self.api_key,
                "country": "br",
                "language": "pt",
                "limit": min(max(limit, 1), 10),
                "autocomplete": "true",
            }
        )
        request = Request(
            f"{self.base_url}/{quote(clean, safe='')}.json?{params}",
            headers={"User-Agent": "InstrutorProCNH/1.0", "Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:  # noqa: S310
                payload = json.load(response)
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            raise ProviderUnavailable from exc
        results = [self._parse(feature) for feature in payload.get("features", [])]
        results = [result for result in results if result]
        if not results:
            raise LocationNotFound
        return results

    @staticmethod
    def _parse(feature):
        center = feature.get("center") or feature.get("geometry", {}).get("coordinates")
        if not center or len(center) < 2:
            return None
        city, uf = "", ""
        for item in [feature, *feature.get("context", [])]:
            item_id = item.get("id", "")
            if item_id.startswith(("municipality.", "place.")) and not city:
                city = item.get("text") or item.get("place_name", "").split(",")[0]
            short = item.get("properties", {}).get("short_code", "")
            if short.upper().startswith("BR-"):
                uf = short.split("-")[-1].upper()
        raw_bbox = feature.get("bbox")
        return GeocodingResult(
            str(feature.get("id", "")),
            feature.get("place_name") or feature.get("text", ""),
            float(center[1]),
            float(center[0]),
            (feature.get("place_type") or ["place"])[0],
            city,
            uf,
            tuple(float(v) for v in raw_bbox[:4]) if raw_bbox else None,
        )


def get_geocoding_provider():
    return MapTilerGeocodingProvider()
