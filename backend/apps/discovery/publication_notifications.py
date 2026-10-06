"""Transactional notice after a real instructor is manually published."""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.audit.models import AuditEvent

from .models import InstructorProfile, PublicationDecision
from .selectors import published_instructor_profiles

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
STALE_SENDING_AFTER = timedelta(minutes=30)


def email_available():
    backend = settings.EMAIL_BACKEND
    if backend not in {
        "django.core.mail.backends.smtp.EmailBackend",
        "django.core.mail.backends.locmem.EmailBackend",  # Test-only transport.
    }:
        return False
    return bool(
        settings.DEFAULT_FROM_EMAIL
        and (backend != "django.core.mail.backends.smtp.EmailBackend" or settings.EMAIL_HOST)
    )


def queue_publication_notice(decision_id):
    """A broker outage must not turn a committed publication into an Admin 500."""
    try:
        from .tasks import deliver_publication_notice_task

        deliver_publication_notice_task.delay(str(decision_id))
    except Exception:
        logger.exception("Could not enqueue publication notice for decision %s", decision_id)


def deliver_publication_notice(decision_id):
    if not email_available():
        return "EMAIL_UNAVAILABLE"

    with transaction.atomic():
        record = (
            PublicationDecision.objects.select_for_update()
            .select_related("profile__person__account")
            .get(pk=decision_id)
        )
        if record.notice_status == record.NoticeStatus.SENDING and (
            not record.notice_attempted_at
            or record.notice_attempted_at > timezone.now() - STALE_SENDING_AFTER
        ):
            return "IN_PROGRESS"
        if record.notice_status not in {
            record.NoticeStatus.PENDING,
            record.NoticeStatus.SENDING,
        }:
            return record.notice_status
        profile = record.profile
        latest_decision_id = (
            PublicationDecision.objects.filter(profile=profile)
            .order_by("-created_at", "-pk")
            .values_list("pk", flat=True)
            .first()
        )
        if (
            record.decision != PublicationDecision.Decision.APPROVE
            or profile.is_demo
            or profile.publication_status != InstructorProfile.PublicationStatus.APPROVED
            or latest_decision_id != record.pk
        ):
            record.notice_status = record.NoticeStatus.SKIPPED
            record.save(update_fields=["notice_status"])
            return "SKIPPED"
        if not published_instructor_profiles().filter(pk=profile.pk).exists():
            return "NOT_PUBLIC_YET"
        record.notice_status = record.NoticeStatus.SENDING
        record.notice_attempts += 1
        record.notice_attempted_at = timezone.now()
        record.save(update_fields=["notice_status", "notice_attempts", "notice_attempted_at"])
        recipient = record.notice_recipient
        profile_id = profile.pk

    try:
        public_url = f"{settings.FRONTEND_PUBLIC_URL}/aluno/instrutores/{profile_id}"
        sent = send_mail(
            "Seu perfil foi publicado — InstrutorProCNH",
            "Sua verificação interna e a decisão de publicação foram concluídas. "
            "Seu perfil está disponível para consulta na plataforma.\n\n"
            f"Veja o perfil público: {public_url}\n\n"
            "Esta publicação na plataforma não é credenciamento ou autorização emitida "
            "por órgão de trânsito.",
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        if sent != 1:
            raise RuntimeError("EMAIL_NOT_ACCEPTED")
    except Exception:
        logger.exception("Publication notice delivery failed for decision %s", decision_id)
        with transaction.atomic():
            record = PublicationDecision.objects.select_for_update().get(pk=decision_id)
            if record.notice_status == record.NoticeStatus.SENDING:
                record.notice_status = (
                    record.NoticeStatus.FAILED
                    if record.notice_attempts >= MAX_ATTEMPTS
                    else record.NoticeStatus.PENDING
                )
                record.save(update_fields=["notice_status"])
        return "DELIVERY_FAILED"

    with transaction.atomic():
        record = PublicationDecision.objects.select_for_update().get(pk=decision_id)
        if record.notice_status == record.NoticeStatus.SENDING:
            record.notice_status = record.NoticeStatus.SENT
            record.notice_sent_at = timezone.now()
            record.save(update_fields=["notice_status", "notice_sent_at"])
            AuditEvent.objects.create(
                action="discovery.publication_notice.sent",
                target_type="discovery.PublicationDecision",
                target_id=record.pk,
                reason_code="TRANSACTIONAL_EMAIL",
                metadata={"channel": "EMAIL"},
            )
    return "SENT"


def due_publication_notice_ids(limit=50):
    stale = timezone.now() - STALE_SENDING_AFTER
    return list(
        PublicationDecision.objects.filter(
            Q(notice_status=PublicationDecision.NoticeStatus.PENDING)
            | Q(
                notice_status=PublicationDecision.NoticeStatus.SENDING,
                notice_attempted_at__lt=stale,
            )
        )
        .order_by("created_at")
        .values_list("pk", flat=True)[:limit]
    )
