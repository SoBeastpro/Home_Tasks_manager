from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0003_populate_category_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(
                editable=False,
                max_length=180,
                unique=True,
                verbose_name="URL-идентификатор",
            ),
        ),
    ]
