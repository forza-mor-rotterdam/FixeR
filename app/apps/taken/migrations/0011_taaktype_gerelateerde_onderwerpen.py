# Generated by Django 3.2.16 on 2024-04-03 14:25

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0010_auto_20240314_1003"),
    ]

    operations = [
        migrations.AddField(
            model_name="taaktype",
            name="gerelateerde_onderwerpen",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.URLField(), default=[], size=None
            ),
        ),
    ]
