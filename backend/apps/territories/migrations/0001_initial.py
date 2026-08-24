import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Country", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("code", models.CharField(max_length=2, unique=True)), ("name", models.CharField(max_length=100))]),
        migrations.CreateModel(name="FederativeUnit", fields=[("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("code", models.CharField(max_length=2, unique=True)), ("name", models.CharField(max_length=100)), ("ibge_code", models.CharField(max_length=2, unique=True)), ("operational_status", models.CharField(choices=[("FIRST_WAVE", "Primeira onda"), ("NATIONAL_READY", "Preparada nacionalmente")], max_length=20)), ("commercially_active", models.BooleanField(default=False)), ("country", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="federative_units", to="territories.country"))], options={"ordering": ["code"]}),
    ]

