import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_alter_account_options_alter_externalidentity_options"),
        ("discovery", "0009_verification_requirements_snapshot"),
        ("marketplace", "0009_alter_documentrequirement_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="documentrequirement",
            name="source_reference",
            field=models.CharField(default="", max_length=240),
        ),
        migrations.AddField(
            model_name="documentrequirement",
            name="approval_recorded_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="documentrequirement",
            name="approval_recorded_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="accounts.account",
            ),
        ),
        migrations.AddField(
            model_name="instructordocument",
            name="verification_request",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="documents",
                to="discovery.professionalverificationrequest",
            ),
        ),
        migrations.AddField(
            model_name="instructordocument",
            name="scanned_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="instructordocument",
            name="retention_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="instructordocument",
            name="legal_hold",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="instructordocument",
            name="scan_status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Aguardando análise"),
                    ("CLEAN", "Arquivo analisado"),
                    ("BLOCKED", "Bloqueado"),
                ],
                default="PENDING",
                max_length=20,
            ),
        ),
    ]
