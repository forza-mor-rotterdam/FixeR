# Generated by Django 3.2.16 on 2023-08-29 17:39

import uuid

import django.db.models.deletion
import utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("context", "0002_auto_20230829_1938"),
        ("authenticatie", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Profiel",
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
                ("filters", utils.fields.DictJSONField(default=dict)),
                ("ui_instellingen", utils.fields.DictJSONField(default=dict)),
                (
                    "context",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="profielen_voor_context",
                        to="context.context",
                    ),
                ),
                (
                    "gebruiker",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profiel",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
