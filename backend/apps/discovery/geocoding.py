import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from django.conf import settings


def _normalized_region_name(value: str) -> str:
    normalized = "".join(
        character
        for character in unicodedata.normalize("NFKD", value).casefold()
        if not unicodedata.combining(character)
    )
    return " ".join(normalized.split())


_BRAZIL_STATE_CODES = {
    _normalized_region_name(name): code
    for name, code in {
        "Acre": "AC",
        "Alagoas": "AL",
        "Amapá": "AP",
        "Amazonas": "AM",
        "Bahia": "BA",
        "Ceará": "CE",
        "Distrito Federal": "DF",
        "Espírito Santo": "ES",
        "Goiás": "GO",
        "Maranhão": "MA",
        "Mato Grosso": "MT",
        "Mato Grosso do Sul": "MS",
        "Minas Gerais": "MG",
        "Pará": "PA",
        "Paraíba": "PB",
        "Paraná": "PR",
        "Pernambuco": "PE",
        "Piauí": "PI",
        "Rio de Janeiro": "RJ",
        "Rio Grande do Norte": "RN",
        "Rio Grande do Sul": "RS",
        "Rondônia": "RO",
        "Roraima": "RR",
        "Santa Catarina": "SC",
        "São Paulo": "SP",
        "Sergipe": "SE",
        "Tocantins": "TO",
    }.items()
}
_BRAZIL_STATE_CODES["federal district"] = "DF"
BRAZIL_UFS = frozenset(_BRAZIL_STATE_CODES.values())


def resolve_brazilian_uf(value: str | None) -> str:
    """Normalize an exact Brazilian state name or code; never guess from a substring."""
    if not isinstance(value, str):
        return ""
    normalized = _normalized_region_name(value)
    if normalized.startswith("br-"):
        normalized = normalized[3:]
    code = normalized.upper()
    return code if code in BRAZIL_UFS else _BRAZIL_STATE_CODES.get(normalized, "")


def _uf_from_feature(feature: dict) -> str:
    candidates = set()
    for item in [feature, *(feature.get("context") or [])]:
        item_type = str(item.get("id") or "").split(".", 1)[0]
        if item_type not in {"region", "subregion"}:
            continue
        properties = item.get("properties") or {}
        for raw in (
            properties.get("short_code"),
            properties.get("region_code"),
            item.get("short_code"),
            item.get("region_code"),
            item.get("text"),
            str(item.get("place_name") or "").split(",")[0],
        ):
            if code := resolve_brazilian_uf(raw):
                candidates.add(code)
    if not candidates:
        label = feature.get("place_name") or ""
        candidates = {code for part in label.split(",") if (code := resolve_brazilian_uf(part))}
    return next(iter(candidates)) if len(candidates) == 1 else ""


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
        return {**asdict(self), "uf_resolution": "RESOLVED" if self.uf else "NEEDS_CONFIRMATION"}


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
        city = ""
        items = [feature, *(feature.get("context") or [])]
        for prefix in ("place.", "municipality.", "locality."):
            item = next(
                (item for item in items if str(item.get("id") or "").startswith(prefix)), None
            )
            if item:
                city = item.get("text") or str(item.get("place_name") or "").split(",")[0]
                break
        label = feature.get("place_name") or feature.get("text", "")
        uf = _uf_from_feature(feature)
        raw_bbox = feature.get("bbox")
        return GeocodingResult(
            str(feature.get("id", "")),
            label,
            float(center[1]),
            float(center[0]),
            (feature.get("place_type") or ["place"])[0],
            city,
            uf,
            tuple(float(v) for v in raw_bbox[:4]) if raw_bbox else None,
        )


def get_geocoding_provider():
    return MapTilerGeocodingProvider()
