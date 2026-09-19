from dataclasses import dataclass
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent

from .models import MarketplaceEvent

RETENTION_DAYS = 90
RETAINED_EVENT_TYPES = (
    MarketplaceEvent.Type.SEARCH_PERFORMED,
    MarketplaceEvent.Type.SEARCH_RESULT_IMPRESSION,
    MarketplaceEvent.Type.INSTRUCTOR_PROFILE_VIEWED,
    MarketplaceEvent.Type.WHATSAPP_CONTACT_CLICKED,
)


@dataclass(frozen=True)
class RetentionResult:
    eligible: int
    processed: int
    batches: int
    dry_run: bool


def analytics_retention_cutoff(*, now=None):
    return (now or timezone.now()) - timedelta(days=RETENTION_DAYS)


def eligible_marketplace_events(*, now=None):
    # Events exactly at the 90-day boundary remain until they are older than the policy window.
    return MarketplaceEvent.objects.filter(
        event_type__in=RETAINED_EVENT_TYPES,
        created_at__lt=analytics_retention_cutoff(now=now),
    ).order_by("created_at", "id")


@transaction.atomic
def _delete_batch(ids):
    queryset = MarketplaceEvent.objects.filter(id__in=ids)
    event_count = queryset.count()
    queryset.delete()
    return event_count


def enforce_marketplace_analytics_retention(*, dry_run=False, batch_size=500, now=None):
    if batch_size < 1 or batch_size > 5000:
        raise ValueError("batch_size must be between 1 and 5000")

    queryset = eligible_marketplace_events(now=now)
    eligible = queryset.count()
    if dry_run:
        return RetentionResult(eligible=eligible, processed=0, batches=0, dry_run=True)

    processed = 0
    batches = 0
    try:
        while True:
            ids = list(queryset.values_list("id", flat=True)[:batch_size])
            if not ids:
                break
            processed += _delete_batch(ids)
            batches += 1
    except Exception as exc:
        AuditEvent.objects.create(
            action="MARKETPLACE_ANALYTICS_RETENTION_FAILED",
            target_type="MarketplaceEvent",
            reason_code="PILOT_RETENTION_90_DAYS",
            metadata={
                "retention_days": RETENTION_DAYS,
                "eligible_count": eligible,
                "processed_count": processed,
                "completed_batch_count": batches,
                "strategy": "DELETE",
                "error_type": type(exc).__name__,
            },
        )
        raise

    AuditEvent.objects.create(
        action="MARKETPLACE_ANALYTICS_RETENTION_ENFORCED",
        target_type="MarketplaceEvent",
        reason_code="PILOT_RETENTION_90_DAYS",
        metadata={
            "retention_days": RETENTION_DAYS,
            "eligible_count": eligible,
            "processed_count": processed,
            "batch_count": batches,
            "strategy": "DELETE",
        },
    )
    return RetentionResult(
        eligible=eligible,
        processed=processed,
        batches=batches,
        dry_run=False,
    )
