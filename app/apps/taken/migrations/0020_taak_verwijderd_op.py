# Generated by Django 4.2.15 on 2024-09-05 13:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0019_merge_20240819_1735"),
    ]

    operations = [
        migrations.AddField(
            model_name="taak",
            name="verwijderd_op",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
