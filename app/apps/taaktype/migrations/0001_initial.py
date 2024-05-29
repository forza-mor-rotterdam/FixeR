# Generated by Django 3.2.18 on 2024-05-29 07:40

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Afdeling",
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
                ("naam", models.CharField(max_length=100)),
                (
                    "onderdeel",
                    models.CharField(
                        choices=[
                            ("schoon", "Schoon"),
                            ("heel", "Heel"),
                            ("veilig", "Veilig"),
                        ],
                        max_length=50,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TaaktypeMiddel",
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
                ("naam", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TaaktypeVoorbeeldsituatie",
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
                    "toelichting",
                    models.CharField(blank=True, max_length=500, null=True),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("waarom_wel", "Waarom wel"),
                            ("waarom_niet", "Waarom niet"),
                        ],
                        max_length=50,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
