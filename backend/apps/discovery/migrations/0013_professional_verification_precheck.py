from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("discovery", "0012_professional_verification_approval_notice")]

    operations = [
        migrations.AddField(
            model_name="professionalverificationrequest",
            name="precheck_status",
            field=models.CharField(
                choices=[
                    ("NOT_STARTED", "Ainda não iniciada"),
                    ("IN_PROGRESS", "Em pré-validação"),
                    ("READY_FOR_HUMAN_REVIEW", "Pronta para análise humana"),
                    ("NEEDS_CORRECTION", "Correção necessária"),
                ],
                db_index=True,
                default="NOT_STARTED",
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="professionalverificationrequest",
            name="precheck_issues",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="professionalverificationrequest",
            name="precheck_checked_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
