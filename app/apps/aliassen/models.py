import logging

from apps.meldingen.service import MeldingenService
from django.contrib.gis.db import models
from utils.models import BasisModel

logger = logging.getLogger(__name__)


class MeldingAlias(BasisModel):
    bron_url = models.CharField(max_length=500)
    response_json = models.JSONField(
        default=dict,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Melding alias"
        verbose_name_plural = "Melding aliassen"

    class MeldingNietValide(Exception):
        pass

    def valideer_bron_url(self):
        response = MeldingenService().get_by_uri(self.bron_url)
        if response.status_code != 200:
            self.response_json = {}
            logger.error(
                f"Melding ophalen fout: status code: {response.status_code}, melding_alias id: {self.id}"
            )
            return
        self.response_json = response.json()

    def __str__(self) -> str:
        try:
            return self.response_json.get("name", self.bron_url)
        except Exception:
            return self.bron_url


class BijlageAlias(BasisModel):
    bron_url = models.CharField(max_length=500)
    response_json = models.JSONField(
        default=dict,
        blank=True,
        null=True,
    )
    taak_gebeurtenis = models.ForeignKey(
        to="taken.Taakgebeurtenis",
        related_name="bijlagen_voor_taak_gebeurtenis",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Bijlage alias"
        verbose_name_plural = "Bijlage aliassen"

    class BijlageNietValide(Exception):
        pass

    def valideer_bron_url(self):
        response = MeldingenService().get_by_uri(self.bron_url)
        if response.status_code != 200:
            raise BijlageAlias.BijlageNietValide(
                f"Response status_code: {response.status_code}"
            )
        self.response_json = response.json()

    def __str__(self) -> str:
        return self.bron_url
