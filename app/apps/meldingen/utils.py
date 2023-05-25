import requests
from django.conf import settings
from django.core.cache import cache


class MeldingAuthResponseException(Exception):
    pass


def get_meldingen_token():
    meldingen_token = cache.get("meldingen_token2")
    if not meldingen_token:
        token_response = requests.post(
            settings.MELDINGEN_TOKEN_API,
            json={
                "username": settings.MELDINGEN_USERNAME,
                "password": settings.MELDINGEN_PASSWORD,
            },
        )
        if token_response.status_code == 200:
            meldingen_token = token_response.json().get("token")
            cache.set(
                "meldingen_token", meldingen_token, settings.MELDINGEN_TOKEN_TIMEOUT
            )
        else:
            raise MeldingAuthResponseException(
                f"auth response status code: {token_response.status_code}"
            )
    return meldingen_token
