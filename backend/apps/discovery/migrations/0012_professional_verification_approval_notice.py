from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("discovery", "0011_publication_notice_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="professionalverificationrequest",
            name="approval_notice_status",
            field=models.CharField(
                choices=[
                    ("NOT_APPLICABLE", "Não aplicável"),
                    ("PENDING", "Pendente"),
                    ("SENDING", "Enviando"),
                    ("SENT", "Enviado"),
                    ("FAILED", "Falhou"),
                    ("SKIPPED", "Cancelado"),
                ],
                default="NOT_APPLICABLE",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="professionalverificationrequest",
            name="approval_notice_recipient",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="professionalverificationrequest",
            name="approval_notice_attempts",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="professionalverificationrequest",
            name="approval_notice_attempted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="professionalverificationrequest",
            name="approval_notice_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
