from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


class MapTileUnavailable(Exception):
    pass


def fetch_map_tile(*, zoom: int, x: int, y: int) -> tuple[bytes, str]:
    if zoom < 0 or zoom > 19 or x < 0 or y < 0 or x >= 2**zoom or y >= 2**zoom:
        raise ValueError("Tile coordinates are outside the supported range")
    if not settings.MAPTILER_API_KEY:
        raise MapTileUnavailable("MapTiler API key is not configured")
    base_url = settings.MAPTILER_MAP_URL.rstrip("/")
    query = urlencode({"key": settings.MAPTILER_API_KEY})
    request = Request(
        f"{base_url}/{zoom}/{x}/{y}.png?{query}",
        headers={"User-Agent": "InstrutorProCNH/1.0", "Accept": "image/png,image/*"},
    )
    try:
        with urlopen(request, timeout=settings.GEOCODING_TIMEOUT_SECONDS) as response:  # noqa: S310
            return response.read(), response.headers.get_content_type()
    except (HTTPError, URLError, TimeoutError) as exc:
        raise MapTileUnavailable from exc
