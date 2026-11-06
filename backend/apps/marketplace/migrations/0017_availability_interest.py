import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("marketplace", "0016_instructor_lesson_package_categories"),
        ("privacy", "0005_google_maps_privacy_notice"),
    ]

    operations = [
        migrations.CreateModel(
            name="AvailabilityInterestPolicy",
            fields=[
                ("id", models.PositiveSmallIntegerField(default=1, editable=False, primary_key=True, serialize=False)),
                ("enabled", models.BooleanField(default=False)),
                ("retention_days", models.PositiveSmallIntegerField(default=90)),
                ("consent_version", models.CharField(blank=True, max_length=40)),
                ("consent_text", models.TextField(blank=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("privacy_notice", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="privacy.privacynotice")),
            ],
            options={"verbose_name": "configuração do aviso de disponibilidade"},
        ),
        migrations.CreateModel(
            name="AvailabilityInterest",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("city", models.CharField(max_length=120)),
                ("uf", models.CharField(max_length=2)),
                ("name_encrypted", models.TextField()),
                ("phone_encrypted", models.TextField()),
                ("phone_fingerprint", models.CharField(max_length=64)),
                ("idempotency_key", models.UUIDField(unique=True)),
                ("status", models.CharField(choices=[("NEW", "Novo"), ("CONTACTED", "Contatado")], default="NEW", max_length=12)),
                ("consent_version", models.CharField(max_length=40)),
                ("consent_text_sha256", models.CharField(max_length=64)),
                ("consented_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField(db_index=True)),
                ("privacy_notice", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="privacy.privacynotice")),
            ],
            options={"verbose_name": "interessado em disponibilidade de instrutor", "verbose_name_plural": "interessados em disponibilidade de instrutores"},
        ),
        migrations.AddIndex(model_name="availabilityinterest", index=models.Index(fields=["uf", "city", "status"], name="mkt_interest_uf_city_idx")),
    ]
