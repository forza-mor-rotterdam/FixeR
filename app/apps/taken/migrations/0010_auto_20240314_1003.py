# Generated by Django 3.2.16 on 2024-03-14 09:03

import uuid

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aliassen", "0002_bijlagealias_taak_gebeurtenis"),
        ("taken", "0009_taakdeellink"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaakZoekData",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("aangemaakt_op", models.DateTimeField(auto_now_add=True)),
                ("aangepast_op", models.DateTimeField(auto_now=True)),
                (
                    "locatie_type",
                    models.CharField(
                        choices=[
                            ("adres", "adres"),
                            ("lichtmast", "lichtmast"),
                            ("graf", "graf"),
                        ],
                        default="adres",
                        max_length=50,
                    ),
                ),
                ("plaatsnaam", models.CharField(blank=True, max_length=255, null=True)),
                ("straatnaam", models.CharField(blank=True, max_length=255, null=True)),
                ("huisnummer", models.IntegerField(blank=True, null=True)),
                ("huisletter", models.CharField(blank=True, max_length=1, null=True)),
                ("toevoeging", models.CharField(blank=True, max_length=4, null=True)),
                ("postcode", models.CharField(blank=True, max_length=7, null=True)),
                ("wijknaam", models.CharField(blank=True, max_length=255, null=True)),
                ("buurtnaam", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "begraafplaats",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("grafnummer", models.CharField(blank=True, max_length=10, null=True)),
                ("vak", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "lichtmast_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "geometrie",
                    django.contrib.gis.db.models.fields.GeometryField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                (
                    "bron_signaal_ids",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(blank=True, max_length=500),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "melding_alias",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="taak_zoek_data",
                        to="aliassen.meldingalias",
                    ),
                ),
            ],
            options={
                "verbose_name": "Taak zoek data",
                "verbose_name_plural": "Taak zoek data",
                "ordering": ("-aangemaakt_op",),
            },
        ),
        migrations.AddField(
            model_name="taak",
            name="taak_zoek_data",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="taak",
                to="taken.taakzoekdata",
            ),
        ),
    ]
