from unittest.mock import patch

import pytest
from django.core import mail
from django.test import override_settings

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile, ProfessionalVerificationRequest
from apps.discovery.verification_notifications import deliver_verification_approval_notice
from apps.people.models import Person

EMAIL_SETTINGS = {
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "DEFAULT_FROM_EMAIL": "no-reply@example.invalid",
    "FRONTEND_PUBLIC_URL": "https://example.test",
}


def case(*, verified=True):
    owner = Account.objects.create_user(
        username="verification-owner", email="owner@example.invalid", password="test-password-123"
    )
    profile = InstructorProfile.objects.create(
        person=Person.objects.create(account=owner),
        display_name="Instrutor",
        is_demo=False,
        verification_status=(
            InstructorProfile.VerificationStatus.VERIFIED
            if verified
            else InstructorProfile.VerificationStatus.PENDING
        ),
    )
    record = ProfessionalVerificationRequest.objects.create(
        profile=profile,
        status=(
            ProfessionalVerificationRequest.Status.VERIFIED
            if verified
            else ProfessionalVerificationRequest.Status.SUBMITTED
        ),
        approval_notice_status=ProfessionalVerificationRequest.NoticeStatus.PENDING,
        approval_notice_recipient=owner.email,
    )
    return profile, record


@pytest.mark.django_db
@override_settings(**EMAIL_SETTINGS)
def test_human_verification_approval_sends_one_email_without_claiming_publication():
    _, record = case()
    assert deliver_verification_approval_notice(record.pk) == "SENT"
    assert deliver_verification_approval_notice(record.pk) == "SENT"
    record.refresh_from_db()
    assert record.approval_notice_status == record.NoticeStatus.SENT
    assert record.approval_notice_attempts == 1
    assert record.approval_notice_sent_at is not None
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["owner@example.invalid"]
    assert "verificação profissional interna foi aprovada" in mail.outbox[0].body
    assert "publicação do seu perfil na busca é uma etapa separada" in mail.outbox[0].body
    assert "credenciamento ou autorização emitida" in mail.outbox[0].body
    assert (
        AuditEvent.objects.filter(action="discovery.verification_approval_notice.sent").count() == 1
    )


@pytest.mark.django_db
@override_settings(**EMAIL_SETTINGS)
def test_unapproved_request_never_sends_approval_notice():
    _, record = case(verified=False)
    assert deliver_verification_approval_notice(record.pk) == "SKIPPED"
    assert mail.outbox == []


@pytest.mark.django_db
@override_settings(**EMAIL_SETTINGS)
def test_old_approval_is_not_emailed_after_new_review_begins():
    profile, record = case()
    ProfessionalVerificationRequest.objects.create(
        profile=profile, status=ProfessionalVerificationRequest.Status.DRAFT
    )
    assert deliver_verification_approval_notice(record.pk) == "SKIPPED"
    assert mail.outbox == []


@pytest.mark.django_db
@override_settings(**EMAIL_SETTINGS)
def test_email_failure_retries_without_undoing_approval():
    profile, record = case()
    with patch("apps.discovery.verification_notifications.send_mail", side_effect=OSError("down")):
        for _ in range(3):
            assert deliver_verification_approval_notice(record.pk) == "DELIVERY_FAILED"
    record.refresh_from_db()
    profile.refresh_from_db()
    assert record.approval_notice_status == record.NoticeStatus.FAILED
    assert record.approval_notice_attempts == 3
    assert profile.verification_status == profile.VerificationStatus.VERIFIED


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
def test_unconfigured_email_stays_pending_for_retry():
    _, record = case()
    assert deliver_verification_approval_notice(record.pk) == "EMAIL_UNAVAILABLE"
    record.refresh_from_db()
    assert record.approval_notice_status == record.NoticeStatus.PENDING
    assert record.approval_notice_attempts == 0
