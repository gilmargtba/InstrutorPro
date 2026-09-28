from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("territories", "0004_regulatory_readiness_evidence_history"),
    ]

    operations = [
        migrations.AddField(
            model_name="regulatoryreadiness",
            name="source_authority",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="regulatoryreadiness",
            name="source_consulted_at",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="regulatoryreadiness",
            name="evidence",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="regulatoryreadinesshistory",
            name="source_authority",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="regulatoryreadinesshistory",
            name="source_consulted_at",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="regulatoryreadinesshistory",
            name="evidence",
            field=models.TextField(blank=True),
        ),
    ]
