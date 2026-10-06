from unittest.mock import patch

import pytest
from django.core import mail
from django.test import override_settings

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile, PublicationDecision
from apps.discovery.publication_notifications import deliver_publication_notice
from apps.people.models import Person

EMAIL_SETTINGS = {
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "DEFAULT_FROM_EMAIL": "no-reply@example.invalid",
    "FRONTEND_PUBLIC_URL": "https://example.test",
}


def case():
    owner = Account.objects.create_user(
        username="notified-owner", email="owner@example.invalid", password="test-password-123"
    )
    reviewer = Account.objects.create_user(
        username="notified-admin", email="admin@example.invalid", password="test-password-123"
    )
    profile = InstructorProfile.objects.create(
        person=Person.objects.create(account=owner),
        display_name="Instrutor",
        is_demo=False,
        profile_status=InstructorProfile.Status.APPROVED,
        verification_status=InstructorProfile.VerificationStatus.VERIFIED,
        publication_status=InstructorProfile.PublicationStatus.APPROVED,
    )
    decision = PublicationDecision.objects.create(
        profile=profile,
        actor=reviewer,
        decision=PublicationDecision.Decision.APPROVE,
        reason="HUMAN_DECISION",
        notice_status=PublicationDecision.NoticeStatus.PENDING,
        notice_recipient=owner.email,
    )
    return profile, decision


@pytest.mark.django_db
@override_settings(**EMAIL_SETTINGS)
def test_published_real_profile_receives_one_minimal_email():
    profile, decision = case()
    with patch(
        "apps.discovery.publication_notifications.published_instructor_profiles",
        return_value=InstructorProfile.objects.filter(pk=profile.pk),
    ):
        assert deliver_publication_notice(decision.pk) == "SENT"
        assert deliver_publication_notice(decision.pk) == "SENT"
    decision.refresh_from_db()
    assert decision.notice_status == decision.NoticeStatus.SENT
    assert decision.notice_attempts == 1
    assert decision.notice_sent_at is not None
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["owner@example.invalid"]
    assert str(profile.pk) in mail.outbox[0].body
    assert "autorização emitida" in mail.outbox[0].body
    assert AuditEvent.objects.filter(action="discovery.publication_notice.sent").count() == 1


@pytest.mark.django_db
@override_settings(**EMAIL_SETTINGS)
def test_notice_is_skipped_after_unpublication_before_delivery():
    profile, decision = case()
    PublicationDecision.objects.create(
        profile=profile,
        actor=decision.actor,
        decision=PublicationDecision.Decision.UNPUBLISH,
        reason="HUMAN_DECISION",
    )
    assert deliver_publication_notice(decision.pk) == "SKIPPED"
    assert mail.outbox == []


@pytest.mark.django_db
@override_settings(**EMAIL_SETTINGS)
def test_email_failure_retries_without_changing_publication():
    profile, decision = case()
    with (
        patch(
            "apps.discovery.publication_notifications.published_instructor_profiles",
            return_value=InstructorProfile.objects.filter(pk=profile.pk),
        ),
        patch("apps.discovery.publication_notifications.send_mail", side_effect=OSError("down")),
    ):
        for _ in range(3):
            assert deliver_publication_notice(decision.pk) == "DELIVERY_FAILED"
    decision.refresh_from_db()
    profile.refresh_from_db()
    assert decision.notice_status == decision.NoticeStatus.FAILED
    assert decision.notice_attempts == 3
    assert profile.publication_status == profile.PublicationStatus.APPROVED
    assert mail.outbox == []


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
def test_unconfigured_email_leaves_notice_pending_for_later_retry():
    _, decision = case()
    assert deliver_publication_notice(decision.pk) == "EMAIL_UNAVAILABLE"
    decision.refresh_from_db()
    assert decision.notice_status == decision.NoticeStatus.PENDING
    assert decision.notice_attempts == 0
