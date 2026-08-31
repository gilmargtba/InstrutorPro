from datetime import date, timedelta

import pytest
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile, InstructorServiceArea
from apps.marketplace.documents import (
    DocumentPermissionDenied,
    DocumentValidationError,
    expire_documents,
    inspect_document,
    review_document,
    upload_synthetic_document,
)
from apps.marketplace.models import DataMode, DocumentRequirement, InstructorDocument
from apps.people.models import Person


def make_profile():
    account = Account.objects.create_user(
        username="fixture-owner", email="fixture-owner@example.invalid", password="safe-password"
    )
    profile = InstructorProfile.objects.create(
        person=Person.objects.create(account=account),
        display_name="Fixture Owner Demo",
        categories=["B"],
        transmission_options=["MANUAL"],
        is_demo=True,
    )
    InstructorServiceArea.objects.create(
        profile=profile,
        city="Porto Alegre",
        uf="RS",
        public_service_location=Point(-51.2177, -30.0346, srid=4326),
        radius_km=10,
        location_authorized=True,
    )
    return account, profile


def requirement(*, required=False, requires_validity=False):
    return DocumentRequirement.objects.create(
        uf="RS",
        category="B",
        rule_version="TEST-1",
        document_type=DocumentRequirement.DocumentType.INSTRUCTOR_AUTHORIZATION,
        label="Fixture de autorização",
        required=required,
        requires_validity=requires_validity,
        active_from=date.today(),
    )


def pdf(name="fixture-credential.pdf", body=b"%PDF-1.4\nsynthetic fixture only"):
    return SimpleUploadedFile(name, body, content_type="application/pdf")


@pytest.mark.django_db
@override_settings(SYNTHETIC_DOCUMENT_UPLOAD_ENABLED=True)
def test_synthetic_upload_is_private_randomized_and_audited(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    owner, profile = make_profile()
    document = upload_synthetic_document(
        actor=owner, instructor=profile, requirement=requirement(), upload=pdf()
    )
    assert document.file.name.startswith(f"quarantine/{profile.id}/")
    assert "fixture-credential" not in document.file.name
    assert document.scan_status == InstructorDocument.ScanStatus.CLEAN
    assert document.status == InstructorDocument.Status.PENDING
    assert AuditEvent.objects.filter(
        action="marketplace.instructor_document.uploaded", target_id=document.id
    ).exists()


@pytest.mark.django_db
@override_settings(SYNTHETIC_DOCUMENT_UPLOAD_ENABLED=True, INSTRUCTOR_DOCUMENT_MAX_BYTES=20)
@pytest.mark.parametrize(
    "upload",
    [
        pdf("credential.pdf"),
        pdf("fixture-malware.pdf", b"MZ executable"),
        pdf("fixture-large.pdf", b"%PDF-" + b"x" * 30),
        SimpleUploadedFile("fixture-bad.exe", b"MZ", content_type="application/octet-stream"),
    ],
)
def test_rejects_non_fixture_executable_oversize_and_extension(upload):
    with pytest.raises(DocumentValidationError):
        inspect_document(upload, data_mode=DataMode.SYNTHETIC)


@pytest.mark.django_db
@override_settings(SYNTHETIC_DOCUMENT_UPLOAD_ENABLED=True)
def test_reviewer_must_be_independent_authorized_and_cannot_approve_expired(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    owner, profile = make_profile()
    document = upload_synthetic_document(
        actor=owner, instructor=profile, requirement=requirement(), upload=pdf()
    )
    with pytest.raises(DocumentPermissionDenied):
        review_document(
            actor=owner,
            document=document,
            decision=InstructorDocument.Status.APPROVED,
            reason="SELF_REVIEW",
        )
    reviewer = Account.objects.create_user(username="reviewer-doc", password="safe-password")
    reviewer.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="marketplace", codename="review_instructor_document"
        )
    )
    reviewed = review_document(
        actor=reviewer,
        document=document,
        decision=InstructorDocument.Status.APPROVED,
        reason="SYNTHETIC_CHECKLIST_PASS",
    )
    assert reviewed.status == InstructorDocument.Status.APPROVED
    assert reviewed.reviewed_by == reviewer


@pytest.mark.django_db
@override_settings(SYNTHETIC_DOCUMENT_UPLOAD_ENABLED=True)
def test_expiration_is_audited(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    owner, profile = make_profile()
    document = upload_synthetic_document(
        actor=owner, instructor=profile, requirement=requirement(), upload=pdf()
    )
    InstructorDocument.objects.filter(pk=document.pk).update(
        status=InstructorDocument.Status.APPROVED,
        valid_until=date.today() - timedelta(days=1),
    )
    assert expire_documents() == 1
    document.refresh_from_db()
    assert document.status == InstructorDocument.Status.EXPIRED
    assert AuditEvent.objects.filter(
        action="marketplace.instructor_document.expired", target_id=document.id
    ).exists()


@pytest.mark.django_db
@override_settings(SYNTHETIC_DOCUMENT_UPLOAD_ENABLED=True)
def test_private_download_denies_other_account_and_audits_owner(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    owner, profile = make_profile()
    document = upload_synthetic_document(
        actor=owner, instructor=profile, requirement=requirement(), upload=pdf()
    )
    client = APIClient()
    outsider = Account.objects.create_user(username="outsider", password="safe-password")
    client.force_authenticate(outsider)
    url = f"/api/v1/marketplace/instructor-documents/{document.id}/download/"
    assert client.get(url).status_code == 403
    client.force_authenticate(owner)
    response = client.get(url)
    assert response.status_code == 200
    assert response["Cache-Control"] == "private, no-store"
    assert AuditEvent.objects.filter(
        action="marketplace.instructor_document.downloaded", target_id=document.id
    ).exists()
