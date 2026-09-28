import io
import json
from unittest.mock import patch

import pytest

from apps.discovery.geocoding import (
    LocationNotFound,
    MapTilerGeocodingProvider,
    ProviderUnavailable,
    resolve_brazilian_uf,
)

BRAZILIAN_LOCALITIES = [
    ("Rio Branco", "Acre", "AC"),
    ("Maceió", "Alagoas", "AL"),
    ("Macapá", "Amapá", "AP"),
    ("Manaus", "Amazonas", "AM"),
    ("Salvador", "Bahia", "BA"),
    ("Fortaleza", "Ceará", "CE"),
    ("Brasília", "Distrito Federal", "DF"),
    ("Vitória", "Espírito Santo", "ES"),
    ("Goiânia", "Goiás", "GO"),
    ("São Luís", "Maranhão", "MA"),
    ("Cuiabá", "Mato Grosso", "MT"),
    ("Campo Grande", "Mato Grosso do Sul", "MS"),
    ("Belo Horizonte", "Minas Gerais", "MG"),
    ("Belém", "Pará", "PA"),
    ("João Pessoa", "Paraíba", "PB"),
    ("Curitiba", "Paraná", "PR"),
    ("Recife", "Pernambuco", "PE"),
    ("Teresina", "Piauí", "PI"),
    ("Rio de Janeiro", "Rio de Janeiro", "RJ"),
    ("Natal", "Rio Grande do Norte", "RN"),
    ("Porto Alegre", "Rio Grande do Sul", "RS"),
    ("Porto Velho", "Rondônia", "RO"),
    ("Boa Vista", "Roraima", "RR"),
    ("Florianópolis", "Santa Catarina", "SC"),
    ("São Paulo", "São Paulo", "SP"),
    ("Aracaju", "Sergipe", "SE"),
    ("Palmas", "Tocantins", "TO"),
]


@pytest.mark.parametrize(("city", "state", "uf"), BRAZILIAN_LOCALITIES)
def test_resolves_all_27_ufs_from_state_context(city, state, uf):
    feature = {
        "id": "place.123",
        "text": city,
        "place_name": f"{city}, {state}, Brasil",
        "center": [-47.88, -15.79],
        "context": [{"id": "subregion.123", "text": state}],
    }
    result = MapTilerGeocodingProvider._parse(feature)
    assert (result.city, result.uf) == (city, uf)
    assert result.public_dict()["uf_resolution"] == "RESOLVED"


@pytest.mark.parametrize("query", ["Brasília", "Brasília DF", "Brasília, DF"])
def test_brasilia_real_provider_shape_resolves_df(settings, query):
    settings.MAPTILER_API_KEY = "test-secret"
    payload = {
        "features": [
            {
                "id": "place.5139760",
                "text": "Brasília",
                "place_name": (
                    "Brasília, Região Integrada de Desenvolvimento "
                    "do Distrito Federal e Entorno, Brasil"
                ),
                "place_type": ["place"],
                "center": [-47.8825, -15.7942],
                "properties": {"country_code": "br"},
                "context": [
                    {
                        "id": "joint_municipality.1",
                        "text": "Região Integrada de Desenvolvimento do Distrito Federal e Entorno",
                    },
                    {"id": "subregion.62", "text": "Distrito Federal"},
                    {"id": "region.1474", "text": "Região Centro-Oeste"},
                    {"id": "country.1", "text": "Brasil"},
                ],
            }
        ]
    }
    response = io.BytesIO(json.dumps(payload).encode())
    with patch("apps.discovery.geocoding.urlopen", return_value=response):
        result = MapTilerGeocodingProvider().geocode(query)[0]
    assert (result.city, result.uf, result.latitude, result.longitude) == (
        "Brasília",
        "DF",
        -15.7942,
        -47.8825,
    )


def test_brasilia_postal_code_prefers_place_to_submunicipality():
    result = MapTilerGeocodingProvider._parse(
        {
            "id": "postal_code.70040-010",
            "text": "70040-010",
            "place_name": "70040-010, Brasília, Brasil",
            "center": [-47.88, -15.79],
            "context": [
                {"id": "municipality.90999", "text": "Plano Piloto"},
                {"id": "place.5139760", "text": "Brasília"},
                {"id": "subregion.62", "text": "Distrito Federal"},
            ],
        }
    )
    assert (result.city, result.uf) == ("Brasília", "DF")


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        (" BR-df ", "DF"),
        ("Federal District", "DF"),
        ("  goias ", "GO"),
        ("São   Paulo", "SP"),
        ("Região Integrada de Desenvolvimento do Distrito Federal e Entorno", ""),
        ("ZZ", ""),
    ],
)
def test_canonical_uf_normalizer(input_value, expected):
    assert resolve_brazilian_uf(input_value) == expected


def test_structured_region_code_and_conflict_fail_closed():
    feature = {
        "id": "place.1",
        "text": "Brasília",
        "center": [-47.88, -15.79],
        "context": [{"id": "subregion.62", "properties": {"region_code": "br-df"}}],
    }
    assert MapTilerGeocodingProvider._parse(feature).uf == "DF"
    feature["context"].append({"id": "region.1", "text": "São Paulo"})
    result = MapTilerGeocodingProvider._parse(feature)
    assert result.uf == ""
    assert result.public_dict()["uf_resolution"] == "NEEDS_CONFIRMATION"


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
