from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("discovery", "0008_alter_demoinstructorservicelocation_options_and_more")]

    operations = [
        migrations.AddField(
            model_name="professionalverificationrequest",
            name="requirements_snapshot",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
