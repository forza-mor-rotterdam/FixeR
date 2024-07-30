# Generated by Django 4.2.11 on 2024-07-30 13:46

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0016_taak_taken_taak_taaksta_0e016e_idx_and_more"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="taak",
            name="taken_taak_geometr_cedb20_idx",
        ),
        migrations.RemoveIndex(
            model_name="taak",
            name="taken_taak_taakopd_47887e_idx",
        ),
        migrations.AddIndex(
            model_name="taak",
            index=models.Index(
                fields=["bezig_met_verwerken"], name="taken_taak_bezig_m_6e55bb_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="taakzoekdata",
            index=models.Index(
                fields=["straatnaam"], name="taken_taakz_straatn_e37c83_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="taakzoekdata",
            index=models.Index(
                fields=["huisnummer"], name="taken_taakz_huisnum_64d563_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="taakzoekdata",
            index=models.Index(
                fields=["huisletter"], name="taken_taakz_huislet_8935f4_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="taakzoekdata",
            index=models.Index(
                fields=["toevoeging"], name="taken_taakz_toevoeg_a61c12_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="taakzoekdata",
            index=models.Index(
                fields=["postcode"], name="taken_taakz_postcod_69fe13_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="taakzoekdata",
            index=models.Index(
                fields=["geometrie"], name="taken_taakz_geometr_13eb3a_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="taakzoekdata",
            index=models.Index(
                fields=["wijknaam"], name="taken_taakz_wijknaa_3dbc69_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="taakzoekdata",
            index=models.Index(
                fields=["buurtnaam"], name="taken_taakz_buurtna_299add_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="taakzoekdata",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["bron_signaal_ids"], name="taken_taakz_bron_si_c2a07c_gin"
            ),
        ),
    ]