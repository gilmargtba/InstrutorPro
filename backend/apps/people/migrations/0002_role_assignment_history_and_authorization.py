import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="roleassignment",
            options={
                "permissions": [
                    ("manage_role_assignments", "Can grant and revoke personal roles")
                ]
            },
        ),
        migrations.AddField(
            model_name="roleassignment",
            name="grant_reason",
            field=models.CharField(default="LEGACY_ASSIGNMENT", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="roleassignment",
            name="granted_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="granted_role_assignments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="roleassignment",
            name="revoke_reason",
            field=models.CharField(blank=True, default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="roleassignment",
            name="revoked_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="revoked_role_assignments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RemoveConstraint(
            model_name="roleassignment",
            name="uq_person_role",
        ),
        migrations.AddConstraint(
            model_name="roleassignment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("revoked_at__isnull", True)),
                fields=("person", "role"),
                name="uq_active_person_role",
            ),
        ),
    ]
