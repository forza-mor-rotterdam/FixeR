# Generated by Django 3.2.16 on 2023-08-30 08:52

import utils.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("context", "0002_auto_20230829_1938"),
    ]

    operations = [
        migrations.AddField(
            model_name="context",
            name="filters",
            field=utils.fields.DictJSONField(default=dict),
        ),
    ]