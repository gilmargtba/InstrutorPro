from datetime import timedelta

import pytest
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import Point
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import (
    InstructorProfile,
    InstructorServiceArea,
    allow_critical_state_mutation,
)
from apps.discovery.selectors import published_instructor_profiles
from apps.marketplace.models import MarketplaceEvent, Plan, Subscription
from apps.marketplace.saas import (
    assign_free_plan,
    change_subscription_plan,
    ensure_saas_catalog,
    has_entitlement,
    instructor_analytics,
)
from apps.people.models import Person, RoleAssignment


@pytest.fixture
def instructor(db):
    account = Account.objects.create_user(
        username="saas-instructor", email="saas@example.invalid", password="safe-test-pass"
    )
    person = Person.objects.create(account=account)
    RoleAssignment.objects.create(person=person, role="INSTRUCTOR", grant_reason="TEST")
    profile = InstructorProfile.objects.create(
        person=person,
        display_name="Instrutora Teste",
        profile_status="APPROVED",
        verification_status="VERIFIED",
        verified_until=timezone.now() + timedelta(days=10),
        publication_status="APPROVED",
    )
    return account, profile


@pytest.mark.django_db
def test_catalog_has_free_and_unpriced_inactive_pro():
    free, pro = ensure_saas_catalog()
    assert free.price_amount == 0 and free.status == Plan.Status.ACTIVE
    assert pro.price_amount is None and pro.status == Plan.Status.DRAFT and not pro.is_public


@pytest.mark.django_db
def test_free_assignment_is_idempotent(instructor):
    account, _ = instructor
    first = assign_free_plan(account)
    second = assign_free_plan(account)
    assert first.pk == second.pk
    assert Subscription.objects.filter(account=account).count() == 1


@pytest.mark.django_db
def test_entitlements_are_central_and_free_does_not_gain_pro(instructor):
    account, _ = instructor
    assign_free_plan(account)
    assert has_entitlement(account, "PUBLIC_PROFILE")
    assert has_entitlement(account, "WHATSAPP_CONTACT")
    assert has_entitlement(account, "BASIC_ANALYTICS")
    assert not has_entitlement(account, "ADVANCED_ANALYTICS")


@pytest.mark.django_db
def test_cancelled_subscription_has_no_entitlement(instructor):
    account, _ = instructor
    subscription = assign_free_plan(account)
    subscription.status = Subscription.Status.CANCELLED
    subscription.cancelled_at = timezone.now()
    subscription.save()
    assert not has_entitlement(account, "PUBLIC_PROFILE")


@pytest.mark.django_db
def test_analytics_aggregation_and_conversion(instructor):
    _, profile = instructor
    now = timezone.now()
    for event_type, count in (
        (MarketplaceEvent.Type.SEARCH_RESULT_IMPRESSION, 4),
        (MarketplaceEvent.Type.INSTRUCTOR_PROFILE_VIEWED, 2),
        (MarketplaceEvent.Type.WHATSAPP_CONTACT_CLICKED, 1),
    ):
        for i in range(count):
            MarketplaceEvent.objects.create(
                event_type=event_type,
                instructor=profile,
                session_hash=f"{event_type}-{i}",
                dedupe_bucket=now + timedelta(minutes=i),
                data_mode="SYNTHETIC",
            )
    result = instructor_analytics(profile, 30)
    assert result["search_impressions"] == 4
    assert result["profile_views"] == 2
    assert result["whatsapp_contacts"] == 1
    assert result["conversion_percent"] == 50


@pytest.mark.django_db
def test_zero_analytics_conversion(instructor):
    assert instructor_analytics(instructor[1], 7)["conversion_percent"] == 0


@pytest.mark.django_db
def test_api_denies_advanced_analytics_to_free(instructor):
    account, _ = instructor
    assign_free_plan(account)
    client = APIClient()
    client.force_authenticate(account)
    assert client.get("/api/v1/marketplace/instructor/advanced-analytics/").status_code == 403


@pytest.mark.django_db
def test_subscription_does_not_change_publication(instructor):
    account, profile = instructor
    with allow_critical_state_mutation():
        profile.publication_status = "SUSPENDED"
        profile.save(update_fields=["publication_status"])
    subscription = assign_free_plan(account)
    assert subscription.status == "ACTIVE"
    profile.refresh_from_db()
    assert profile.publication_status == "SUSPENDED"


@pytest.mark.django_db
@override_settings(APP_ENV="DEV")
def test_admin_plan_change_requires_permission_and_audits(instructor):
    account, _ = instructor
    subscription = assign_free_plan(account)
    _, pro = ensure_saas_catalog()
    admin = Account.objects.create_user(username="saas-admin", email="admin@example.invalid")
    with pytest.raises(PermissionError):
        change_subscription_plan(actor=admin, subscription=subscription, plan=pro, reason="TEST")
    admin.user_permissions.add(Permission.objects.get(codename="manage_saas"))
    admin = Account.objects.get(pk=admin.pk)
    change_subscription_plan(actor=admin, subscription=subscription, plan=pro, reason="TEST")
    assert AuditEvent.objects.filter(action="marketplace.subscription.plan_changed").exists()


@pytest.mark.django_db
@override_settings(APP_ENV="PRODUCTION")
def test_production_blocks_admin_plan_change(instructor):
    account, _ = instructor
    subscription = assign_free_plan(account)
    _, pro = ensure_saas_catalog()
    account.user_permissions.add(Permission.objects.get(codename="manage_saas"))
    with pytest.raises(PermissionError):
        change_subscription_plan(actor=account, subscription=subscription, plan=pro, reason="TEST")


@pytest.mark.django_db
@override_settings(
    APP_ENV="PRODUCTION",
    SYNTHETIC_MARKETPLACE_ENABLED=False,
    REAL_INSTRUCTOR_PUBLICATION_ENABLED=True,
)
def test_production_denies_synthetic_even_if_verified_and_published(instructor):
    _, profile = instructor
    InstructorServiceArea.objects.create(
        profile=profile,
        city="Porto Alegre",
        uf="RS",
        public_service_location=Point(-51.2, -30.0, srid=4326),
        radius_km=10,
        location_authorized=True,
    )
    assert not published_instructor_profiles().filter(pk=profile.pk).exists()
