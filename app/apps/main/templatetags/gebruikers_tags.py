from django import template
from django.contrib.auth import get_user_model

register = template.Library()


@register.filter
def gebruiker_middels_email(value):
    if not value:
        return ""
    UserModel = get_user_model()
    gebruiker = UserModel.objects.filter(email=value).first()
    if gebruiker:
        return gebruiker
    return value
