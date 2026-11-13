import uuid
from datetime import timedelta

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.test import RequestFactory, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.marketplace.availability_interest import purge_expired_availability_interests
from apps.marketplace.models import AvailabilityInterest, AvailabilityInterestPolicy
from apps.people.identifiers import _fernet
from apps.privacy.models import PrivacyNotice
from apps.territories.models import Country, FederativeUnit

URL = "/api/v1/marketplace/availability-interest/"


@pytest.fixture
def setup_policy(db):
    country, _ = Country.objects.get_or_create(code="BR", defaults={"name": "Brasil"})
    FederativeUnit.objects.get_or_create(
        country=country, code="GO", defaults={"name": "Goiás", "ibge_code": "52"}
    )
    notice = PrivacyNotice.objects.filter(is_current=True).first()
    if not notice:
        notice = PrivacyNotice.objects.create(
            version="interest-test-1",
            title="Aviso teste",
            is_current=True,
            published_at=timezone.now(),
        )
    return AvailabilityInterestPolicy.objects.create(
        privacy_notice=notice,
        consent_version="interest-1",
        consent_text="Autorizo contato manual pelo WhatsApp sobre disponibilidade de instrutores.",
    )


def payload(policy):
    return {
        "city": "Goiatuba",
        "uf": "GO",
        "name": "Aluno Teste",
        "phone": "64999990000",
        "birth_date": "1990-01-01",
        "privacy_notice_version": policy.privacy_notice.version,
        "consent_version": policy.consent_version,
        "consent_granted": True,
        "idempotency_key": str(uuid.uuid4()),
    }


@pytest.mark.django_db
def test_interest_is_closed_until_admin_activates_policy(setup_policy):
    client = APIClient()
    assert client.get(URL).json() == {"enabled": False}
    assert client.post(URL, payload(setup_policy), format="json").status_code == 503
    assert not AvailabilityInterest.objects.exists()


@pytest.mark.django_db
def test_policy_rejects_activation_without_valid_notice(db):
    policy = AvailabilityInterestPolicy(enabled=True, retention_days=90)
    with pytest.raises(ValidationError):
        policy.full_clean()


@pytest.mark.django_db
def test_regular_account_cannot_view_private_interest_or_configure_collection():
    actor = Account.objects.create_user(
        username="interest-reader", email="reader@example.invalid", password="test-password-123"
    )
    request = RequestFactory().get("/admin/")
    request.user = actor
    assert not admin.site._registry[AvailabilityInterest].has_view_permission(request)
    assert not admin.site._registry[AvailabilityInterestPolicy].has_change_permission(request)


@pytest.mark.django_db
@override_settings(
    PII_FIELD_ENCRYPTION_KEY="MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
    PII_FINGERPRINT_KEY="test-only-fingerprint-key-with-32-bytes-minimum",
)
def test_interest_requires_adult_and_separate_consent_and_is_idempotent(setup_policy):
    policy = setup_policy
    policy.enabled = True
    policy.full_clean()
    policy.save()
    client = APIClient()
    data = payload(policy)
    assert client.get(URL).json()["retention_days"] == 90
    assert client.post(URL, {**data, "consent_granted": False}, format="json").status_code == 400
    assert client.post(URL, {**data, "birth_date": "2015-01-01"}, format="json").status_code == 400
    assert client.post(URL, {**data, "uf": "XX"}, format="json").status_code == 400
    first = client.post(URL, data, format="json")
    assert first.status_code == 201
    assert client.post(URL, data, format="json").status_code == 200
    assert AvailabilityInterest.objects.count() == 1
    item = AvailabilityInterest.objects.get()
    assert "Aluno Teste" not in item.name_encrypted
    assert _fernet().decrypt(item.name_encrypted.encode()).decode() == "Aluno Teste"
    assert item.expires_at - item.consented_at == timedelta(days=90)
    assert (
        AuditEvent.objects.filter(
            action="marketplace.availability_interest.created", target_id=item.pk
        ).count()
        == 1
    )
    withdrawal_url = URL + "withdraw/"
    assert (
        client.post(
            withdrawal_url, {"reference": str(item.pk), "phone": "64999990001"}, format="json"
        ).status_code
        == 200
    )
    assert AvailabilityInterest.objects.exists()
    assert (
        client.post(
            withdrawal_url, {"reference": str(item.pk), "phone": data["phone"]}, format="json"
        ).status_code
        == 200
    )
    assert not AvailabilityInterest.objects.exists()
    assert AuditEvent.objects.filter(
        action="marketplace.availability_interest.withdrawn", target_id=item.pk
    ).exists()
    assert (
        client.post(URL, {**data, "idempotency_key": str(uuid.uuid4())}, format="json").status_code
        == 201
    )
    item = AvailabilityInterest.objects.get()
    item.expires_at = timezone.now() - timedelta(seconds=1)
    item.save(update_fields=["expires_at"])
    assert purge_expired_availability_interests() == 1
    assert not AvailabilityInterest.objects.exists()


@pytest.mark.django_db
@override_settings(
    PII_FIELD_ENCRYPTION_KEY="MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
    PII_FINGERPRINT_KEY="test-only-fingerprint-key-with-32-bytes-minimum",
)
def test_interest_accepts_uf_city_and_region_without_precise_coordinates(setup_policy):
    policy = setup_policy
    policy.enabled = True
    policy.full_clean()
    policy.save()
    client = APIClient()
    base = payload(policy)
    assert (
        client.post(URL, {**base, "scope": "REGION", "region": ""}, format="json").status_code
        == 400
    )
    assert client.post(URL, {**base, "scope": "CITY", "city": ""}, format="json").status_code == 400
    assert client.post(URL, {**base, "scope": "INVALID"}, format="json").status_code == 400

    for scope, city, region in (
        ("UF", "", ""),
        ("CITY", "Goiatuba", ""),
        ("REGION", "Goiatuba", "Centro"),
    ):
        response = client.post(
            URL,
            {
                **base,
                "scope": scope,
                "city": city,
                "region": region,
                "idempotency_key": str(uuid.uuid4()),
            },
            format="json",
        )
        assert response.status_code == 201
        item = AvailabilityInterest.objects.get(pk=response.json()["id"])
        assert (item.scope, item.city, item.region, item.uf) == (scope, city, region, "GO")
