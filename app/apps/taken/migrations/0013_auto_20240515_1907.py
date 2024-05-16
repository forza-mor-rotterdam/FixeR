# Generated by Django 3.2.18 on 2024-05-15 17:07

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0012_auto_20240415_1636"),
    ]

    operations = [
        migrations.AddField(
            model_name="taaktype",
            name="gerelateerde_taaktypes",
            field=models.ManyToManyField(
                blank=True,
                related_name="gerelateerde_taaktypes_voor_taaktype",
                to="taken.Taaktype",
            ),
        ),
        migrations.AlterField(
            model_name="taaktype",
            name="gerelateerde_onderwerpen",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.URLField(), default=list, size=None
            ),
        ),
    ]