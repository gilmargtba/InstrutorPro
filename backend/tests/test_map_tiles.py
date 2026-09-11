from io import BytesIO
from unittest.mock import patch

import pytest

from apps.discovery.map_tiles import MapTileUnavailable, fetch_map_tile


class _Headers:
    def get_content_type(self):
        return "image/png"


class _Response(BytesIO):
    headers = _Headers()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


@pytest.mark.django_db
def test_public_map_tile_proxies_without_exposing_key(client, settings):
    settings.MAPTILER_API_KEY = "private-test-key"
    with patch("apps.discovery.map_tiles.urlopen", return_value=_Response(b"png")) as mocked:
        response = client.get("/api/v1/map/tiles/4/5/6.png")
    assert response.status_code == 200
    assert response.content == b"png"
    assert response["Content-Type"] == "image/png"
    assert response["Cache-Control"] == "public, max-age=3600"
    assert "private-test-key" not in response.content.decode(errors="ignore")
    assert "private-test-key" in mocked.call_args.args[0].full_url


@pytest.mark.django_db
def test_public_map_tile_rejects_invalid_coordinates(client):
    response = client.get("/api/v1/map/tiles/4/16/0.png")
    assert response.status_code == 400


@pytest.mark.django_db
def test_public_map_tile_returns_stable_provider_failure(client, settings):
    settings.MAPTILER_API_KEY = ""
    response = client.get("/api/v1/map/tiles/4/5/6.png")
    assert response.status_code == 502
    assert response.json() == {"detail": "Map tile provider unavailable."}


def test_fetch_map_tile_rejects_provider_failure(settings):
    settings.MAPTILER_API_KEY = "private-test-key"
    with patch("apps.discovery.map_tiles.urlopen", side_effect=TimeoutError):
        with pytest.raises(MapTileUnavailable):
            fetch_map_tile(zoom=4, x=5, y=6)
