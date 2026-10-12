from unittest.mock import patch

import pytest
from django.contrib.gis.geos import Point
from django.test import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.instructor_precheck import InstructorValidationService
from apps.discovery.models import InstructorProfile, InstructorServiceArea
from apps.discovery.verification_services import (
    save_verification_draft,
    submit_verification_request,
)
from apps.marketplace.models import (
    DataMode,
    InstructorContactChannel,
    InstructorDocument,
    InstructorOffer,
)
from apps.people.models import Person, RoleAssignment

ENABLED = {
    "SYNTHETIC_MARKETPLACE_ENABLED": False,
    "REAL_PRODUCTION_AUTHORIZATION": "NOT_GRANTED",
    "PROFESSIONAL_VERIFICATION_MODE": "PRODUCTION",
    "REAL_PROFESSIONAL_VERIFICATION": True,
    "PII_FIELD_ENCRYPTION_KEY": "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
    "PII_FINGERPRINT_KEY": "test-only-fingerprint-key-with-32-bytes-minimum",
}


def submitted_profile(*, complete=True):
    owner = Account.objects.create_user(
        username="precheck-owner", email="precheck@example.invalid", password="test-password-123"
    )
    person = Person.objects.create(account=owner)
    RoleAssignment.objects.create(
        person=person, role=RoleAssignment.Role.INSTRUCTOR, granted_by=owner, grant_reason="TEST"
    )
    profile = InstructorProfile.objects.create(
        person=person, display_name="Instrutor Teste", categories=["A"], is_demo=False
    )
    InstructorServiceArea.objects.create(
        profile=profile,
        city="Goiatuba",
        uf="GO",
        public_service_location=Point(-49.37, -18.01, srid=4326),
        location_authorized=complete,
    )
    save_verification_draft(actor=owner, profile=profile, cpf="52998224725")
    item, created = submit_verification_request(actor=owner, profile=profile)
    assert created
    if complete:
        InstructorOffer.objects.create(
            instructor=profile,
            category="A",
            price_amount="70.00",
            duration_minutes=50,
            data_mode=DataMode.REAL,
        )
        InstructorContactChannel.objects.create(
            instructor=profile, whatsapp_e164="+5564999999999", data_mode=DataMode.REAL
        )
    return owner, profile, item


def evidence(item, document_type=InstructorDocument.DocumentType.DRIVER_LICENSE, scan="CLEAN"):
    return InstructorDocument.objects.create(
        instructor=item.profile,
        verification_request=item,
        document_type=document_type,
        file="private/test-only.pdf",
        original_name="test-only.pdf",
        mime_type="application/pdf",
        size_bytes=128,
        sha256="a" * 64,
        scan_status=scan,
        data_mode=DataMode.REAL,
    )


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_precheck_ready_is_idempotent_and_does_not_verify_or_publish():
    _, profile, item = submitted_profile()
    evidence(item)
    evidence(item, InstructorDocument.DocumentType.PROFESSIONAL_CREDENTIAL)
    assert InstructorValidationService.run(item.pk) == item.PrecheckStatus.READY_FOR_HUMAN_REVIEW
    assert InstructorValidationService.run(item.pk) == item.PrecheckStatus.READY_FOR_HUMAN_REVIEW
    item.refresh_from_db()
    profile.refresh_from_db()
    assert item.precheck_issues == []
    assert item.precheck_checked_at is not None
    assert profile.verification_status != profile.VerificationStatus.VERIFIED
    assert profile.publication_status == profile.PublicationStatus.UNPUBLISHED
    assert AuditEvent.objects.filter(action="discovery.instructor_precheck.completed").count() == 1


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_precheck_explains_missing_cnh_offer_area_and_whatsapp_without_exposing_cpf():
    owner, _, item = submitted_profile(complete=False)
    evidence(item, InstructorDocument.DocumentType.OTHER_PROFESSIONAL)
    assert InstructorValidationService.run(item.pk) == item.PrecheckStatus.NEEDS_CORRECTION
    item.refresh_from_db()
    assert set(item.precheck_issues) == {
        "CNH_MISSING",
        "PROFESSIONAL_CREDENTIAL_MISSING",
        "OFFER_MISSING",
        "SERVICE_AREA_MISSING",
        "WHATSAPP_MISSING",
    }
    client = APIClient()
    client.force_authenticate(owner)
    response = client.get("/api/v1/instructor/verification/")
    assert response.status_code == 200
    assert response.json()["precheck_status"] == "NEEDS_CORRECTION"
    assert len(response.json()["precheck_issues"]) == 5
    assert "52998224725" not in str(response.json())


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_precheck_flags_contaminated_document_even_if_cnh_exists():
    _, _, item = submitted_profile()
    evidence(item, scan="BLOCKED")
    assert InstructorValidationService.run(item.pk) == item.PrecheckStatus.NEEDS_CORRECTION
    item.refresh_from_db()
    assert "FILE_BLOCKED" in item.precheck_issues
    assert "CNH_MISSING" in item.precheck_issues


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_precheck_recovers_after_missing_evidence_is_added():
    _, profile, item = submitted_profile(complete=False)
    assert InstructorValidationService.run(item.pk) == item.PrecheckStatus.NEEDS_CORRECTION
    evidence(item)
    evidence(item, InstructorDocument.DocumentType.PROFESSIONAL_CREDENTIAL)
    InstructorServiceArea.objects.filter(profile=profile).update(location_authorized=True)
    InstructorOffer.objects.create(
        instructor=profile,
        category="A",
        price_amount="70.00",
        duration_minutes=50,
        data_mode=DataMode.REAL,
    )
    InstructorContactChannel.objects.create(
        instructor=profile, whatsapp_e164="+5564999999999", data_mode=DataMode.REAL
    )
    assert InstructorValidationService.run(item.pk) == item.PrecheckStatus.READY_FOR_HUMAN_REVIEW


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_submission_schedules_precheck_only_after_commit():
    owner = Account.objects.create_user(
        username="queued-precheck", email="queued@example.invalid", password="test-password-123"
    )
    person = Person.objects.create(account=owner)
    profile = InstructorProfile.objects.create(person=person, display_name="Teste", is_demo=False)
    save_verification_draft(actor=owner, profile=profile, cpf="52998224725")
    with patch("apps.discovery.instructor_precheck.queue_instructor_precheck") as queue:
        from django.test import TestCase

        with TestCase.captureOnCommitCallbacks(execute=True):
            item, _ = submit_verification_request(actor=owner, profile=profile)
        queue.assert_called_once_with(item.pk)
