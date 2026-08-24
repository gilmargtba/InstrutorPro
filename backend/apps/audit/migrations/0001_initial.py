import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="AuditEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("action", models.CharField(max_length=100)),
                ("target_type", models.CharField(max_length=100)),
                ("target_id", models.UUIDField(blank=True, null=True)),
                ("request_id", models.UUIDField(blank=True, null=True)),
                ("reason_code", models.CharField(blank=True, max_length=100)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("occurred_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-occurred_at"]},
        ),
        migrations.AddIndex(model_name="auditevent", index=models.Index(fields=["target_type", "target_id"], name="audit_target_idx")),
    ]

