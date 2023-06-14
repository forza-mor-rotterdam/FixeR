import json
from datetime import datetime

from django import template

register = template.Library()


@register.filter
def to_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
    except Exception as e:
        print(e)
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")
    except Exception as e:
        print(e)
    return value


@register.filter
def json_encode(value):
    return json.dumps(value)


@register.simple_tag
def vind_in_dict(op_zoek_dict, key):
    if type(op_zoek_dict) != dict:
        return key
    result = op_zoek_dict.get(key, op_zoek_dict.get(str(key), key))
    if isinstance(result, (list, tuple)):
        return result[0]
    return result
