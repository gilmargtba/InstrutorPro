from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("marketplace", "0013_visual_review_photo")]

    operations = [
        migrations.AlterField(
            model_name="instructordocument",
            name="document_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("DRIVER_LICENSE", "CNH"),
                    ("PROFESSIONAL_CREDENTIAL", "Credencial profissional"),
                    ("PROFESSIONAL_CERTIFICATE", "Certificado/credenciamento"),
                    ("OTHER_PROFESSIONAL", "Outro documento profissional"),
                    ("SELFIE_WITH_CNH", "Foto com CNH para conferência visual"),
                ],
                max_length=32,
            ),
        ),
        migrations.RemoveConstraint(
            model_name="instructordocument",
            name="ck_document_requirement_or_generic",
        ),
        migrations.AddConstraint(
            model_name="instructordocument",
            constraint=models.CheckConstraint(
                condition=models.Q(requirement__isnull=False)
                | models.Q(
                    document_type__in=[
                        "DRIVER_LICENSE",
                        "PROFESSIONAL_CREDENTIAL",
                        "PROFESSIONAL_CERTIFICATE",
                        "OTHER_PROFESSIONAL",
                        "SELFIE_WITH_CNH",
                    ],
                    verification_request__isnull=False,
                ),
                name="ck_document_requirement_or_generic",
            ),
        ),
    ]
