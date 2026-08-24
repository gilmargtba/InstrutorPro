from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q
from django.utils import timezone

from .models import InstructorProfile


def published_instructor_profiles():
    now = timezone.now()
    return (
        InstructorProfile.objects.filter(
            is_demo=True,
            profile_status="APPROVED",
            verification_status="VERIFIED",
            publication_status="APPROVED",
            person__account__lifecycle_status="ACTIVE",
            person__account__is_active=True,
            person__role_assignments__role="INSTRUCTOR",
            person__role_assignments__revoked_at__isnull=True,
            service_area__location_authorized=True,
            service_area__uf__in=["RS", "SC", "SP", "RJ", "ES"],
        )
        .filter(Q(verified_until__isnull=True) | Q(verified_until__gt=now))
        .distinct()
    )


def search_demo_instructors(
    *, latitude, longitude, radius_km, category, transmission=None, vehicle_available=None
):
    origin = Point(float(longitude), float(latitude), srid=4326)
    queryset = published_instructor_profiles().filter(
        service_area__public_service_location__distance_lte=(origin, D(km=float(radius_km))),
        categories__contains=[category],
    )
    if transmission:
        queryset = queryset.filter(transmission_options__contains=[transmission])
    if vehicle_available is not None:
        queryset = queryset.filter(vehicle_available=vehicle_available)
    return queryset.annotate(
        distance=Distance("service_area__public_service_location", origin)
    ).order_by("distance", "id")
