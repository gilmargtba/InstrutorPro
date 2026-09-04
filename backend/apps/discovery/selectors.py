from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Count, Min, Q
from django.utils import timezone

from .models import InstructorProfile


def published_instructor_profiles():
    now = timezone.now()
    data_filter = (
        {"is_demo": True} if settings.SYNTHETIC_MARKETPLACE_ENABLED else {"is_demo": False}
    )
    if (
        not settings.SYNTHETIC_MARKETPLACE_ENABLED
        and not settings.REAL_INSTRUCTOR_PUBLICATION_ENABLED
    ):
        return InstructorProfile.objects.none()
    return (
        InstructorProfile.objects.filter(
            **data_filter,
            profile_status="APPROVED",
            verification_status="VERIFIED",
            publication_status="APPROVED",
            person__account__lifecycle_status="ACTIVE",
            person__account__is_active=True,
            person__role_assignments__role="INSTRUCTOR",
            person__role_assignments__revoked_at__isnull=True,
            service_area__location_authorized=True,
        )
        .filter(Q(verified_until__isnull=True) | Q(verified_until__gt=now))
        .distinct()
    )


def published_instructor_counts_by_uf():
    return (
        published_instructor_profiles()
        .values("service_area__uf")
        .annotate(total=Count("id"), search_location=Min("service_area__city"))
        .order_by("service_area__uf")
    )


def search_published_instructors(
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
    return (
        queryset.select_related("service_area")
        .prefetch_related("profile_photos", "documents__requirement")
        .annotate(distance=Distance("service_area__public_service_location", origin))
        .order_by("distance", "id")[: settings.INSTRUCTOR_SEARCH_MAX_RESULTS]
    )


search_demo_instructors = search_published_instructors
