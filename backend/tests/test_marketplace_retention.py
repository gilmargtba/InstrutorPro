from datetime import timedelta
from io import StringIO
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.marketplace.models import DataMode, MarketplaceEvent
from apps.marketplace.retention import (
    RETAINED_EVENT_TYPES,
    _delete_batch,
    enforce_marketplace_analytics_retention,
)


def event(*, age_days, event_type=MarketplaceEvent.Type.SEARCH_PERFORMED, instructor=None):
    item = MarketplaceEvent.objects.create(
        event_type=event_type,
        instructor=instructor,
        session_hash=uuid4().hex * 2,
        dedupe_bucket=timezone.now().replace(minute=0, second=0, microsecond=0),
        source="retention-test",
        category="B",
        city="Porto Alegre",
        uf="RS",
        data_mode=DataMode.REAL,
    )
    MarketplaceEvent.objects.filter(pk=item.pk).update(
        created_at=timezone.now() - timedelta(days=age_days)
    )
    item.refresh_from_db()
    return item


@pytest.mark.django_db
def test_event_with_89_days_remains():
    item = event(age_days=89)
    result = enforce_marketplace_analytics_retention()
    assert result.processed == 0
    assert MarketplaceEvent.objects.filter(pk=item.pk).exists()


@pytest.mark.django_db
def test_event_exactly_at_limit_remains():
    now = timezone.now()
    item = event(age_days=1)
    MarketplaceEvent.objects.filter(pk=item.pk).update(created_at=now - timedelta(days=90))
    result = enforce_marketplace_analytics_retention(now=now)
    assert result.processed == 0
    assert MarketplaceEvent.objects.filter(pk=item.pk).exists()


@pytest.mark.django_db
def test_event_older_than_90_days_is_deleted_and_run_is_idempotent():
    item = event(age_days=91)
    first = enforce_marketplace_analytics_retention()
    second = enforce_marketplace_analytics_retention()
    assert first.processed == 1
    assert second.processed == 0
    assert not MarketplaceEvent.objects.filter(pk=item.pk).exists()


def test_retention_scope_is_limited_to_four_approved_event_types():
    assert set(RETAINED_EVENT_TYPES) == {
        MarketplaceEvent.Type.SEARCH_PERFORMED,
        MarketplaceEvent.Type.SEARCH_RESULT_IMPRESSION,
        MarketplaceEvent.Type.INSTRUCTOR_PROFILE_VIEWED,
        MarketplaceEvent.Type.WHATSAPP_CONTACT_CLICKED,
    }


@pytest.mark.django_db
def test_recent_event_remains():
    item = event(age_days=0)
    enforce_marketplace_analytics_retention()
    assert MarketplaceEvent.objects.filter(pk=item.pk).exists()


@pytest.mark.django_db
def test_expired_event_is_deleted_without_retaining_sensitive_fields():
    item = event(age_days=91)
    item.source = "phone=+5551999999999"
    item.city = "content=hello coordinates=-30,-51 address=private"
    item.save(update_fields=["source", "city"])
    enforce_marketplace_analytics_retention()
    assert not MarketplaceEvent.objects.filter(pk=item.pk).exists()
    audit = AuditEvent.objects.get(action="MARKETPLACE_ANALYTICS_RETENTION_ENFORCED")
    serialized = str(audit.metadata)
    assert "+5551" not in serialized
    assert "hello" not in serialized
    assert "-30" not in serialized
    assert "private" not in serialized


@pytest.mark.django_db
def test_dry_run_reports_without_modifying_database():
    item = event(age_days=91)
    output = StringIO()
    call_command("enforce_marketplace_analytics_retention", "--dry-run", stdout=output)
    assert MarketplaceEvent.objects.filter(pk=item.pk).exists()
    assert "RETENTION_ELIGIBLE=1" in output.getvalue()
    assert "RETENTION_PROCESSED=0" in output.getvalue()
    assert not AuditEvent.objects.exists()


@pytest.mark.django_db
def test_partial_batch_failure_does_not_corrupt_failing_batch():
    first = event(age_days=92)
    second = event(age_days=91)

    calls = 0

    def delete_then_fail(ids):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("injected batch failure")
        return _delete_batch(ids)

    with (
        patch(
            "apps.marketplace.retention._delete_batch",
            side_effect=delete_then_fail,
        ),
        pytest.raises(RuntimeError),
    ):
        enforce_marketplace_analytics_retention(batch_size=1)
    assert not MarketplaceEvent.objects.filter(pk=first.pk).exists()
    assert MarketplaceEvent.objects.filter(pk=second.pk).exists()
    audit = AuditEvent.objects.get(action="MARKETPLACE_ANALYTICS_RETENTION_FAILED")
    assert audit.metadata["processed_count"] == 1
    assert audit.metadata["completed_batch_count"] == 1
    assert audit.metadata["error_type"] == "RuntimeError"


@pytest.mark.django_db
def test_deleting_expired_event_preserves_current_analytics():
    unrelated_audit = AuditEvent.objects.create(
        action="SECURITY_EVENT",
        target_type="Account",
        reason_code="TEST",
    )
    expired = event(age_days=91)
    recent = event(age_days=1)
    enforce_marketplace_analytics_retention()
    assert not MarketplaceEvent.objects.filter(pk=expired.pk).exists()
    assert MarketplaceEvent.objects.filter(pk=recent.pk).exists()
    assert MarketplaceEvent.objects.count() == 1
    assert AuditEvent.objects.filter(pk=unrelated_audit.pk).exists()


@pytest.mark.django_db
def test_command_rejects_unsafe_batch_size():
    with pytest.raises(Exception, match="batch_size must be between"):
        call_command("enforce_marketplace_analytics_retention", "--batch-size", "0")
