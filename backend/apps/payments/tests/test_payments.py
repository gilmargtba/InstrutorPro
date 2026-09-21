import json

import pytest
from django.test import override_settings
from django.utils import timezone

from apps.accounts.models import Account
from apps.marketplace.models import Plan, Subscription
from apps.payments.models import PaymentOrder, PaymentTransaction, PaymentWebhookEvent
from apps.payments.providers import FakePaymentProvider
from apps.payments.services import create_payment, process_webhook

pytestmark = pytest.mark.django_db


def account():
    return Account.objects.create_user(
        username="payer", email="payer@example.com", password="safe-test-password"
    )


@override_settings(
    REAL_PRODUCTION_AUTHORIZATION="FULL_PRODUCTION", REAL_PAYMENTS=True, REAL_PRO_BILLING=False
)
def test_payment_creation_is_idempotent_and_conflicts_fail_closed():
    owner = account()
    provider = FakePaymentProvider()
    first = create_payment(
        account=owner, amount_minor=1290, idempotency_key="checkout-1", provider=provider
    )
    second = create_payment(
        account=owner, amount_minor=1290, idempotency_key="checkout-1", provider=provider
    )
    assert first.id == second.id
    assert PaymentOrder.objects.count() == 1
    with pytest.raises(ValueError, match="IDEMPOTENCY_KEY_CONFLICT"):
        create_payment(
            account=owner, amount_minor=9999, idempotency_key="checkout-1", provider=provider
        )


def test_real_payment_is_blocked_by_default():
    with pytest.raises(PermissionError, match="REAL_PAYMENTS_DISABLED"):
        create_payment(
            account=account(),
            amount_minor=1290,
            idempotency_key="disabled",
            provider=FakePaymentProvider(),
        )


def webhook(provider, order, event_id, status):
    raw = json.dumps(
        {
            "event_id": event_id,
            "payment_id": order.provider_payment_id,
            "status": status,
            "amount_minor": order.amount_minor,
        }
    ).encode()
    return raw, provider.sign(raw)


@override_settings(
    REAL_PRODUCTION_AUTHORIZATION="FULL_PRODUCTION", REAL_PAYMENTS=True, REAL_PRO_BILLING=False
)
def test_valid_webhook_is_idempotent_and_invalid_signature_is_rejected():
    provider = FakePaymentProvider()
    order = create_payment(
        account=account(), amount_minor=1290, idempotency_key="webhook-1", provider=provider
    )
    raw, signature = webhook(provider, order, "evt-paid", "PAID")
    with pytest.raises(PermissionError, match="INVALID_WEBHOOK_SIGNATURE"):
        process_webhook(provider=provider, signature="invalid", raw_body=raw)
    receipt, processed = process_webhook(provider=provider, signature=signature, raw_body=raw)
    duplicate, duplicate_processed = process_webhook(
        provider=provider, signature=signature, raw_body=raw
    )
    order.refresh_from_db()
    assert order.status == PaymentOrder.Status.PAID
    assert processed is True and duplicate_processed is False
    assert receipt.id == duplicate.id
    assert PaymentWebhookEvent.objects.count() == 1
    assert PaymentTransaction.objects.count() == 1


@override_settings(
    REAL_PRODUCTION_AUTHORIZATION="FULL_PRODUCTION", REAL_PAYMENTS=True, REAL_PRO_BILLING=True
)
def test_pro_entitlement_activates_only_after_confirmed_payment():
    owner = account()
    plan = Plan.objects.create(
        code="PRO-TEST",
        name="Pro Test",
        status=Plan.Status.DRAFT,
        billing_interval=Plan.BillingInterval.MONTHLY,
    )
    subscription = Subscription.objects.create(
        account=owner, plan=plan, status=Subscription.Status.PAST_DUE, started_at=timezone.now()
    )
    provider = FakePaymentProvider()
    order = create_payment(
        account=owner, amount_minor=1290, idempotency_key="pro-1", provider=provider
    )
    order.subscription = subscription
    order.save(update_fields=["subscription", "updated_at"])
    subscription.refresh_from_db()
    assert subscription.status == Subscription.Status.PAST_DUE
    raw, signature = webhook(provider, order, "evt-pro-paid", "PAID")
    process_webhook(provider=provider, signature=signature, raw_body=raw)
    subscription.refresh_from_db()
    assert subscription.status == Subscription.Status.ACTIVE


@override_settings(
    APP_ENV="TEST",
    PAYMENT_PROVIDER="fake",
    PAYMENT_WEBHOOK_SECRET="endpoint-secret",
    REAL_PRODUCTION_AUTHORIZATION="FULL_PRODUCTION",
    REAL_PAYMENTS=True,
)
def test_webhook_endpoint_rejects_invalid_and_deduplicates(client):
    provider = FakePaymentProvider("endpoint-secret")
    order = create_payment(
        account=account(), amount_minor=1290, idempotency_key="endpoint-1", provider=provider
    )
    raw, signature = webhook(provider, order, "evt-endpoint", "PAID")
    url = "/api/v1/payments/webhook/fake/"
    assert client.post(url, data=raw, content_type="application/json").status_code == 401
    first = client.post(
        url,
        data=raw,
        content_type="application/json",
        HTTP_X_PAYMENT_SIGNATURE=signature,
    )
    second = client.post(
        url,
        data=raw,
        content_type="application/json",
        HTTP_X_PAYMENT_SIGNATURE=signature,
    )
    assert first.status_code == 200 and first.json()["processed"] is True
    assert second.status_code == 200 and second.json()["processed"] is False


@override_settings(
    REAL_PRODUCTION_AUTHORIZATION="FULL_PRODUCTION", REAL_PAYMENTS=True, REAL_PRO_BILLING=False
)
def test_cancel_and_refund_are_monotonic():
    provider = FakePaymentProvider()
    cancelled = create_payment(
        account=account(), amount_minor=1000, idempotency_key="cancel-1", provider=provider
    )
    raw, signature = webhook(provider, cancelled, "evt-cancel", "CANCELLED")
    process_webhook(provider=provider, signature=signature, raw_body=raw)
    cancelled.refresh_from_db()
    assert cancelled.status == PaymentOrder.Status.CANCELLED

    paid = create_payment(
        account=Account.objects.create_user(
            username="payer2", email="payer2@example.com", password="safe-test-password"
        ),
        amount_minor=2000,
        idempotency_key="refund-1",
        provider=provider,
    )
    raw, signature = webhook(provider, paid, "evt-paid-2", "PAID")
    process_webhook(provider=provider, signature=signature, raw_body=raw)
    raw, signature = webhook(provider, paid, "evt-refund", "REFUNDED")
    process_webhook(provider=provider, signature=signature, raw_body=raw)
    paid.refresh_from_db()
    assert paid.status == PaymentOrder.Status.REFUNDED
