from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Count, Min, Q
from django.utils import timezone

from apps.marketplace.capabilities import enabled
from apps.territories.policies import approved_instructor_publication_ufs

from .models import InstructorProfile


def published_instructor_profiles():
    now = timezone.now()
    data_filter = (
        {"is_demo": True} if settings.SYNTHETIC_MARKETPLACE_ENABLED else {"is_demo": False}
    )
    if not settings.SYNTHETIC_MARKETPLACE_ENABLED and not enabled("REAL_MARKETPLACE_SEARCH"):
        return InstructorProfile.objects.none()
    queryset = InstructorProfile.objects.filter(
        **data_filter,
        profile_status="APPROVED",
        verification_status="VERIFIED",
        publication_status="APPROVED",
        person__account__lifecycle_status="ACTIVE",
        person__account__is_active=True,
        person__role_assignments__role="INSTRUCTOR",
        person__role_assignments__revoked_at__isnull=True,
        service_area__location_authorized=True,
    ).filter(Q(verified_until__isnull=True) | Q(verified_until__gt=now))
    if not settings.SYNTHETIC_MARKETPLACE_ENABLED:
        queryset = queryset.filter(
            service_area__uf__in=approved_instructor_publication_ufs().values("code")
        )
    return queryset.distinct()


def published_instructor_counts_by_uf():
    return (
        published_instructor_profiles()
        .values("service_area__uf")
        .annotate(total=Count("id"), search_location=Min("service_area__city"))
        .order_by("service_area__uf")
    )


def search_published_instructors(
    *,
    latitude,
    longitude,
    uf=None,
    category=None,
    radius_km=None,
    transmission=None,
    vehicle_available=None,
    max_price=None,
    ordering="distance",
):
    data_mode = "SYNTHETIC" if settings.SYNTHETIC_MARKETPLACE_ENABLED else "REAL"
    origin = Point(float(longitude), float(latitude), srid=4326)
    queryset = published_instructor_profiles().filter(
        service_area__public_service_location__isnull=False,
    )
    if category:
        queryset = queryset.filter(categories__contains=[category])
    if radius_km is not None:
        queryset = queryset.filter(
            service_area__public_service_location__distance_lte=(origin, D(km=radius_km))
        )
    if uf:
        queryset = queryset.filter(service_area__uf=uf)
    if transmission:
        queryset = queryset.filter(transmission_options__contains=[transmission])
    if vehicle_available is not None:
        queryset = queryset.filter(vehicle_available=vehicle_available)
    offer_filter = Q(offers__is_active=True, offers__data_mode=data_mode)
    if category:
        offer_filter &= Q(offers__category=category)
    else:
        eligible_categories = Q()
        for offered_category in ("A", "B", "C", "D", "E"):
            eligible_categories |= Q(
                **{
                    "categories__contains": [offered_category],
                    "offers__category": offered_category,
                }
            )
        offer_filter &= eligible_categories
    queryset = queryset.annotate(
        minimum_price=Min(
            "offers__price_amount",
            filter=offer_filter,
        )
    ).filter(minimum_price__isnull=False)
    if max_price is not None:
        queryset = queryset.filter(minimum_price__lte=max_price)
    order = ("minimum_price", "distance", "id") if ordering == "price" else ("distance", "id")
    return (
        queryset.select_related("service_area")
        .prefetch_related("profile_photos", "documents__requirement", "offers")
        .annotate(distance=Distance("service_area__public_service_location", origin))
        .order_by(*order)[: settings.INSTRUCTOR_SEARCH_MAX_RESULTS]
    )


search_demo_instructors = search_published_instructors
