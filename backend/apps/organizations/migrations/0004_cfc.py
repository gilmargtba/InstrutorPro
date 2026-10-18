import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.organizations.validators


class Migration(migrations.Migration):
    dependencies = [
        ("organizations", "0003_alter_clinic_options_alter_clinicmembership_options"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("people", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CFC",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("display_name", models.CharField(max_length=150, verbose_name="nome do CFC")),
                (
                    "cnpj",
                    models.CharField(
                        max_length=14,
                        unique=True,
                        validators=[apps.organizations.validators.validate_cnpj],
                        verbose_name="CNPJ",
                    ),
                ),
                (
                    "declared_instructor_count",
                    models.PositiveIntegerField(default=0, verbose_name="instrutores informados"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=False, verbose_name="acesso ao painel autorizado"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "CFC", "verbose_name_plural": "CFCs"},
        ),
        migrations.CreateModel(
            name="CFCMembership",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "cfc",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="memberships",
                        to="organizations.cfc",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cfc_memberships",
                        to="people.person",
                    ),
                ),
            ],
            options={
                "verbose_name": "responsável pelo CFC",
                "verbose_name_plural": "responsáveis pelos CFCs",
            },
        ),
        migrations.AddConstraint(
            model_name="cfcmembership",
            constraint=models.UniqueConstraint(fields=("cfc", "person"), name="uq_cfc_person"),
        ),
        migrations.CreateModel(
            name="CFCInstructorLink",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("display_name", models.CharField(max_length=120, verbose_name="nome informado")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Aguardando instrutor"),
                            ("ACCEPTED", "Aceito pelo instrutor"),
                        ],
                        default="PENDING",
                        max_length=12,
                    ),
                ),
                ("invited_at", models.DateTimeField(auto_now_add=True)),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "account",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cfc_instructor_link",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "cfc",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="instructor_links",
                        to="organizations.cfc",
                    ),
                ),
            ],
            options={
                "verbose_name": "pré-cadastro de instrutor do CFC",
                "verbose_name_plural": "pré-cadastros de instrutores dos CFCs",
            },
        ),
    ]
