from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("marketplace", "0017_availability_interest")]

    operations = [
        migrations.AddField(
            model_name="availabilityinterest",
            name="scope",
            field=models.CharField(
                choices=[("UF", "UF"), ("CITY", "Cidade"), ("REGION", "Região")],
                default="CITY",
                max_length=8,
            ),
        ),
        migrations.AddField(
            model_name="availabilityinterest",
            name="region",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AlterField(
            model_name="availabilityinterest",
            name="city",
            field=models.CharField(blank=True, max_length=120),
        ),
    ]
