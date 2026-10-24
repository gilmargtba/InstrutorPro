from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models
from django.db.models import Q


def copy_legacy_categories(apps, schema_editor):
    Package = apps.get_model("marketplace", "InstructorLessonPackage")
    for package in (
        Package.objects.using(schema_editor.connection.alias).only("id", "category").iterator()
    ):
        Package.objects.using(schema_editor.connection.alias).filter(pk=package.pk).update(
            categories=[package.category]
        )


class Migration(migrations.Migration):
    dependencies = [("marketplace", "0015_instructor_lesson_package")]

    operations = [
        migrations.AddField(
            model_name="instructorlessonpackage",
            name="categories",
            field=ArrayField(
                base_field=models.CharField(
                    choices=[(value, value) for value in "ABCDE"], max_length=1
                ),
                default=list,
                size=5,
            ),
        ),
        migrations.RunPython(copy_legacy_categories, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="instructorlessonpackage",
            constraint=models.CheckConstraint(
                condition=~Q(categories=[]), name="ck_package_categories_not_empty"
            ),
        ),
    ]
