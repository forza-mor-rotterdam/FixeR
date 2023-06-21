import base64

from django.core.files.storage import default_storage
from django.db.models import Count
from django.http import QueryDict


def get_filter_options(f_qs, qs, fields=[]):
    out = {}

    def value_lookup(obj, key, f: list | tuple):
        if isinstance(obj, dict):
            return obj.get(key, key)
        if isinstance(obj, (str, int)):
            return obj
        return key

    for f in fields:
        f = f if isinstance(f, (list, tuple)) else (f,)
        key = f[1] if len(f) > 1 else f[0]
        value_lookup_str = f[2] if len(f) > 2 else key
        f_dict = {
            ll[0]: (value_lookup(ll[1], ll[0], f), 0)
            for ll in qs.order_by(key).values_list(key, value_lookup_str).distinct(key)
        }
        ff_dict = {
            fl[0]: (value_lookup(fl[1], fl[0], f), fl[2])
            for fl in f_qs.order_by(key)
            .values_list(key, value_lookup_str)
            .annotate(count=Count(key))
        }
        f_dict.update(ff_dict)
        f_dict = {str(k): v for k, v in f_dict.items() if k}
        out[f[0]] = f_dict
    return out


def filter_taken(qs, actieve_filters):
    if actieve_filters.get("locatie"):
        qs = qs.filter(
            melding__response_json__locaties_voor_melding__0__begraafplaats__in=actieve_filters[
                "locatie"
            ]
        )
    if actieve_filters.get("taken"):
        qs = qs.filter(taaktype__id__in=actieve_filters["taken"])
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
