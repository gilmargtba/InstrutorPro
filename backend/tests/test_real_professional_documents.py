from unittest.mock import patch

import pytest
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.discovery.models import (
    InstructorProfile,
    InstructorServiceArea,
    ProfessionalVerificationRequest,
)
from apps.discovery.verification_services import save_verification_draft, start_verification_review
from apps.marketplace.models import DocumentRequirement, InstructorDocument
from apps.marketplace.real_documents import DocumentUploadError, inspect_real_upload
from apps.people.models import Person

ENABLED = {
    "REAL_PRODUCTION_AUTHORIZATION": "FULL_PRODUCTION",
    "PROFESSIONAL_VERIFICATION_MODE": "PRODUCTION",
    "REAL_PROFESSIONAL_VERIFICATION": True,
    "REAL_DOCUMENT_UPLOADS": True,
    "PROFESSIONAL_DOCUMENT_UPLOAD_MODE": "PRODUCTION",
    "REAL_DOCUMENT_UPLOAD_ENABLED": True,
    "CLAMD_HOST": "clamav",
    "PII_FIELD_ENCRYPTION_KEY": "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
    "PII_FINGERPRINT_KEY": "test-only-fingerprint-key-with-32-bytes-minimum",
}


def profile(username):
    account = Account.objects.create_user(
        username=username, email=f"{username}@example.invalid", password="test-password-123"
    )
    person = Person.objects.create(account=account)
    instructor = InstructorProfile.objects.create(
        person=person, display_name=username, categories=["B"], is_demo=False
    )
    InstructorServiceArea.objects.create(profile=instructor, city="Goiânia", uf="GO")
    return account, instructor


def approved_requirement():
    return DocumentRequirement.objects.create(
        uf="GO",
        category="B",
        rule_version="test-approved-v1",
        document_type=DocumentRequirement.DocumentType.INSTRUCTOR_AUTHORIZATION,
        label="Evidência profissional de teste",
        active_from=timezone.localdate(),
        source_reference="TEST_ONLY",
        approval_recorded_at=timezone.now(),
    )


def sample_file(
    name="evidence.pdf", content=b"%PDF-1.4\nsynthetic test data", mime="application/pdf"
):
    return SimpleUploadedFile(name, content, content_type=mime)


@pytest.mark.parametrize(
    ("name", "content", "mime"),
    [
        ("documento.pdf", b"%PDF-1.4\nconteudo de teste", "application/pdf"),
        ("documento.jpg", b"\xff\xd8\xff\xe0conteudo de teste", "image/jpeg"),
        ("documento.png", b"\x89PNG\r\n\x1a\nconteudo de teste", "image/png"),
    ],
)
def test_allowed_file_signatures(name, content, mime):
    assert inspect_real_upload(sample_file(name, content, mime))["mime_type"] == mime


@pytest.mark.parametrize("name", ["../documento.pdf", "documento..pdf", "a\nb.pdf"])
def test_unsafe_file_names_are_rejected(name):
    upload = sample_file()
    upload._name = name  # Bypass Django's filename normalization to exercise the service guard.
    with pytest.raises(DocumentUploadError):
        inspect_real_upload(upload)


def test_oversized_file_is_rejected():
    with override_settings(INSTRUCTOR_DOCUMENT_MAX_BYTES=10):
        with pytest.raises(DocumentUploadError, match="tamanho permitido"):
            inspect_real_upload(sample_file())


def reviewer(username, *, can_access_document):
    account = Account.objects.create_user(
        username=username,
        email=f"{username}@example.invalid",
        password="test-password-123",
        is_staff=True,
    )
    account.user_permissions.add(
        Permission.objects.get(codename="review_professional_verification")
    )
    if can_access_document:
        account.user_permissions.add(Permission.objects.get(codename="review_instructor_document"))
    return account


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_only_configured_requirement_is_exposed_and_missing_document_blocks_submit(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        account, instructor = profile("owner-req")
        rule = approved_requirement()
        client = APIClient()
        client.force_authenticate(account)
        save_verification_draft(actor=account, profile=instructor, cpf="52998224725")
        state = client.get("/api/v1/instructor/verification/")
        assert state.status_code == 200
        assert state.json()["requirements"] == [
            {"id": str(rule.id), "label": rule.label, "required": True}
        ]
        submit = client.post("/api/v1/instructor/verification/submit/", {}, format="json")
        assert submit.status_code == 400
        assert "Documento obrigatório pendente" in str(submit.json())


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_clean_private_upload_can_submit_with_frozen_rule_snapshot(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        account, instructor = profile("owner-clean")
        rule = approved_requirement()
        client = APIClient()
        client.force_authenticate(account)
        save_verification_draft(actor=account, profile=instructor, cpf="52998224725")
        with patch(
            "apps.marketplace.real_documents.scan_with_clamd",
            return_value=InstructorDocument.ScanStatus.CLEAN,
        ):
            response = client.post(
                "/api/v1/instructor/verification/documents/",
                {"requirement_id": str(rule.id), "file": sample_file()},
                format="multipart",
            )
        assert response.status_code == 201
        document = InstructorDocument.objects.get(instructor=instructor)
        assert document.scan_status == document.ScanStatus.CLEAN
        assert document.file.name.startswith("professional-documents/")
        assert not document.file.url.startswith("/media/")
        submitted = client.post("/api/v1/instructor/verification/submit/", {}, format="json")
        assert submitted.status_code == 201
        item = ProfessionalVerificationRequest.objects.get(profile=instructor)
        assert item.requirements_snapshot[0]["id"] == str(rule.id)
        assert (
            client.delete(f"/api/v1/instructor/verification/documents/{document.pk}/").status_code
            == 400
        )


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_scanner_outage_quarantines_and_blocks_submit(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        account, instructor = profile("owner-outage")
        rule = approved_requirement()
        client = APIClient()
        client.force_authenticate(account)
        save_verification_draft(actor=account, profile=instructor, cpf="52998224725")
        with patch("apps.marketplace.real_documents.scan_with_clamd", side_effect=OSError):
            response = client.post(
                "/api/v1/instructor/verification/documents/",
                {"requirement_id": str(rule.id), "file": sample_file()},
                format="multipart",
            )
        assert response.status_code == 201
        document = InstructorDocument.objects.get(instructor=instructor)
        assert document.scan_status == document.ScanStatus.PENDING
        assert document.file.name.startswith("quarantine/")
        assert (
            client.post("/api/v1/instructor/verification/submit/", {}, format="json").status_code
            == 400
        )


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_other_instructor_cannot_remove_document_and_bad_files_are_rejected(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        account, instructor = profile("owner-idor")
        other, _ = profile("other-idor")
        rule = approved_requirement()
        client = APIClient()
        client.force_authenticate(account)
        save_verification_draft(actor=account, profile=instructor, cpf="52998224725")
        for upload in [
            sample_file(name="bad.pdf.exe"),
            sample_file(name="double.name.pdf"),
            sample_file(content=b"MZ binary"),
            sample_file(mime="text/plain"),
        ]:
            response = client.post(
                "/api/v1/instructor/verification/documents/",
                {"requirement_id": str(rule.id), "file": upload},
                format="multipart",
            )
            assert response.status_code == 400
        with patch(
            "apps.marketplace.real_documents.scan_with_clamd",
            return_value=InstructorDocument.ScanStatus.CLEAN,
        ):
            client.post(
                "/api/v1/instructor/verification/documents/",
                {"requirement_id": str(rule.id), "file": sample_file()},
                format="multipart",
            )
        document = InstructorDocument.objects.get(instructor=instructor)
        client.force_authenticate(other)
        assert (
            client.delete(f"/api/v1/instructor/verification/documents/{document.pk}/").status_code
            == 404
        )
        download_url = f"/api/v1/marketplace/instructor-documents/{document.pk}/download/"
        assert client.get(download_url).status_code == 403
        client.force_authenticate(account)
        assert client.get(download_url).status_code == 403


@pytest.mark.django_db
@override_settings(**{**ENABLED, "REAL_DOCUMENT_UPLOADS": False})
def test_capability_off_rejects_upload_without_creating_document(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        account, instructor = profile("owner-off")
        rule = approved_requirement()
        client = APIClient()
        client.force_authenticate(account)
        save_verification_draft(actor=account, profile=instructor, cpf="52998224725")
        response = client.post(
            "/api/v1/instructor/verification/documents/",
            {"requirement_id": str(rule.id), "file": sample_file()},
            format="multipart",
        )
        assert response.status_code == 403
        assert not InstructorDocument.objects.exists()


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_only_assigned_authorized_reviewer_can_download_clean_file(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, instructor = profile("owner-review")
        rule = approved_requirement()
        client = APIClient()
        client.force_authenticate(owner)
        save_verification_draft(actor=owner, profile=instructor, cpf="52998224725")
        with patch(
            "apps.marketplace.real_documents.scan_with_clamd",
            return_value=InstructorDocument.ScanStatus.CLEAN,
        ):
            assert (
                client.post(
                    "/api/v1/instructor/verification/documents/",
                    {"requirement_id": str(rule.id), "file": sample_file()},
                    format="multipart",
                ).status_code
                == 201
            )
        document = InstructorDocument.objects.get(instructor=instructor)
        url = f"/api/v1/marketplace/instructor-documents/{document.pk}/download/"
        client.force_authenticate(user=None)
        assert client.get(url).status_code in {401, 403}
        client.force_authenticate(owner)
        item = ProfessionalVerificationRequest.objects.get(profile=instructor)
        assert (
            client.post("/api/v1/instructor/verification/submit/", {}, format="json").status_code
            == 201
        )
        assigned = reviewer("assigned-reviewer", can_access_document=True)
        other = reviewer("other-reviewer", can_access_document=True)
        insufficient = reviewer("insufficient-reviewer", can_access_document=False)
        start_verification_review(actor=assigned, verification_request=item)
        client.force_authenticate(other)
        assert client.get(url).status_code == 403
        client.force_authenticate(insufficient)
        assert client.get(url).status_code == 403
        client.force_authenticate(assigned)
        download = client.get(url)
        assert download.status_code == 200
        assert download["Cache-Control"] == "private, no-store"
        assert download["X-Content-Type-Options"] == "nosniff"
        download.close()
