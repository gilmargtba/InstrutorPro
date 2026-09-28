import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("territories", "0003_alter_country_options_alter_federativeunit_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="regulatoryreadiness",
            name="source_reference",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="regulatoryreadiness",
            name="notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="regulatoryreadiness",
            name="approved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="regulatoryreadiness",
            name="approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="regulatory_approvals",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="RegulatoryReadinessHistory",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[
                    ("NOT_REVIEWED", "Não revisada"),
                    ("RESEARCHING", "Em pesquisa"),
                    ("REVIEW_REQUIRED", "Revisão necessária"),
                    ("APPROVED", "Aprovada"),
                    ("SUSPENDED", "Suspensa"),
                ], max_length=20)),
                ("valid_from", models.DateField(blank=True, null=True)),
                ("valid_until", models.DateField(blank=True, null=True)),
                ("source_url", models.URLField(blank=True)),
                ("source_reference", models.CharField(blank=True, max_length=255)),
                ("notes", models.TextField(blank=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("recorded_at", models.DateTimeField(auto_now_add=True)),
                ("approved_by", models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL,
                )),
                ("reviewed_by", models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.PROTECT,
                    related_name="+", to=settings.AUTH_USER_MODEL,
                )),
                ("readiness", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="history", to="territories.regulatoryreadiness",
                )),
            ],
            options={
                "ordering": ["-recorded_at"],
                "verbose_name": "histórico de prontidão regulatória",
                "verbose_name_plural": "histórico de prontidão regulatória",
            },
        ),
    ]
