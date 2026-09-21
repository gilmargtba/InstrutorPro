import io
import json
from unittest.mock import patch

import pytest

from apps.discovery.geocoding import (
    LocationNotFound,
    MapTilerGeocodingProvider,
    ProviderUnavailable,
)


def test_provider_requires_backend_secret(settings):
    settings.MAPTILER_API_KEY = ""
    with pytest.raises(ProviderUnavailable):
        MapTilerGeocodingProvider().geocode("Goiânia, GO")


def test_maptiler_parses_real_structured_locality_and_limits_to_brazil(settings):
    settings.MAPTILER_API_KEY = "test-secret"
    payload = {
        "features": [
            {
                "id": "municipality.5208707",
                "text": "Goiânia",
                "place_name": "Goiânia, Goiás, Brasil",
                "place_type": ["municipality"],
                "center": [-49.2643, -16.6869],
                "bbox": [-49.5, -16.9, -49.0, -16.4],
                "context": [{"id": "region.GO", "properties": {"short_code": "BR-GO"}}],
            }
        ]
    }
    response = io.BytesIO(json.dumps(payload).encode())
    response.__enter__ = lambda value: value
    response.__exit__ = lambda *args: None
    with patch("apps.discovery.geocoding.urlopen", return_value=response) as mocked:
        result = MapTilerGeocodingProvider().geocode("Goiânia, GO")[0]
    assert (result.city, result.uf, result.latitude, result.longitude) == (
        "Goiânia",
        "GO",
        -16.6869,
        -49.2643,
    )
    called_url = mocked.call_args.args[0].full_url
    assert "country=br" in called_url and "test-secret" in called_url


def test_maptiler_infers_uf_from_full_region_name_when_short_code_is_absent(settings):
    settings.MAPTILER_API_KEY = "test-secret"
    payload = {
        "features": [
            {
                "id": "municipality.76654",
                "text": "Goiatuba",
                "place_name": "Goiatuba, Goiás, Brasil",
                "place_type": ["municipality"],
                "center": [-49.36405934393406, -18.015457559680755],
                "context": [{"id": "region.52", "text": "Goiás"}],
            }
        ]
    }
    response = io.BytesIO(json.dumps(payload).encode())
    response.__enter__ = lambda value: value
    response.__exit__ = lambda *args: None
    with patch("apps.discovery.geocoding.urlopen", return_value=response):
        result = MapTilerGeocodingProvider().geocode("Goiatuba, GO, Brasil")[0]
    assert (result.city, result.uf, result.latitude, result.longitude) == (
        "Goiatuba",
        "GO",
        -18.015457559680755,
        -49.36405934393406,
    )


def test_maptiler_infers_uf_from_label_when_region_context_is_absent(settings):
    settings.MAPTILER_API_KEY = "test-secret"
    payload = {
        "features": [
            {
                "id": "municipality.76654",
                "text": "Goiatuba",
                "place_name": "Goiatuba, Goiás, Brasil",
                "place_type": ["municipality"],
                "center": [-49.36405934393406, -18.015457559680755],
            }
        ]
    }
    response = io.BytesIO(json.dumps(payload).encode())
    response.__enter__ = lambda value: value
    response.__exit__ = lambda *args: None
    with patch("apps.discovery.geocoding.urlopen", return_value=response):
        result = MapTilerGeocodingProvider().geocode("Goiatuba, GO, Brasil")[0]
    assert result.uf == "GO"


@pytest.mark.parametrize(
    ("query", "encoded_cep"),
    [("88000-000", "88000-000"), ("88000000", "88000-000")],
)
def test_cep_preserves_maptiler_postal_code_format(settings, query, encoded_cep):
    settings.MAPTILER_API_KEY = "test-secret"
    response = io.BytesIO(b'{"features": []}')
    response.__enter__ = lambda value: value
    response.__exit__ = lambda *args: None
    with patch("apps.discovery.geocoding.urlopen", return_value=response) as mocked:
        with pytest.raises(LocationNotFound):
            MapTilerGeocodingProvider().geocode(query)
    assert encoded_cep in mocked.call_args.args[0].full_url
