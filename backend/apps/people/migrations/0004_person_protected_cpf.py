from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("people", "0003_person_birth_date_person_phone")]

    operations = [
        migrations.AddField(
            model_name="person",
            name="cpf_ciphertext",
            field=models.TextField(blank=True, editable=False),
        ),
        migrations.AddField(
            model_name="person",
            name="cpf_fingerprint",
            field=models.CharField(editable=False, max_length=64, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="person",
            name="cpf_key_version",
            field=models.CharField(blank=True, editable=False, max_length=20),
        ),
        migrations.AddField(
            model_name="person",
            name="cpf_last2",
            field=models.CharField(blank=True, editable=False, max_length=2),
        ),
    ]
