from django.db import migrations
from django.utils.text import slugify
from unidecode import unidecode


def populate_category_slugs(apps, schema_editor):
    Category = apps.get_model("categories", "Category")
    for category in Category.objects.all().order_by("pk"):
        base_slug = slugify(unidecode(category.name)) or "category"
        category.slug = f"{base_slug}-{category.pk}"
        category.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0002_category_slug"),
    ]

    operations = [
        migrations.RunPython(
            populate_category_slugs,
            migrations.RunPython.noop,
        ),
    ]
