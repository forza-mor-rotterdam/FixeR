import logging
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from requests import Request, Response

logger = logging.getLogger(__name__)


class MeldingenService:
    _api_base_url = None
    _timeout: tuple[int, ...] = (5, 10)
    _api_path: str = "/api/v1"

    class BasisUrlFout(Exception):
        ...

    class DataOphalenFout(Exception):
        ...

    def __init__(self, *args, **kwargs: dict):
        self._api_base_url = settings.MELDINGEN_URL
        super().__init__(*args, **kwargs)

    def get_url(self, url):
        url_o = urlparse(url)
        if not url_o.scheme and not url_o.netloc:
            return f"{self._api_base_url}{url}"
        if f"{url_o.scheme}://{url_o.netloc}" == self._api_base_url:
            return url
        raise MeldingenService.BasisUrlFout(
            f"url: {url}, basis_url: {self._api_base_url}"
        )

    def haal_token(self):
        meldingen_token = cache.get("meldingen_token")
        logger.info(f"meldingen_token exists: {bool(meldingen_token)}")
        if not meldingen_token:
            logger.info(
                f"MELDINGEN_PASSWORD EXISTS: {(settings.MELDINGEN_PASSWORD is not None)}"
            )
            email = settings.MELDINGEN_USERNAME
            try:
                validate_email(email)
            except ValidationError:
                email = f"{settings.MELDINGEN_USERNAME}@forzamor.nl"
            token_response = requests.post(
                settings.MELDINGEN_TOKEN_API,
                json={
                    "username": email,
                    "password": settings.MELDINGEN_PASSWORD,
                },
            )
            logger.info(settings.MELDINGEN_TOKEN_API)
            logger.info(settings.MELDINGEN_USERNAME)
            if token_response.status_code == 200:
                meldingen_token = token_response.json().get("token")
                cache.set(
                    "meldingen_token", meldingen_token, settings.MELDINGEN_TOKEN_TIMEOUT
                )
            else:
                raise MeldingenService.DataOphalenFout(
                    f"status code: {token_response.status_code}, response text: {token_response.text}"
                )

        return meldingen_token

    def get_headers(self):
        headers = {"Authorization": f"Token {self.haal_token()}"}
        return headers

    def do_request(self, url, method="get", data={}, raw_response=True):
        action: Request = getattr(requests, method)
        action_params: dict = {
            "url": self.get_url(url),
            "headers": self.get_headers(),
            "json": data,
            "timeout": self._timeout,
        }
        response: Response = action(**action_params)
        if raw_response:
            return response
        return response.json()

    def get_melding_lijst(self, query_string=""):
        return self.do_request(
            f"{self._api_path}/melding/?{query_string}", raw_response=False
        )

    def get_melding(self, id, query_string=""):
        return self.do_request(
            f"{self._api_path}/melding/{id}/?{query_string}", raw_response=False
        )

    def get_by_uri(self, uri):
        return self.do_request(uri)

    def taak_aanmaken(
        self,
        melding_uuid,
        taaktype_url,
        titel,
        bericht=None,
        gebruiker=None,
        additionele_informatie={},
    ):
        data = {
            "taaktype": taaktype_url,
            "titel": titel,
            "bericht": bericht,
            "gebruiker": gebruiker,
            "additionele_informatie": additionele_informatie,
        }
        return self.do_request(
            f"{self._api_path}/melding/{melding_uuid}/taakopdracht/",
            method="post",
            data=data,
        )

    def taak_status_aanpassen(
        self,
        taakopdracht_url,
        status,
        resolutie=None,
        omschrijving_intern=None,
        bijlagen=[],
        gebruiker=None,
        uitvoerder=None,
    ):
        data = {
            "taakstatus": {
                "naam": status,
            },
            "resolutie": resolutie,
            "omschrijving_intern": omschrijving_intern,
            "bijlagen": bijlagen,
            "gebruiker": gebruiker,
        }
        if uitvoerder:
            data.update({"uitvoerder": uitvoerder})
        return self.do_request(
            f"{taakopdracht_url}status-aanpassen/", method="patch", data=data
        )
