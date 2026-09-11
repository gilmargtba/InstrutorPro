import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("marketplace", "0006_instructorcontactchannel_instructoroffer_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Entitlement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=48, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Plan",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("code", models.CharField(max_length=32, unique=True)),
                ("name", models.CharField(max_length=80)),
                ("description", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("DRAFT", "Rascunho"), ("ACTIVE", "Ativo"), ("ARCHIVED", "Arquivado")], default="DRAFT", max_length=16)),
                ("billing_interval", models.CharField(choices=[("NONE", "Sem cobrança"), ("MONTHLY", "Mensal"), ("YEARLY", "Anual")], default="NONE", max_length=16)),
                ("price_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("display_order", models.PositiveSmallIntegerField(default=0)),
                ("is_public", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["display_order", "code"], "permissions": [("manage_saas", "Can manage SaaS plans and subscriptions")]},
        ),
        migrations.CreateModel(
            name="PlanEntitlement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("entitlement", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="plan_entitlements", to="marketplace.entitlement")),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="plan_entitlements", to="marketplace.plan")),
            ],
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("TRIALING", "Em teste"), ("ACTIVE", "Ativa"), ("PAST_DUE", "Em atraso"), ("CANCELLED", "Cancelada"), ("EXPIRED", "Expirada")], max_length=16)),
                ("started_at", models.DateTimeField()),
                ("trial_ends_at", models.DateTimeField(blank=True, null=True)),
                ("current_period_start", models.DateTimeField(blank=True, null=True)),
                ("current_period_end", models.DateTimeField(blank=True, null=True)),
                ("cancel_at_period_end", models.BooleanField(default=False)),
                ("cancelled_at", models.DateTimeField(blank=True, null=True)),
                ("provider", models.CharField(blank=True, max_length=40)),
                ("provider_customer_id", models.CharField(blank=True, max_length=160)),
                ("provider_subscription_id", models.CharField(blank=True, max_length=160)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subscriptions", to=settings.AUTH_USER_MODEL)),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subscriptions", to="marketplace.plan")),
            ],
        ),
        migrations.AddConstraint(model_name="plan", constraint=models.CheckConstraint(condition=models.Q(("price_amount__isnull", True), ("price_amount__gte", 0), _connector="OR"), name="ck_plan_price_nonnegative")),
        migrations.AddConstraint(model_name="planentitlement", constraint=models.UniqueConstraint(fields=("plan", "entitlement"), name="uq_plan_entitlement")),
        migrations.AddIndex(model_name="subscription", index=models.Index(fields=["account", "status"], name="marketplace_account_4791ba_idx")),
        migrations.AddConstraint(model_name="subscription", constraint=models.UniqueConstraint(condition=models.Q(("status__in", ["TRIALING", "ACTIVE", "PAST_DUE"])), fields=("account",), name="uq_active_subscription_per_account")),
    ]
