from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taken", "0033_taakgebeurtenis_groep"),
    ]

    operations = [
        migrations.AddField(
            model_name="taakgebeurtenis",
            name="reden_afwijzing",
            field=models.CharField(
                blank=True,
                choices=[
                    ("al_verholpen", "De taak is al verholpen"),
                    ("niet_gemeente", "De taak is niet voor de gemeente"),
                    ("niet_voor_mij", "De taak is niet voor mij"),
                    ("locatie_onduidelijk", "De locatie van de taak is onduidelijk"),
                    ("anders", "Anders, namelijk"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="taakgebeurtenis",
            name="reden_afwijzing_toelichting",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
