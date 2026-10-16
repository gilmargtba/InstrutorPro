from unittest.mock import patch

import pytest
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import (
    InstructorProfile,
    InstructorServiceArea,
    ProfessionalVerificationRequest,
)
from apps.discovery.verification_services import (
    record_review_and_approve,
    reject_verification_request,
    save_verification_draft,
    start_verification_review,
)
from apps.marketplace.documents import review_document
from apps.marketplace.models import (
    DataMode,
    DocumentRequirement,
    InstructorContactChannel,
    InstructorDocument,
    InstructorOffer,
)
from apps.marketplace.real_documents import DocumentUploadError, inspect_real_upload
from apps.people.models import Person, RoleAssignment

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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "uf", "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()
)
@override_settings(**{**ENABLED, "REAL_PRODUCTION_AUTHORIZATION": "NOT_GRANTED"})
def test_generic_upload_with_zero_approved_requirements_in_every_uf(tmp_path, uf):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, instructor = profile("generic-owner")
        InstructorServiceArea.objects.filter(profile=instructor).update(uf=uf)
        save_verification_draft(actor=owner, profile=instructor, cpf="52998224725")
        client = APIClient()
        client.force_authenticate(owner)
        state = client.get("/api/v1/instructor/verification/").json()
        assert state["document_upload_available"] is True
        assert state["requirements"] == []
        with patch("apps.marketplace.real_documents.scan_with_clamd", return_value="CLEAN"):
            response = client.post(
                "/api/v1/instructor/verification/documents/",
                {
                    "document_type": "PROFESSIONAL_CREDENTIAL",
                    "file": sample_file(),
                },
                format="multipart",
            )
        assert response.status_code == 201
        document = InstructorDocument.objects.get()
        assert document.requirement_id is None
        assert document.retention_status == "POLICY_PENDING"
        assert document.file.name.startswith("professional-documents/")
        assert response.json()["documents"][0]["label"] == "Credencial profissional"
        blocked = client.post("/api/v1/instructor/verification/submit/", {}, format="json")
        assert blocked.status_code == 400
        assert "CNH" in str(blocked.json())
        instructor.refresh_from_db()
        assert instructor.verification_status != "VERIFIED"
        assert instructor.publication_status == "UNPUBLISHED"


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_cnh_document_type_upload_is_private_and_requires_human_review(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, instructor = profile("cnh-owner")
        save_verification_draft(actor=owner, profile=instructor, cpf="52998224725")
        client = APIClient()
        client.force_authenticate(owner)
        with patch("apps.marketplace.real_documents.scan_with_clamd", return_value="CLEAN"):
            response = client.post(
                "/api/v1/instructor/verification/documents/",
                {"document_type": "DRIVER_LICENSE", "file": sample_file()},
                format="multipart",
            )
        assert response.status_code == 201
        document = InstructorDocument.objects.get(instructor=instructor)
        assert document.document_type == InstructorDocument.DocumentType.DRIVER_LICENSE
        assert document.scan_status == InstructorDocument.ScanStatus.CLEAN
        assert document.status == InstructorDocument.Status.PENDING
        assert "file" not in response.json()["documents"][0]


@pytest.mark.django_db
@pytest.mark.parametrize("scan_result", ["PENDING", "BLOCKED"])
@override_settings(**ENABLED)
def test_generic_nonclean_file_cannot_accompany_submission(tmp_path, scan_result):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, instructor = profile("generic-nonclean")
        save_verification_draft(actor=owner, profile=instructor, cpf="52998224725")
        client = APIClient()
        client.force_authenticate(owner)
        kwargs = (
            {"side_effect": DocumentUploadError()}
            if scan_result == "PENDING"
            else {"return_value": scan_result}
        )
        with patch("apps.marketplace.real_documents.scan_with_clamd", **kwargs):
            assert (
                client.post(
                    "/api/v1/instructor/verification/documents/",
                    {
                        "document_type": "OTHER_PROFESSIONAL",
                        "file": sample_file(),
                    },
                    format="multipart",
                ).status_code
                == 201
            )
        assert (
            client.post("/api/v1/instructor/verification/submit/", {}, format="json").status_code
            == 400
        )
        document = InstructorDocument.objects.get()
        assert document.scan_status == scan_result
        assert (
            client.get(
                f"/api/v1/marketplace/instructor-documents/{document.pk}/download/"
            ).status_code
            == 403
        )


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


def complete_submission(profile, *, excluded_document=None):
    """Supply applicant-controlled prerequisites for tests of later review steps."""
    RoleAssignment.objects.get_or_create(
        person=profile.person,
        role=RoleAssignment.Role.INSTRUCTOR,
        defaults={"granted_by": profile.person.account, "grant_reason": "TEST"},
    )
    InstructorServiceArea.objects.filter(profile=profile).update(
        public_service_location=Point(-49.37, -18.01, srid=4326),
        location_authorized=True,
    )
    InstructorOffer.objects.get_or_create(
        instructor=profile, category="B", data_mode=DataMode.REAL,
        defaults={"price_amount": "70.00", "duration_minutes": 50},
    )
    InstructorContactChannel.objects.get_or_create(
        instructor=profile,
        defaults={"whatsapp_e164": "+5562999999999", "data_mode": DataMode.REAL},
    )
    item = ProfessionalVerificationRequest.objects.get(profile=profile, status="DRAFT")
    present = set(item.documents.values_list("document_type", flat=True))
    needed = {
        InstructorDocument.DocumentType.DRIVER_LICENSE,
        InstructorDocument.DocumentType.PROFESSIONAL_CREDENTIAL,
    }
    for kind in needed - present:
        if kind == excluded_document:
            continue
        InstructorDocument.objects.create(
            instructor=profile, verification_request=item, document_type=kind,
            file=f"private/test-{kind}.pdf", original_name=f"test-{kind}.pdf",
            mime_type="application/pdf", size_bytes=128, sha256="a" * 64,
            scan_status=InstructorDocument.ScanStatus.CLEAN, data_mode=DataMode.REAL,
        )


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_submission_requires_applicant_evidence_but_not_prior_uf_approval():
    owner, instructor = profile("complete-submission-ce")
    InstructorServiceArea.objects.filter(profile=instructor).update(uf="CE", city="Fortaleza")
    save_verification_draft(actor=owner, profile=instructor, cpf="52998224725")
    client = APIClient()
    client.force_authenticate(owner)
    pending = client.get("/api/v1/instructor/verification/").json()["submission_blockers"]
    assert any("CNH" in issue for issue in pending)
    assert any("WhatsApp" in issue for issue in pending)
    blocked = client.post("/api/v1/instructor/verification/submit/", {}, format="json")
    assert blocked.status_code == 400
    assert "CNH" in str(blocked.json())
    complete_submission(instructor)
    assert client.get("/api/v1/instructor/verification/").json()["submission_blockers"] == []
    submitted = client.post("/api/v1/instructor/verification/submit/", {}, format="json")
    assert submitted.status_code == 201
    instructor.refresh_from_db()
    assert instructor.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED


@pytest.mark.django_db
@override_settings(**{**ENABLED, "CLAMD_HOST": ""})
def test_configured_document_outage_keeps_request_as_draft():
    owner, instructor = profile("submission-scanner-outage")
    save_verification_draft(actor=owner, profile=instructor, cpf="52998224725")
    client = APIClient()
    client.force_authenticate(owner)
    state = client.get("/api/v1/instructor/verification/").json()
    assert state["document_upload_available"] is False
    assert "temporariamente indisponível" in state["submission_blockers"][0]
    blocked = client.post("/api/v1/instructor/verification/submit/", {}, format="json")
    assert blocked.status_code == 400
    assert ProfessionalVerificationRequest.objects.get(profile=instructor).status == "DRAFT"


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


@pytest.mark.django_db
@override_settings(**{**ENABLED, "REAL_VISUAL_IDENTITY_REVIEW_ENABLED": False})
def test_visual_review_photo_is_disabled_until_privacy_gate(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, instructor = profile("photo-disabled-owner")
        save_verification_draft(actor=owner, profile=instructor, cpf="52998224725")
        client = APIClient()
        client.force_authenticate(owner)
        state = client.get("/api/v1/instructor/verification/").json()
        assert state["visual_review_available"] is False
        response = client.post(
            "/api/v1/instructor/verification/documents/",
            {
                "document_type": "SELFIE_WITH_CNH",
                "manual_identity_review_authorized": "true",
                "file": sample_file("visual.jpg", b"\xff\xd8\xff\xe0private-test", "image/jpeg"),
            },
            format="multipart",
        )
        assert response.status_code == 400
        assert not InstructorDocument.objects.exists()


@pytest.mark.django_db
@override_settings(**{**ENABLED, "REAL_VISUAL_IDENTITY_REVIEW_ENABLED": True})
def test_visual_review_photo_requires_owner_confirmation_and_image_and_stays_private(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, instructor = profile("photo-with-cnh-owner")
        save_verification_draft(actor=owner, profile=instructor, cpf="52998224725")
        client = APIClient()
        client.force_authenticate(owner)
        endpoint = "/api/v1/instructor/verification/documents/"

        def jpeg():
            return sample_file("visual.jpg", b"\xff\xd8\xff\xe0private-test", "image/jpeg")

        assert (
            client.post(
                endpoint,
                {"document_type": "SELFIE_WITH_CNH", "file": jpeg()},
                format="multipart",
            ).status_code
            == 400
        )
        assert (
            client.post(
                endpoint,
                {
                    "document_type": "SELFIE_WITH_CNH",
                    "manual_identity_review_authorized": "true",
                    "file": sample_file(),
                },
                format="multipart",
            ).status_code
            == 400
        )
        assert not InstructorDocument.objects.exists()

        with patch("apps.marketplace.real_documents.scan_with_clamd", return_value="CLEAN"):
            response = client.post(
                endpoint,
                {
                    "document_type": "SELFIE_WITH_CNH",
                    "manual_identity_review_authorized": "true",
                    "file": jpeg(),
                },
                format="multipart",
            )
        assert response.status_code == 201
        document = InstructorDocument.objects.get()
        assert document.manual_identity_review_authorized_at is not None
        assert document.scan_status == document.ScanStatus.CLEAN
        assert document.status == document.Status.PENDING
        assert response.json()["documents"][0]["label"] == "Foto com CNH para conferência visual"
        assert AuditEvent.objects.filter(
            action="marketplace.professional_document.uploaded",
            target_id=document.pk,
            metadata__visual_review_notice_version="INSTRUCTOR-CNH-VISUAL-REVIEW-1",
        ).exists()
        assert instructor.publication_status == instructor.PublicationStatus.UNPUBLISHED
        anonymous = APIClient()
        assert anonymous.get(
            f"/api/v1/marketplace/instructor-documents/{document.pk}/download/"
        ).status_code in {401, 403}


@pytest.mark.django_db
@override_settings(**{**ENABLED, "REAL_VISUAL_IDENTITY_REVIEW_ENABLED": True})
def test_visual_review_photo_is_listed_on_same_human_review_screen(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, instructor = profile("photo-review-owner")
        analyst = reviewer("photo-review-analyst", can_access_document=True)
        save_verification_draft(actor=owner, profile=instructor, cpf="52998224725")
        client = APIClient()
        client.force_authenticate(owner)
        with patch("apps.marketplace.real_documents.scan_with_clamd", return_value="CLEAN"):
            response = client.post(
                "/api/v1/instructor/verification/documents/",
                {
                    "document_type": "SELFIE_WITH_CNH",
                    "manual_identity_review_authorized": "true",
                    "file": sample_file(
                        "visual.png", b"\x89PNG\r\n\x1a\nprivate-test", "image/png"
                    ),
                },
                format="multipart",
            )
        assert response.status_code == 201
        complete_submission(instructor)
        submitted = client.post("/api/v1/instructor/verification/submit/", {}, format="json")
        assert submitted.status_code == 201
        item = ProfessionalVerificationRequest.objects.get(profile=instructor)
        start_verification_review(actor=analyst, verification_request=item)
        from django.test.client import Client
        from django.urls import reverse

        web = Client()
        web.force_login(analyst)
        page = web.get(
            reverse("admin:discovery_verification_request_transition", args=[item.pk, "approve"])
        )
        assert page.status_code == 200
        content = page.content.decode()
        assert "Foto com CNH para conferência visual" in content
        assert "compare visualmente rosto e documento" in content
        assert "Visualizar com autorização e auditoria" in content


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
def test_verified_owner_can_submit_private_supplement_for_human_review(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, instructor = profile("supplement-owner")
        analyst = reviewer("supplement-analyst", can_access_document=True)
        client = APIClient()
        client.force_authenticate(owner)
        assert (
            client.patch(
                "/api/v1/instructor/verification/", {"cpf": "52998224725"}, format="json"
            ).status_code
            == 200
        )
        with override_settings(REAL_DOCUMENT_UPLOADS=False):
            response = client.post("/api/v1/instructor/verification/submit/", {}, format="json")
            assert response.status_code == 201
        original = ProfessionalVerificationRequest.objects.get(profile=instructor)
        start_verification_review(actor=analyst, verification_request=original)
        record_review_and_approve(
            actor=analyst,
            verification_request=original,
            method="Consulta manual",
            source="Fonte de teste autorizada",
            notes="",
            consultation_confirmed=True,
        )
        instructor.refresh_from_db()

        state = client.get("/api/v1/instructor/verification/").json()
        assert state["can_start_supplement"] is True
        assert state["can_edit"] is False
        opened = client.post("/api/v1/instructor/verification/supplement/", {}, format="json")
        repeated = client.post("/api/v1/instructor/verification/supplement/", {}, format="json")
        assert opened.status_code == 201
        assert repeated.status_code == 200
        assert opened.json()["is_supplement"] is True
        supplement = ProfessionalVerificationRequest.objects.exclude(pk=original.pk).get(
            profile=instructor
        )
        assert supplement.previous_verified_request_id == original.id
        assert (
            client.patch(
                "/api/v1/instructor/verification/", {"cpf": "11144477735"}, format="json"
            ).status_code
            == 400
        )
        assert (
            client.post("/api/v1/instructor/verification/submit/", {}, format="json").status_code
            == 400
        )
        with patch("apps.marketplace.real_documents.scan_with_clamd", return_value="CLEAN"):
            upload = client.post(
                "/api/v1/instructor/verification/documents/",
                {"document_type": "PROFESSIONAL_CREDENTIAL", "file": sample_file()},
                format="multipart",
            )
        assert upload.status_code == 201
        document = InstructorDocument.objects.get(verification_request=supplement)
        other, _ = profile("supplement-other")
        client.force_authenticate(other)
        assert client.get("/api/v1/instructor/verification/").json()["documents"] == []
        assert (
            client.post(
                "/api/v1/instructor/verification/supplement/", {}, format="json"
            ).status_code
            == 400
        )
        client.force_authenticate(owner)
        assert (
            client.post("/api/v1/instructor/verification/submit/", {}, format="json").status_code
            == 201
        )
        instructor.refresh_from_db()
        assert instructor.verification_status == InstructorProfile.VerificationStatus.PENDING
        assert instructor.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED
        start_verification_review(actor=analyst, verification_request=supplement)
        with pytest.raises(Exception, match="documentos complementares"):
            record_review_and_approve(
                actor=analyst,
                verification_request=supplement,
                method="Consulta manual",
                source="Fonte de teste autorizada",
                notes="",
                consultation_confirmed=True,
            )
        review_document(
            actor=analyst,
            document=document,
            decision=InstructorDocument.Status.APPROVED,
            reason="TEST_REVIEW",
            source="Fonte de teste autorizada",
        )
        record_review_and_approve(
            actor=analyst,
            verification_request=supplement,
            method="Consulta manual",
            source="Fonte de teste autorizada",
            notes="",
            consultation_confirmed=True,
        )
        original.refresh_from_db()
        instructor.refresh_from_db()
        assert original.status == original.Status.VERIFIED
        assert supplement.previous_verified_request_id == original.id
        assert instructor.verification_status == InstructorProfile.VerificationStatus.VERIFIED
        assert instructor.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED

        assert (
            client.post(
                "/api/v1/instructor/verification/supplement/", {}, format="json"
            ).status_code
            == 201
        )
        retry_candidate = ProfessionalVerificationRequest.objects.filter(
            profile=instructor, status=ProfessionalVerificationRequest.Status.DRAFT
        ).get()
        assert retry_candidate.previous_verified_request_id == supplement.id
        with patch("apps.marketplace.real_documents.scan_with_clamd", return_value="CLEAN"):
            assert (
                client.post(
                    "/api/v1/instructor/verification/documents/",
                    {"document_type": "OTHER_PROFESSIONAL", "file": sample_file("cnh.pdf")},
                    format="multipart",
                ).status_code
                == 201
            )
        assert (
            client.post("/api/v1/instructor/verification/submit/", {}, format="json").status_code
            == 201
        )
        start_verification_review(actor=analyst, verification_request=retry_candidate)
        reject_verification_request(
            actor=analyst, verification_request=retry_candidate, reason_code="TEST_INSUFFICIENT"
        )
        instructor.refresh_from_db()
        assert instructor.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED
        assert client.get("/api/v1/instructor/verification/").json()["can_start_supplement"] is True
        reopened = client.post("/api/v1/instructor/verification/supplement/", {}, format="json")
        assert reopened.status_code == 201
        newest = ProfessionalVerificationRequest.objects.filter(
            profile=instructor, status=ProfessionalVerificationRequest.Status.DRAFT
        ).get()
        assert newest.previous_verified_request_id == retry_candidate.previous_verified_request_id


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
        complete_submission(instructor)
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
        complete_submission(instructor)
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
