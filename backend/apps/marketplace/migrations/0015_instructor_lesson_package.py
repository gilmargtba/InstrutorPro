import uuid

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


def seed_premium_draft(apps, schema_editor):
    Plan = apps.get_model("marketplace", "Plan")
    Plan.objects.get_or_create(
        code="PREMIUM",
        defaults={
            "name": "Premium",
            "description": "Catálogo preparado; assinatura e cobrança não habilitadas.",
            "status": "DRAFT",
            "billing_interval": "MONTHLY",
            "price_amount": None,
            "display_order": 30,
            "is_public": False,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("marketplace", "0014_instructor_document_driver_license")]

    operations = [
        migrations.CreateModel(
            name="InstructorLessonPackage",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=120)),
                ("category", models.CharField(max_length=1)),
                ("lesson_count", models.PositiveSmallIntegerField()),
                ("price_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("vehicle_included", models.BooleanField(default=False)),
                ("description", models.CharField(blank=True, max_length=500)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "data_mode",
                    models.CharField(
                        choices=[("SYNTHETIC", "Sintético"), ("REAL", "Real")], max_length=12
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "instructor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lesson_packages",
                        to="discovery.instructorprofile",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at", "id"],
                "verbose_name": "pacote de aulas do instrutor",
                "verbose_name_plural": "pacotes de aulas dos instrutores",
            },
        ),
        migrations.AddIndex(
            model_name="instructorlessonpackage",
            index=models.Index(
                fields=["instructor", "is_active", "created_at"],
                name="marketplace_package_active_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="instructorlessonpackage",
            constraint=models.CheckConstraint(
                condition=Q(category__in=["A", "B", "C", "D", "E"]), name="ck_package_category"
            ),
        ),
        migrations.AddConstraint(
            model_name="instructorlessonpackage",
            constraint=models.CheckConstraint(
                condition=Q(lesson_count__in=[2, 5, 10]), name="ck_package_lesson_count"
            ),
        ),
        migrations.AddConstraint(
            model_name="instructorlessonpackage",
            constraint=models.CheckConstraint(
                condition=Q(price_amount__gt=0), name="ck_package_price_positive"
            ),
        ),
        migrations.RunPython(seed_premium_draft, migrations.RunPython.noop),
    ]
