# Generated by Django 4.2.15 on 2024-12-02 14:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0021_alter_taaktype_toelichting"),
    ]

    operations = [
        migrations.AlterField(
            model_name="taak",
            name="titel",
            field=models.CharField(max_length=200),
        ),
    ]
