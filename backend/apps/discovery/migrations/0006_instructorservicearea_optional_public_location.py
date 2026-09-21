import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("discovery", "0005_professionalverification_provenance")]

    operations = [
        migrations.AlterField(
            model_name="instructorservicearea",
            name="public_service_location",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, geography=True, null=True, srid=4326
            ),
        )
    ]
