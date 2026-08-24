import os
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Permission
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import (
    DemoInstructorServiceLocation,
    InstructorProfile,
    InstructorServiceArea,
    LocationPublicationAuthorization,
    ProfessionalVerification,
)
from apps.people.models import Person, RoleAssignment

DEMO_INSTRUCTORS = [
    (
        "poa-marina",
        "Marina Alves Demo",
        "Porto Alegre",
        "RS",
        -30.0346,
        -51.2177,
        "MANUAL",
        "4.9",
        "92.00",
    ),
    (
        "poa-caio",
        "Rafael Demo",
        "Porto Alegre",
        "RS",
        -30.0188,
        -51.2050,
        "AUTOMATIC",
        "4.8",
        "98.00",
    ),
    (
        "poa-bia",
        "Beatriz Lima Demo",
        "Porto Alegre",
        "RS",
        -30.0540,
        -51.1950,
        "MANUAL",
        "4.7",
        "88.00",
    ),
    (
        "fln-luana",
        "Luana Costa Demo",
        "Florianópolis",
        "SC",
        -27.5949,
        -48.5482,
        "MANUAL",
        "4.8",
        "94.00",
    ),
    (
        "fln-davi",
        "Davi Rocha Demo",
        "Florianópolis",
        "SC",
        -27.5750,
        -48.5250,
        "AUTOMATIC",
        "4.6",
        "99.00",
    ),
    (
        "sp-nina",
        "Nina Prado Demo",
        "São Paulo",
        "SP",
        -23.5505,
        -46.6333,
        "MANUAL",
        "4.9",
        "105.00",
    ),
    (
        "sp-igor",
        "Igor Campos Demo",
        "São Paulo",
        "SP",
        -23.5650,
        -46.6500,
        "AUTOMATIC",
        "4.7",
        "110.00",
    ),
    (
        "rj-clara",
        "Clara Reis Demo",
        "Rio de Janeiro",
        "RJ",
        -22.9068,
        -43.1729,
        "MANUAL",
        "4.8",
        "103.00",
    ),
    (
        "rj-noah",
        "Noah Martins Demo",
        "Rio de Janeiro",
        "RJ",
        -22.9250,
        -43.1900,
        "AUTOMATIC",
        "4.7",
        "108.00",
    ),
    (
        "vix-lara",
        "Lara Freitas Demo",
        "Vitória",
        "ES",
        -20.3155,
        -40.3128,
        "MANUAL",
        "4.9",
        "96.00",
    ),
    (
        "vix-teo",
        "Teo Barros Demo",
        "Vitória",
        "ES",
        -20.3000,
        -40.3000,
        "AUTOMATIC",
        "4.6",
        "101.00",
    ),
]


class Command(BaseCommand):
    help = "Seed synthetic public service points for MAPA ONLINE 01"

    def handle(self, *args, **options):
        for key, name, city, uf, lat, lng, transmission, rating, price in DEMO_INSTRUCTORS:
            DemoInstructorServiceLocation.objects.update_or_create(
                fixture_key=key,
                defaults={
                    "display_name": name,
                    "city": city,
                    "uf": uf,
                    "public_service_location": Point(lng, lat, srid=4326),
                    "private_location": None,
                    "categories": ["B"],
                    "transmission": transmission,
                    "vehicle_available": True,
                    "demo_rating": Decimal(rating),
                    "demo_price": Decimal(price),
                    "availability_summary": "Horários demonstrativos nesta semana",
                    "is_demo": True,
                },
            )
        self.stdout.write(
            self.style.SUCCESS(f"{len(DEMO_INSTRUCTORS)} synthetic instructors ready")
        )
        reviewer, _ = Account.objects.get_or_create(
            username="reviewer_demo",
            defaults={"email": "reviewer.demo@example.invalid", "is_staff": True},
        )
        demo_password = os.getenv("DEMO_ADMIN_PASSWORD")
        if demo_password:
            reviewer.set_password(demo_password)
            reviewer.save(update_fields=["password"])
        reviewer.user_permissions.add(
            *Permission.objects.filter(
                content_type__app_label="discovery",
                codename__in=[
                    "manage_instructor_publication",
                    "view_instructorprofile",
                    "change_instructorprofile",
                ],
            )
        )
        now = timezone.now()
        for index, (key, name, city, uf, lat, lng, transmission, rating, price) in enumerate(
            DEMO_INSTRUCTORS
        ):
            account, _ = Account.objects.get_or_create(
                username=f"{key}_demo", defaults={"email": f"{key}@example.invalid"}
            )
            person, _ = Person.objects.get_or_create(account=account)
            RoleAssignment.objects.get_or_create(
                person=person,
                role="INSTRUCTOR",
                revoked_at__isnull=True,
                defaults={"granted_by": reviewer, "grant_reason": "SYNTHETIC_FIXTURE"},
            )
            published = index == 0
            profile, created = InstructorProfile.objects.get_or_create(
                person=person,
                defaults={
                    "display_name": name,
                    "bio": "Perfil exclusivamente sintético.",
                    "categories": ["B"],
                    "transmission_options": [transmission],
                    "vehicle_available": True,
                    "service_radius_km": 10,
                    "demo_rating": Decimal(rating),
                    "demo_price": Decimal(price),
                    "profile_status": "APPROVED" if published else "UNDER_REVIEW",
                    "verification_status": "VERIFIED",
                    "verified_until": now + timedelta(days=30),
                    "publication_status": "APPROVED" if published else "UNPUBLISHED",
                    "is_demo": True,
                },
            )
            if not created:
                profile.display_name = name
                profile.bio = "Perfil exclusivamente sintético."
                profile.categories = ["B"]
                profile.transmission_options = [transmission]
                profile.vehicle_available = True
                profile.service_radius_km = 10
                profile.demo_rating = Decimal(rating)
                profile.demo_price = Decimal(price)
                profile.save(
                    update_fields=[
                        "display_name", "bio", "categories", "transmission_options",
                        "vehicle_available", "service_radius_km", "demo_rating", "demo_price",
                    ]
                )
            area, area_created = InstructorServiceArea.objects.get_or_create(
                profile=profile,
                defaults={
                    "city": city,
                    "uf": uf,
                    "public_service_location": Point(lng, lat, srid=4326),
                    "private_location": None,
                    "radius_km": 10,
                    "location_authorized": True,
                },
            )
            if not area_created:
                area.city = city
                area.uf = uf
                area.public_service_location = Point(lng, lat, srid=4326)
                area.private_location = None
                area.radius_km = 10
                area.save(
                    update_fields=["city", "uf", "public_service_location", "private_location", "radius_km"]
                )
            if not area.authorization_history.filter(revoked_at__isnull=True).exists():
                LocationPublicationAuthorization.objects.create(
                    service_area=area,
                    purpose="SYNTHETIC_MARKETPLACE_DISCOVERY",
                    policy_version="DEMO-1",
                    authorized_at=now,
                    actor=reviewer,
                )
            if not profile.verification_history.exists():
                ProfessionalVerification.objects.create(
                    profile=profile,
                    provider="SYNTHETIC",
                    status="VERIFIED",
                    verified_at=now,
                    verified_until=now + timedelta(days=30),
                    actor=reviewer,
                    reason="SYNTHETIC_FIXTURE",
                )
            for action in [
                "profile_submitted",
                "profile_review_started",
                "verification_verified",
                "location_authorized",
            ]:
                AuditEvent.objects.get_or_create(
                    action=f"discovery.{action}",
                    target_type="discovery.InstructorProfile",
                    target_id=profile.id,
                    reason_code="SYNTHETIC_FIXTURE",
                    defaults={"actor": reviewer, "metadata": {"synthetic": True}},
                )
