import uuid

from django.conf import settings
from django.db import models


class PaymentCustomer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payment_customer"
    )
    provider = models.CharField(max_length=40)
    provider_customer_id = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_customer_id"], name="uq_payment_provider_customer"
            )
        ]

    def __str__(self):
        return f"{self.provider}:{self.id}"


class PaymentOrder(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Criada"
        PENDING = "PENDING", "Pendente"
        PAID = "PAID", "Paga"
        FAILED = "FAILED", "Falhou"
        CANCELLED = "CANCELLED", "Cancelada"
        REFUNDED = "REFUNDED", "Estornada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payment_orders"
    )
    subscription = models.ForeignKey(
        "marketplace.Subscription",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="payment_orders",
    )
    provider = models.CharField(max_length=40)
    provider_payment_id = models.CharField(max_length=160, blank=True)
    idempotency_key = models.CharField(max_length=128, unique=True)
    amount_minor = models.PositiveBigIntegerField()
    currency = models.CharField(max_length=3, default="BRL")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_payment_id"],
                condition=~models.Q(provider_payment_id=""),
                name="uq_payment_provider_payment",
            ),
            models.CheckConstraint(
                condition=models.Q(amount_minor__gt=0), name="ck_payment_amount_gt0"
            ),
        ]

    def __str__(self):
        return f"{self.id}:{self.status}"


class PaymentTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(PaymentOrder, on_delete=models.PROTECT, related_name="transactions")
    provider_event_id = models.CharField(max_length=160)
    previous_status = models.CharField(max_length=16, choices=PaymentOrder.Status.choices)
    new_status = models.CharField(max_length=16, choices=PaymentOrder.Status.choices)
    amount_minor = models.PositiveBigIntegerField()
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "provider_event_id"], name="uq_payment_transaction_event"
            )
        ]

    def __str__(self):
        return f"{self.order_id}:{self.new_status}"


class PaymentWebhookEvent(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "Recebido"
        PROCESSED = "PROCESSED", "Processado"
        REJECTED = "REJECTED", "Rejeitado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=40)
    provider_event_id = models.CharField(max_length=160)
    payload_sha256 = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.RECEIVED)
    error_code = models.CharField(max_length=80, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_event_id"], name="uq_payment_webhook_event"
            )
        ]

    def __str__(self):
        return f"{self.provider}:{self.provider_event_id}"
