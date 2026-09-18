from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("discovery", "0004_codex_02e_workflow")]

    operations = [
        migrations.AddField(
            model_name="professionalverification",
            name="authority",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="professionalverification",
            name="method",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="professionalverification",
            name="provenance_reference",
            field=models.CharField(blank=True, max_length=160),
        ),
    ]
