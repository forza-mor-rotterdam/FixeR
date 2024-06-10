import logging

from django import template
from rest_framework.reverse import reverse

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def taaktype_url(context, taaktype):
    return reverse(
        "v1:taaktype-detail",
        kwargs={"uuid": taaktype.uuid},
        request=context.get("request"),
    )
