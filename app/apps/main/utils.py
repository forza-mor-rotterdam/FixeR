import base64

from django.core.files.storage import default_storage
from utils.constanten import PDOK_WIJKEN


def truncate_tekst(text, length=200):
    if len(text) > length:
        return f"{text[:length]}..."
    return text


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

        taakgebeurtenis = (
            mg.get("taakgebeurtenis", {}) if mg.get("taakgebeurtenis", {}) else {}
        )
        taakstatus_is_voltooid = (
            taakgebeurtenis
            and taakgebeurtenis.get("taakstatus")
            and taakgebeurtenis.get("taakstatus", {}).get("naam")
            in {"voltooid", "voltooid_met_feedback"}
        ) or taakgebeurtenis.get("verwijderd_op")
        taakstatus_event = (
            taakgebeurtenis
            and taakgebeurtenis.get("taakstatus")
            and taakgebeurtenis.get("taakstatus", {}).get("naam")
            in [
                "toegewezen",
                "openstaand",
            ]
            or taakgebeurtenis
            and taakgebeurtenis.get("gebeurtenis_type") == "gedeeld"
        )
        t_id = taakgebeurtenis.get("taakopdracht")
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
        if taakstatus_event:
            index = t_ids.index(t_id)
            row[index] = 3
        for i, t in enumerate(t_ids):
            row[i] = -1 if t == -1 else row[i]

        row.insert(0, 0 if taakgebeurtenis else 1)

        if taakstatus_is_voltooid:
            index = t_ids.index(t_id)
            if index + 1 >= len(t_ids):
                del t_ids[-1]
            else:
                t_ids[index] = -1

        row_dict = {
            "mg": mg,
            "row": row,
        }
        tijdlijn_data.append(row_dict)

    row_dict = {
        "row": [t if t not in [1, 2, 3] else 0 for t in row],
    }
    tijdlijn_data.append(row_dict)
    tijdlijn_data = [t for t in reversed(tijdlijn_data)]
    return tijdlijn_data


def get_wijknaam_by_wijkcode(wijkcode):
    for wijk in PDOK_WIJKEN:
        if wijk["wijkcode"] == wijkcode:
            return wijk["wijknaam"]
    return None
