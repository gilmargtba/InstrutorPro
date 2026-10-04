from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("discovery", "0009_verification_requirements_snapshot")]

    operations = [
        migrations.AddField(
            model_name="professionalverificationrequest",
            name="previous_verified_request",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="supplements",
                to="discovery.professionalverificationrequest",
            ),
        ),
    ]
