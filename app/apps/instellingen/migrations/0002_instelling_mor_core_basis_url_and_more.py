# Generated by Django 4.2.11 on 2024-06-19 16:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("instellingen", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="instelling",
            name="mor_core_basis_url",
            field=models.URLField(default="http://core.mor.local:8002"),
        ),
        migrations.AddField(
            model_name="instelling",
            name="mor_core_token_timeout",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="instelling",
            name="taakr_basis_url",
            field=models.URLField(default="http://taakr.mor.local:8009"),
        ),
    ]
