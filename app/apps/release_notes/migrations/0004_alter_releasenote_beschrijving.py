# Generated by Django 3.2.16 on 2023-12-18 13:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("release_notes", "0003_auto_20231214_1803"),
    ]

    operations = [
        migrations.AlterField(
            model_name="releasenote",
            name="beschrijving",
            field=models.TextField(blank=True, max_length=1000),
        ),
    ]
