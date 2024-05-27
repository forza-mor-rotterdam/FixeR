# Generated by Django 3.2.16 on 2024-04-15 14:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taaktype", "0001_initial"),
        ("taken", "0011_taaktype_gerelateerde_onderwerpen"),
    ]

    operations = [
        migrations.AddField(
            model_name="taaktype",
            name="afdelingen",
            field=models.ManyToManyField(
                blank=True,
                related_name="taaktypes_voor_afdelingen",
                to="taaktype.Afdeling",
            ),
        ),
        migrations.AddField(
            model_name="taaktype",
            name="taaktypemiddelen",
            field=models.ManyToManyField(
                blank=True,
                related_name="taaktypes_voor_taaktypemiddelen",
                to="taaktype.TaaktypeMiddel",
            ),
        ),
    ]
