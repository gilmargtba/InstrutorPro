"""Validate public service points against the bundled IBGE UF map."""

import json
from functools import lru_cache
from pathlib import Path

from django.contrib.gis.geos import GEOSGeometry, Point

from .models import FederativeUnit


@lru_cache(maxsize=1)
def _uf_geometries():
    source = Path(__file__).resolve().parent / "data" / "br-ufs.geojson"
    with source.open(encoding="utf-8") as file:
        features = json.load(file)["features"]
    return {
        feature["properties"]["codarea"]: GEOSGeometry(json.dumps(feature["geometry"]), srid=4326)
        for feature in features
    }


def public_point_in_uf(*, latitude: float, longitude: float, uf: str) -> bool:
    """The submitted public point must be inside the declared Brazilian UF."""
    ibge_code = FederativeUnit.objects.filter(code=uf).values_list("ibge_code", flat=True).first()
    geometry = _uf_geometries().get(ibge_code)
    return bool(geometry and geometry.covers(Point(longitude, latitude, srid=4326)))
