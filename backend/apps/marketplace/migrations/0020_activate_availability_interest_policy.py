from django.db import migrations


CONSENT_VERSION = "availability-interest-2026-11-13"


def activate_approved_interest_policy(apps, schema_editor):
    Policy = apps.get_model("marketplace", "AvailabilityInterestPolicy")
    Policy.objects.filter(
        pk=1,
        consent_version=CONSENT_VERSION,
        retention_days=90,
        privacy_notice__version="2026-11-13",
        enabled=False,
    ).update(enabled=True)


def pause_interest_policy(apps, schema_editor):
    Policy = apps.get_model("marketplace", "AvailabilityInterestPolicy")
    Policy.objects.filter(pk=1, consent_version=CONSENT_VERSION).update(enabled=False)


class Migration(migrations.Migration):
    dependencies = [("marketplace", "0019_seed_availability_interest_policy")]

    operations = [migrations.RunPython(activate_approved_interest_policy, pause_interest_policy)]
