from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("discovery", "0013_professional_verification_precheck")]

    operations = [
        migrations.AddField(
            model_name="professionalverificationrequest",
            name="admin_document_intake",
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
