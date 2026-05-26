from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0034_taakgebeurtenis_reden_afwijzing"),
    ]

    operations = [
        migrations.AlterField(
            model_name="taaktype",
            name="toelichting",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
