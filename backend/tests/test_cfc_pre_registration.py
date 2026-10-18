import re

import pytest
from django.core import mail
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile
from apps.organizations.models import CFC, CFCInstructorLink, CFCMembership
from apps.people.models import Person, RoleAssignment
from apps.privacy.models import LegalAcceptanceRecord, LegalDocument, PrivacyNotice

CAPABILITIES = {
    "INSTRUCTOR_REGISTRATION_MODE": "PRODUCTION",
    "REAL_ACCOUNT_REGISTRATION": True,
    "REAL_PERSONAL_DATA": True,
    "REAL_INSTRUCTOR_REGISTRATION": True,
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "DEFAULT_FROM_EMAIL": "no-reply@example.invalid",
    "FRONTEND_PUBLIC_URL": "https://example.invalid",
}


@pytest.fixture
def cfc_manager(db):
    actor = Account.objects.create_user(
        username="manager-cfc", email="manager@example.invalid", password="secure-manager-password"
    )
    person = Person.objects.create(account=actor)
    cfc = CFC.objects.create(display_name="CFC Central", cnpj="10280826000105", is_active=True)
    CFCMembership.objects.create(cfc=cfc, person=person)
    client = APIClient()
    client.force_authenticate(actor)
    return actor, cfc, client


def legal_documents():
    terms = LegalDocument.objects.filter(
        document_type=LegalDocument.Type.TERMS,
        audience=LegalDocument.Audience.INSTRUCTOR,
        is_active=True,
    ).first()
    if not terms:
        terms = LegalDocument.objects.create(
            document_type=LegalDocument.Type.TERMS,
            audience=LegalDocument.Audience.INSTRUCTOR,
            version="cfc-test-1",
            title="Termos do instrutor",
            content="Termos de teste.",
            effective_at=timezone.now(),
            is_active=True,
        )
    privacy = PrivacyNotice.objects.filter(is_current=True).first()
    if not privacy:
        privacy = PrivacyNotice.objects.create(
            version="cfc-test-privacy",
            title="Privacidade de teste",
            published_at=timezone.now(),
            is_current=True,
        )
    return terms, privacy


@pytest.mark.django_db
@override_settings(**CAPABILITIES)
def test_cfc_manager_pre_registers_and_instructor_accepts_without_publication(cfc_manager):
    actor, cfc, client = cfc_manager
    base = f"/api/v1/cfc/{cfc.pk}/"
    assert client.patch(base, {"declared_instructor_count": 2}, format="json").status_code == 200
    response = client.post(
        base + "instructors/",
        {"display_name": "Instrutora Convidada", "email": "new@example.invalid"},
        format="json",
    )
    assert response.status_code == 201
    account = Account.objects.get(email="new@example.invalid")
    assert not account.is_active and not account.has_usable_password()
    assert not Person.objects.filter(account=account).exists()
    assert not InstructorProfile.objects.filter(person__account=account).exists()
    assert len(mail.outbox) == 1
    match = re.search(r"uid=([^&\s]+)&token=([^\s]+)", mail.outbox[0].body)
    assert match
    assert client.get(base).json()["pre_registered_count"] == 1
    assert client.get(base).json()["accepted_count"] == 0
    terms, privacy = legal_documents()
    activation = {
        "uid": match.group(1),
        "token": match.group(2),
        "birth_date": "1990-01-01",
        "password": "safe-instructor-password-123",
        "password_confirmation": "safe-instructor-password-123",
        "terms_version": terms.version,
        "privacy_version": privacy.version,
        "terms_accepted": True,
        "privacy_acknowledged": True,
        "cfc_link_accepted": True,
    }
    public = APIClient()
    assert (
        public.post("/api/v1/cfc/activate-instructor/", activation, format="json").status_code
        == 200
    )
    account.refresh_from_db()
    assert account.can_operate
    profile = InstructorProfile.objects.get(person__account=account)
    assert profile.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED
    assert profile.verification_status == InstructorProfile.VerificationStatus.NOT_STARTED
    assert RoleAssignment.objects.filter(person=account.person, role="INSTRUCTOR").exists()
    assert LegalAcceptanceRecord.objects.filter(account=account, terms_document=terms).exists()
    assert (
        CFCInstructorLink.objects.get(account=account).status == CFCInstructorLink.Status.ACCEPTED
    )
    assert (
        public.post("/api/v1/cfc/activate-instructor/", activation, format="json").status_code
        == 400
    )
    assert AuditEvent.objects.filter(actor=actor, action="cfc.instructor.pre_registered").exists()


@pytest.mark.django_db
@override_settings(**CAPABILITIES)
def test_cfc_access_denied_to_other_accounts_and_inactive_cfc(cfc_manager):
    _, cfc, client = cfc_manager
    outsider = Account.objects.create_user(
        username="outsider-cfc", email="outsider@example.invalid", password="safe-password"
    )
    other_client = APIClient()
    other_client.force_authenticate(outsider)
    base = f"/api/v1/cfc/{cfc.pk}/"
    assert other_client.get(base).status_code == 403
    assert (
        other_client.post(
            base + "instructors/",
            {"display_name": "Não autorizado", "email": "attempt@example.invalid"},
            format="json",
        ).status_code
        == 403
    )
    assert not Account.objects.filter(email="attempt@example.invalid").exists()
    cfc.is_active = False
    cfc.save(update_fields=["is_active"])
    assert client.get(base).status_code == 403


@pytest.mark.django_db
@override_settings(**CAPABILITIES)
def test_existing_email_is_not_attached_or_reset_by_cfc(cfc_manager):
    _, cfc, client = cfc_manager
    existing = Account.objects.create_user(
        username="existing-cfc", email="existing@example.invalid", password="original-password"
    )
    result = client.post(
        f"/api/v1/cfc/{cfc.pk}/instructors/",
        {
            "display_name": "Pessoa Existente",
            "email": existing.email,
        },
        format="json",
    )
    assert result.status_code == 409
    assert not CFCInstructorLink.objects.filter(account=existing).exists()
    assert existing.check_password("original-password")


@pytest.mark.django_db
@override_settings(**CAPABILITIES)
def test_pending_invitation_can_be_resent_but_other_cfc_cannot_access_it(cfc_manager):
    actor, cfc, client = cfc_manager
    response = client.post(
        f"/api/v1/cfc/{cfc.pk}/instructors/",
        {"display_name": "Instrutor Convidado", "email": "resend@example.invalid"},
        format="json",
    )
    assert response.status_code == 201
    link_id = response.json()["id"]
    other = CFC.objects.create(display_name="Outro CFC", cnpj="11444777000161", is_active=True)
    CFCMembership.objects.create(cfc=other, person=actor.person)
    wrong = client.post(f"/api/v1/cfc/{other.pk}/instructors/{link_id}/resend/")
    assert wrong.status_code == 404
    assert len(mail.outbox) == 1
    resent = client.post(f"/api/v1/cfc/{cfc.pk}/instructors/{link_id}/resend/")
    assert resent.status_code == 200
    assert len(mail.outbox) == 2
    assert AuditEvent.objects.filter(action="cfc.instructor.invitation_resent").count() == 1


@pytest.mark.django_db
@override_settings(**CAPABILITIES)
def test_activation_rejects_wrong_token_and_missing_link_acceptance(cfc_manager):
    _, cfc, client = cfc_manager
    client.post(
        f"/api/v1/cfc/{cfc.pk}/instructors/",
        {"display_name": "Instrutora Convidada", "email": "not-accepted@example.invalid"},
        format="json",
    )
    match = re.search(r"uid=([^&\s]+)&token=([^\s]+)", mail.outbox[0].body)
    terms, privacy = legal_documents()
    payload = {
        "uid": match.group(1),
        "token": "invalid-token",
        "birth_date": "1990-01-01",
        "password": "safe-instructor-password-123",
        "password_confirmation": "safe-instructor-password-123",
        "terms_version": terms.version,
        "privacy_version": privacy.version,
        "terms_accepted": True,
        "privacy_acknowledged": True,
        "cfc_link_accepted": True,
    }
    public = APIClient()
    assert (
        public.post("/api/v1/cfc/activate-instructor/", payload, format="json").status_code == 400
    )
    payload["token"] = match.group(2)
    payload["cfc_link_accepted"] = False
    assert (
        public.post("/api/v1/cfc/activate-instructor/", payload, format="json").status_code == 400
    )
    account = Account.objects.get(email="not-accepted@example.invalid")
    assert not account.is_active
    assert not Person.objects.filter(account=account).exists()


@pytest.mark.django_db
@override_settings(
    **{**CAPABILITIES, "EMAIL_BACKEND": "django.core.mail.backends.dummy.EmailBackend"}
)
def test_no_pre_registration_without_real_mail(cfc_manager):
    _, cfc, client = cfc_manager
    result = client.post(
        f"/api/v1/cfc/{cfc.pk}/instructors/",
        {
            "display_name": "Pessoa Nova",
            "email": "new2@example.invalid",
        },
        format="json",
    )
    assert result.status_code == 503
    assert not Account.objects.filter(email="new2@example.invalid").exists()
