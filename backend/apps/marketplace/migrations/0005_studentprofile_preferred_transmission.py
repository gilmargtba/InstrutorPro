import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("marketplace", "0004_instructordocument_credential_uf_and_more")]
    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="preferred_transmission",
            field=models.CharField(default="INDIFFERENT", max_length=12),
        ),
        migrations.CreateModel(
            name="InstructorOnboardingDraft",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("current_step", models.PositiveSmallIntegerField(default=1)),
                ("completed_steps", models.JSONField(default=list)),
                ("region", models.CharField(blank=True, max_length=100)),
                ("credential_identifier", models.CharField(blank=True, max_length=160)),
                ("credential_issued_at", models.DateField(blank=True, null=True)),
                ("credential_valid_until", models.DateField(blank=True, null=True)),
                (
                    "data_mode",
                    models.CharField(
                        choices=[("SYNTHETIC", "Sintético"), ("REAL", "Real")], max_length=12
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "instructor",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        related_name="onboarding_draft",
                        to="discovery.instructorprofile",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="instructoronboardingdraft",
            constraint=models.CheckConstraint(
                condition=models.Q(("current_step__gte", 1), ("current_step__lte", 7)),
                name="ck_onboarding_draft_step",
            ),
        ),
    ]
