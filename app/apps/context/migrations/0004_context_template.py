# Generated by Django 3.2.16 on 2023-08-30 12:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("context", "0003_context_filters"),
    ]

    operations = [
        migrations.AddField(
            model_name="context",
            name="template",
            field=models.CharField(
                choices=[("standaard", "Standaard"), ("benc", "Begraven & Cremeren")],
                default="standaard",
                max_length=50,
            ),
        ),
    ]
