import base64

from apps.context.constanten import FILTER_NAMEN, FILTERS_LOOKUP
from django.core.files.storage import default_storage
from django.http import QueryDict


def get_filters(context):
    filters = context.filters.get("fields", [])
    filters = [f for f in filters if f in FILTER_NAMEN]
    return filters


def get_actieve_filters(gebruiker, filters, status="nieuw"):
    actieve_filters = {f: [] for f in filters}
    profiel_filters = (
        gebruiker.profiel.filters.get(status, {})
        if isinstance(gebruiker.profiel.filters.get("status", {}), dict)
        else {}
    )
    actieve_filters.update({k: v for k, v in profiel_filters.items() if k in filters})
    return actieve_filters


def get_sortering(gebruiker):
    return gebruiker.profiel.ui_instellingen.get("sortering", "Datum-reverse")


def set_sortering(gebruiker, nieuwe_sortering):
    gebruiker.profiel.ui_instellingen.update({"sortering": nieuwe_sortering})
    return gebruiker.profiel.save()


def get_kaart_modus(gebruiker):
    return gebruiker.profiel.ui_instellingen.get("kaart_modus", "volgen")


def set_kaart_modus(gebruiker, nieuwe_kaart_modus):
    gebruiker.profiel.ui_instellingen.update({"kaart_modus": nieuwe_kaart_modus})
    return gebruiker.profiel.save()


def get_actieve_filters_aantal(actieve_filters):
    return len([ll for k, v in actieve_filters.items() for ll in v])


def set_actieve_filters(gebruiker, actieve_filters, status="nieuw"):
    gebruiker.profiel.filters.update({status: actieve_filters})
    return gebruiker.profiel.save()


def get_filter_options(f_qs, qs, fields=[]):
    return {f.key(): f(qs, f_qs).get_options(qs, f_qs) for f in fields}


def filter_taken(qs, actieve_filters):
    qs = qs.filter(
        **{
            FILTERS_LOOKUP.get(k)().get_filter_lookup(): v
            for k, v in actieve_filters.items()
            if FILTERS_LOOKUP.get(k) and v
        }
    )
    return qs


def dict_to_querystring(d: dict) -> str:
    return "&".join([f"{p}={v}" for p, l in d.items() for v in l])


def querystring_to_dict(s: str) -> dict:
    return dict(QueryDict(s))


def to_base64(file):
    binary_file = default_storage.open(file)
    binary_file_data = binary_file.read()
    base64_encoded_data = base64.b64encode(binary_file_data)
    base64_message = base64_encoded_data.decode("utf-8")
    return base64_message


def melding_naar_tijdlijn(melding: dict):
    tijdlijn_data = []
    t_ids = []
    row = []
    for mg in reversed(melding.get("meldinggebeurtenissen", [])):
        row = [0 for t in t_ids]

        tg = mg.get("taakgebeurtenis", {}) if mg.get("taakgebeurtenis", {}) else {}
        taakstatus_is_voltooid = (
            tg and tg.get("taakstatus", {}).get("naam") == "voltooid"
        )
        t_id = tg.get("taakopdracht")
        if t_id and t_id not in t_ids:
            try:
                i = t_ids.index(-1)
                t_ids[i] = t_id
                row[i] = 1
            except Exception:
                t_ids.append(t_id)
                row.append(1)

        if taakstatus_is_voltooid:
            index = t_ids.index(t_id)
            row[index] = 2

        for index, t in enumerate(t_ids):
            row[index] = -1 if t == -1 else row[index]

        row.insert(0, 0 if tg else 1)

        if taakstatus_is_voltooid:
            index = t_ids.index(t_id)
            if index + 1 >= len(t_ids):
                del t_ids[-1]
            else:
                t_ids[index] = -1

        row_dict = {
            "mg": mg,
            "row": row,
            "afgesloten": False,
        }
        tijdlijn_data.append(row_dict)

    row_dict = {
        "row": [t if t not in [1, 2] else 0 for t in row],
    }
    tijdlijn_data.append(row_dict)
    tijdlijn_data = [t for t in reversed(tijdlijn_data)]
    return tijdlijn_data


def update_meldingen(meldingen_qs):
    for melding_alias in meldingen_qs:
        melding_alias.save()
