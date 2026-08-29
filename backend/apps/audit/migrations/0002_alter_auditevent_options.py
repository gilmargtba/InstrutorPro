from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("audit", "0001_initial")]

    operations = [
        migrations.AlterModelOptions(
            name="auditevent",
            options={
                "ordering": ["-occurred_at"],
                "permissions": [("view_security_audit", "Can view security audit events")],
            },
        )
    ]

