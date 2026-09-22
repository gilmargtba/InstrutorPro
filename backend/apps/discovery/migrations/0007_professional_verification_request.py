import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("people", "0004_person_protected_cpf"),
        ("discovery", "0006_instructorservicearea_optional_public_location"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProfessionalVerificationRequest",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("DRAFT", "Rascunho"), ("SUBMITTED", "Enviada"), ("UNDER_REVIEW", "Em análise"), ("VERIFIED", "Verificada"), ("REJECTED", "Rejeitada")], default="DRAFT", max_length=20)),
                ("submitted_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("review_started_at", models.DateTimeField(blank=True, null=True)),
                ("verification_method", models.CharField(blank=True, max_length=80)),
                ("verification_source", models.CharField(blank=True, max_length=160)),
                ("checked_at", models.DateTimeField(blank=True, null=True)),
                ("internal_notes", models.TextField(blank=True)),
                ("rejection_reason_code", models.CharField(blank=True, max_length=80)),
                ("public_message", models.CharField(blank=True, max_length=240)),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("decision_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="decided_professional_verification_requests", to=settings.AUTH_USER_MODEL)),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="verification_requests", to="discovery.instructorprofile")),
                ("reviewer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="assigned_professional_verification_requests", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["submitted_at", "created_at"],
                "permissions": [("review_professional_verification", "Can review professional verification"), ("reveal_protected_identifier", "Can reveal protected personal identifier")],
            },
        ),
        migrations.AddConstraint(
            model_name="professionalverificationrequest",
            constraint=models.UniqueConstraint(condition=models.Q(("status__in", ["DRAFT", "SUBMITTED", "UNDER_REVIEW"])), fields=("profile",), name="uq_active_professional_verification_request"),
        ),
    ]
