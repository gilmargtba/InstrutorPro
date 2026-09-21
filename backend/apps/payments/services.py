import hashlib

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.marketplace.capabilities import enabled

from .models import PaymentOrder, PaymentTransaction, PaymentWebhookEvent

ALLOWED_TRANSITIONS = {
    PaymentOrder.Status.CREATED: {PaymentOrder.Status.PENDING, PaymentOrder.Status.CANCELLED},
    PaymentOrder.Status.PENDING: {
        PaymentOrder.Status.PAID,
        PaymentOrder.Status.FAILED,
        PaymentOrder.Status.CANCELLED,
    },
    PaymentOrder.Status.PAID: {PaymentOrder.Status.REFUNDED},
    PaymentOrder.Status.FAILED: set(),
    PaymentOrder.Status.CANCELLED: set(),
    PaymentOrder.Status.REFUNDED: set(),
}


@transaction.atomic
def create_payment(*, account, amount_minor, idempotency_key, provider):
    if not enabled("REAL_PAYMENTS"):
        raise PermissionError("REAL_PAYMENTS_DISABLED")
    order, created = PaymentOrder.objects.get_or_create(
        idempotency_key=idempotency_key,
        defaults={
            "account": account,
            "provider": provider.code,
            "amount_minor": amount_minor,
        },
    )
    if not created:
        if order.account_id != account.id or order.amount_minor != amount_minor:
            raise ValueError("IDEMPOTENCY_KEY_CONFLICT")
        return order
    result = provider.create_payment(
        reference=str(order.id), amount_minor=amount_minor, idempotency_key=idempotency_key
    )
    order.provider_payment_id = result.payment_id
    order.status = result.status
    order.save(update_fields=["provider_payment_id", "status", "updated_at"])
    return order


@transaction.atomic
def process_webhook(*, provider, signature, raw_body):
    if not provider.verify_webhook(signature=signature, raw_body=raw_body):
        raise PermissionError("INVALID_WEBHOOK_SIGNATURE")
    event = provider.parse_webhook(raw_body)
    receipt, created = PaymentWebhookEvent.objects.get_or_create(
        provider=provider.code,
        provider_event_id=event.event_id,
        defaults={"payload_sha256": hashlib.sha256(raw_body).hexdigest()},
    )
    if not created:
        return receipt, False
    order = PaymentOrder.objects.select_for_update().get(
        provider=provider.code, provider_payment_id=event.payment_id
    )
    if event.amount_minor != order.amount_minor:
        receipt.status = PaymentWebhookEvent.Status.REJECTED
        receipt.error_code = "AMOUNT_MISMATCH"
        receipt.processed_at = timezone.now()
        receipt.save(update_fields=["status", "error_code", "processed_at"])
        raise ValueError("AMOUNT_MISMATCH")
    if event.status not in ALLOWED_TRANSITIONS[order.status]:
        receipt.status = PaymentWebhookEvent.Status.REJECTED
        receipt.error_code = "INVALID_STATUS_TRANSITION"
        receipt.processed_at = timezone.now()
        receipt.save(update_fields=["status", "error_code", "processed_at"])
        raise ValueError("INVALID_STATUS_TRANSITION")
    previous = order.status
    order.status = event.status
    order.save(update_fields=["status", "updated_at"])
    PaymentTransaction.objects.create(
        order=order,
        provider_event_id=event.event_id,
        previous_status=previous,
        new_status=event.status,
        amount_minor=event.amount_minor,
        occurred_at=timezone.now(),
    )
    receipt.status = PaymentWebhookEvent.Status.PROCESSED
    receipt.processed_at = timezone.now()
    receipt.save(update_fields=["status", "processed_at"])
    AuditEvent.objects.create(
        action="payments.webhook.processed",
        target_type="payments.PaymentOrder",
        target_id=order.id,
        metadata={"provider": provider.code, "event_id": event.event_id, "status": event.status},
    )
    if order.subscription_id and event.status == PaymentOrder.Status.PAID:
        if not enabled("REAL_PRO_BILLING"):
            raise PermissionError("REAL_PRO_BILLING_DISABLED")
        order.subscription.status = order.subscription.Status.ACTIVE
        order.subscription.save(update_fields=["status", "updated_at"])
    return receipt, True


def configured_provider():
    # No real adapter is selected in Fatia 8J. Fake is restricted to tests.
    if settings.PAYMENT_PROVIDER == "fake" and settings.APP_ENV == "TEST":
        from .providers import FakePaymentProvider

        return FakePaymentProvider(settings.PAYMENT_WEBHOOK_SECRET)
    raise LookupError("PAYMENT_PROVIDER_NOT_CONFIGURED")
