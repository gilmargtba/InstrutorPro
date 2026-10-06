from uuid import uuid4

import pytest
from django.contrib.auth.models import Permission
from django.test import Client, override_settings
from django.urls import reverse

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import (
    InstructorProfile,
    ProfessionalVerificationRequest,
)
from apps.discovery.verification_services import start_verification_review
from apps.marketplace.models import DataMode, InstructorDocument
from apps.people.models import Person

SETTINGS = {
    "REAL_PRODUCTION_AUTHORIZATION": "NOT_GRANTED",
    "PROFESSIONAL_VERIFICATION_MODE": "PRODUCTION",
    "REAL_PROFESSIONAL_VERIFICATION": True,
}


def case():
    owner = Account.objects.create_user(
        username="one-page-owner", email="owner@example.invalid", password="test-password-123"
    )
    profile = InstructorProfile.objects.create(
        person=Person.objects.create(account=owner), display_name="Instrutor", is_demo=False
    )
    reviewer = Account.objects.create_user(
        username="one-page-reviewer",
        email="reviewer@example.invalid",
        password="test-password-123",
        is_staff=True,
    )
    reviewer.user_permissions.add(
        Permission.objects.get(codename="review_professional_verification"),
        Permission.objects.get(codename="review_instructor_document"),
    )
    item = ProfessionalVerificationRequest.objects.create(
        profile=profile, status=ProfessionalVerificationRequest.Status.SUBMITTED
    )
    start_verification_review(actor=reviewer, verification_request=item)
    document = InstructorDocument.objects.create(
        instructor=profile,
        verification_request=item,
        document_type=InstructorDocument.DocumentType.PROFESSIONAL_CREDENTIAL,
        file=f"private-test/{uuid4()}.pdf",
        original_name="credential.pdf",
        mime_type="application/pdf",
        size_bytes=8,
        sha256="0" * 64,
        scan_status=InstructorDocument.ScanStatus.CLEAN,
        data_mode=DataMode.REAL,
    )
    web = Client()
    web.force_login(reviewer)
    url = reverse("admin:discovery_verification_request_transition", args=[item.pk, "approve"])
    return web, url, item, document


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_reviewer_can_approve_checked_clean_document_and_verification_in_one_page():
    web, url, item, document = case()
    page = web.get(url)
    assert page.status_code == 200
    assert str(document.pk) in page.content.decode()
    assert "Documentos conferidos e aprovados nesta decisão" in page.content.decode()

    response = web.post(
        url,
        {
            "reviewed_document_ids": [str(document.pk)],
            "verification_method": "Conferência visual e consulta",
            "verification_source": "Fonte conferida pelo revisor",
            "consultation_confirmed": "on",
        },
    )
    assert response.status_code == 302
    item.refresh_from_db()
    document.refresh_from_db()
    assert item.status == item.Status.VERIFIED
    assert document.status == document.Status.APPROVED
    assert document.reviewed_by == item.reviewer
    assert (
        AuditEvent.objects.filter(
            action="marketplace.instructor_document.reviewed", target_id=document.pk
        ).count()
        == 1
    )


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_one_page_rejects_foreign_document_and_rolls_back():
    web, url, item, document = case()
    response = web.post(
        url,
        {
            "reviewed_document_ids": [str(uuid4())],
            "verification_method": "Conferência visual",
            "verification_source": "Fonte conferida pelo revisor",
            "consultation_confirmed": "on",
        },
    )
    assert response.status_code == 200
    item.refresh_from_db()
    document.refresh_from_db()
    assert item.status == item.Status.UNDER_REVIEW
    assert document.status == document.Status.PENDING
    assert item.checked_at is None


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_one_page_does_not_review_unchecked_document():
    web, url, item, document = case()
    response = web.post(
        url,
        {
            "verification_method": "Conferência visual",
            "verification_source": "Fonte conferida pelo revisor",
            "consultation_confirmed": "on",
        },
    )
    assert response.status_code == 200
    item.refresh_from_db()
    document.refresh_from_db()
    assert item.status == item.Status.UNDER_REVIEW
    assert item.checked_at is None
    assert document.status == document.Status.PENDING


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_partial_one_page_selection_rolls_back_document_decision():
    web, url, item, first = case()
    second = InstructorDocument.objects.create(
        instructor=item.profile,
        verification_request=item,
        document_type=InstructorDocument.DocumentType.PROFESSIONAL_CERTIFICATE,
        file=f"private-test/{uuid4()}.pdf",
        original_name="certificate.pdf",
        mime_type="application/pdf",
        size_bytes=8,
        sha256="1" * 64,
        scan_status=InstructorDocument.ScanStatus.CLEAN,
        data_mode=DataMode.REAL,
    )
    response = web.post(
        url,
        {
            "reviewed_document_ids": [str(first.pk)],
            "verification_method": "Conferência visual",
            "verification_source": "Fonte conferida pelo revisor",
            "consultation_confirmed": "on",
        },
    )
    assert response.status_code == 200
    item.refresh_from_db()
    first.refresh_from_db()
    second.refresh_from_db()
    assert item.status == item.Status.UNDER_REVIEW
    assert first.status == second.status == InstructorDocument.Status.PENDING
    assert not AuditEvent.objects.filter(
        action="marketplace.instructor_document.reviewed", target_id=first.pk
    ).exists()
