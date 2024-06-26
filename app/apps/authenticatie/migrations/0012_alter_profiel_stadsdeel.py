# Generated by Django 4.2.11 on 2024-06-19 16:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authenticatie", "0011_profiel_afdelingen"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profiel",
            name="stadsdeel",
            field=models.CharField(
                blank=True,
                choices=[
                    ("volledig", "Heel Rotterdam"),
                    ("noord", "Noord"),
                    ("zuid", "Zuid"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]