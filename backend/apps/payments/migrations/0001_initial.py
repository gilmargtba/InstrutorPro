import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("marketplace", "0008_seed_saas_catalog"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="PaymentCustomer",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("provider", models.CharField(max_length=40)),
                ("provider_customer_id", models.CharField(max_length=160)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("account", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="payment_customer", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="PaymentOrder",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("provider", models.CharField(max_length=40)),
                ("provider_payment_id", models.CharField(blank=True, max_length=160)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                ("amount_minor", models.PositiveBigIntegerField()),
                ("currency", models.CharField(default="BRL", max_length=3)),
                ("status", models.CharField(choices=[("CREATED", "Criada"), ("PENDING", "Pendente"), ("PAID", "Paga"), ("FAILED", "Falhou"), ("CANCELLED", "Cancelada"), ("REFUNDED", "Estornada")], default="CREATED", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payment_orders", to=settings.AUTH_USER_MODEL)),
                ("subscription", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="payment_orders", to="marketplace.subscription")),
            ],
        ),
        migrations.CreateModel(
            name="PaymentTransaction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("provider_event_id", models.CharField(max_length=160)),
                ("previous_status", models.CharField(choices=[("CREATED", "Criada"), ("PENDING", "Pendente"), ("PAID", "Paga"), ("FAILED", "Falhou"), ("CANCELLED", "Cancelada"), ("REFUNDED", "Estornada")], max_length=16)),
                ("new_status", models.CharField(choices=[("CREATED", "Criada"), ("PENDING", "Pendente"), ("PAID", "Paga"), ("FAILED", "Falhou"), ("CANCELLED", "Cancelada"), ("REFUNDED", "Estornada")], max_length=16)),
                ("amount_minor", models.PositiveBigIntegerField()),
                ("occurred_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transactions", to="payments.paymentorder")),
            ],
        ),
        migrations.CreateModel(
            name="PaymentWebhookEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("provider", models.CharField(max_length=40)),
                ("provider_event_id", models.CharField(max_length=160)),
                ("payload_sha256", models.CharField(max_length=64)),
                ("status", models.CharField(choices=[("RECEIVED", "Recebido"), ("PROCESSED", "Processado"), ("REJECTED", "Rejeitado")], default="RECEIVED", max_length=16)),
                ("error_code", models.CharField(blank=True, max_length=80)),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AddConstraint(model_name="paymentcustomer", constraint=models.UniqueConstraint(fields=("provider", "provider_customer_id"), name="uq_payment_provider_customer")),
        migrations.AddConstraint(model_name="paymentorder", constraint=models.UniqueConstraint(condition=models.Q(("provider_payment_id", ""), _negated=True), fields=("provider", "provider_payment_id"), name="uq_payment_provider_payment")),
        migrations.AddConstraint(model_name="paymentorder", constraint=models.CheckConstraint(condition=models.Q(("amount_minor__gt", 0)), name="ck_payment_amount_gt0")),
        migrations.AddConstraint(model_name="paymenttransaction", constraint=models.UniqueConstraint(fields=("order", "provider_event_id"), name="uq_payment_transaction_event")),
        migrations.AddConstraint(model_name="paymentwebhookevent", constraint=models.UniqueConstraint(fields=("provider", "provider_event_id"), name="uq_payment_webhook_event")),
    ]
