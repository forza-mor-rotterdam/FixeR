import logging

from apps.services.basis import BasisService
from django.conf import settings

logger = logging.getLogger(__name__)


class TaakRService(BasisService):
    _default_error_message = "Er ging iets mis met het ophalen van data van TaakR"

    def __init__(self, *args, **kwargs: dict):
        self._api_base_url = settings.TAAKR_URL
        super().__init__(*args, **kwargs)

    def get_afdelingen(self, use_cache=True) -> list:
        alle_afdelingen = []
        next_page = f"{self._api_base_url}/api/v1/afdeling"
        while next_page:
            response = self.do_request(
                next_page,
                cache_timeout=0,  # Back to 60*60
                raw_response=False,
                force_cache=not use_cache,
            )
            current_afdelingen = response.get("results", [])
            alle_afdelingen.extend(current_afdelingen)
            next_page = response.get("next")

        return alle_afdelingen

    def get_afdeling(self, afdeling_uuid):
        url = f"{self._api_base_url}/api/v1/afdeling/{afdeling_uuid}"
        afdeling = self.do_request(
            url,
            cache_timeout=0,  # Back to 60*60
            raw_response=False,
        )

        return afdeling

    def get_afdeling_by_url(self, afdeling_url):
        afdeling = self.do_request(
            afdeling_url,
            cache_timeout=0,  # Back to 60*60
            raw_response=False,
        )

        return afdeling

    def get_taaktypes(self, use_cache=True) -> list:
        alle_taaktypes = []
        next_page = f"{self._api_base_url}/api/v1/taaktype"
        while next_page:
            response = self.do_request(
                next_page,
                cache_timeout=0,  # Back to 60*60
                force_cache=not use_cache,
                raw_response=False,
            )
            current_taaktypes = response.get("results", [])
            alle_taaktypes.extend(current_taaktypes)
            next_page = response.get("next")
        return alle_taaktypes

    def get_taaktype(self, taaktype_uuid):
        url = f"{self._api_base_url}/api/v1/taaktype/{taaktype_uuid}"
        taaktype = self.do_request(
            url,
            cache_timeout=0,  # Back to 60*60
            raw_response=False,
        )

        return taaktype

    def get_taaktype_by_url(self, taaktype_url):
        taaktype = self.do_request(
            taaktype_url,
            cache_timeout=0,  # Back to 60*60
            raw_response=False,
        )

        return taaktype

    def get_taakapplicatie_taaktype_url(self, taaktype_url):
        if taaktype := self.get_taaktype_by_url(taaktype_url):
            return taaktype.get("_links").get("taakapplicatie_taaktype_url")