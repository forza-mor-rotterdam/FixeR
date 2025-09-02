import json
import logging

from apps.main.services import MORCoreService
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from utils.constanten import BEGRAAFPLAATS_MIDDELS_ID
from utils.models import BasisModel

logger = logging.getLogger(__name__)


LOCATIE_TYPE_CHOICES = (
    ("adres", "adres"),
    ("lichtmast", "lichtmast"),
    ("graf", "graf"),
)


class MeldingAlias(BasisModel):
    bron_url = models.CharField(max_length=500, unique=True)
    response_json = models.JSONField(
        default=dict,
        blank=True,
        null=True,
    )
    locatie_type = models.CharField(max_length=50, null=True, blank=True)
    plaatsnaam = models.CharField(max_length=255, null=True, blank=True)
    straatnaam = models.CharField(max_length=255, null=True, blank=True)
    huisnummer = models.IntegerField(null=True, blank=True)
    huisletter = models.CharField(max_length=1, null=True, blank=True)
    toevoeging = models.CharField(max_length=4, null=True, blank=True)
    postcode = models.CharField(max_length=7, null=True, blank=True)
    wijknaam = models.CharField(max_length=255, null=True, blank=True)
    buurtnaam = models.CharField(max_length=255, null=True, blank=True)
    begraafplaats = models.CharField(max_length=50, null=True, blank=True)
    grafnummer = models.CharField(max_length=10, null=True, blank=True)
    vak = models.CharField(max_length=10, null=True, blank=True)
    lichtmast_id = models.CharField(max_length=255, null=True, blank=True)
    geometrie = models.GeometryField(null=True, blank=True)
    bron_signaal_ids = ArrayField(
        models.CharField(max_length=500, blank=True), blank=True, null=True
    )
    zoek_tekst = models.TextField(
        default="",
        blank=True,
        null=True,
    )
    locatie_verbose = models.CharField(
        max_length=200,
        default="",
        blank=True,
        null=True,
    )
    thumbnail_afbeelding_relative_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    melding_uuid = models.UUIDField(null=True, blank=True)

    class Meta:
        verbose_name = "Melding alias"
        verbose_name_plural = "Melding aliassen"

        indexes = [
            models.Index(fields=["straatnaam"]),
            models.Index(fields=["huisnummer"]),
            models.Index(fields=["huisletter"]),
            models.Index(fields=["toevoeging"]),
            models.Index(fields=["postcode"]),
            models.Index(fields=["geometrie"]),  # Might have to be a GistIndex
            models.Index(fields=["wijknaam"]),
            models.Index(fields=["buurtnaam"]),
            models.Index(fields=["begraafplaats"]),
            GinIndex(fields=["bron_signaal_ids"]),
        ]

    class MeldingNietValide(Exception):
        pass

    def valideer_bron_url(self):
        try:
            response = MORCoreService().haal_data(self.bron_url, raw_response=True)
        except MORCoreService.BasisUrlFout as e:
            print(e)
            return
        if response.status_code not in [200, 404]:
            error = f"Melding ophalen fout: status code: {response.status_code}, melding_alias id: {self.id}"
            logger.error(error)
            raise Exception(error)
        self.response_json = response.json()

    def get_locatie_verbose(self):
        locatie_verbose = "Geen locatie gegevens"
        huisletter = self.huisletter or ""
        huisnummer = self.huisnummer or ""
        straatnaam = self.straatnaam or ""
        toevoeging = self.toevoeging
        toevoeging = f"-{toevoeging}" if toevoeging else ""
        begraafplaats = BEGRAAFPLAATS_MIDDELS_ID.get(self.begraafplaats)
        begraafplaats = begraafplaats or ""
        grafnummer = self.grafnummer or ""
        grafnummer_verbose = f"Graf {grafnummer}" or ""
        vak = self.vak or ""
        vak_verbose = f"Vak {vak}" or ""
        if self.locatie_type == "adres":
            locatie_verbose = (
                f"{straatnaam} {huisnummer}{huisletter}{toevoeging}".strip()
            )
        elif self.locatie_type == "graf":
            locatie_verbose = ", ".join(
                [
                    item
                    for item in [begraafplaats, vak_verbose, grafnummer_verbose]
                    if item
                ]
            )
        return locatie_verbose

    def set_locatie_verbose(self):
        self.locatie_verbose = self.get_locatie_verbose()

    def get_zoek_tekst(self):
        locatie_zoek_tekst = []
        huisletter = self.huisletter or ""
        huisnummer = self.huisnummer or ""
        straatnaam = self.straatnaam or ""
        toevoeging = self.toevoeging
        toevoeging = f"-{toevoeging}" if toevoeging else ""
        begraafplaats = BEGRAAFPLAATS_MIDDELS_ID.get(self.begraafplaats)
        begraafplaats = begraafplaats or ""
        grafnummer = self.grafnummer or ""
        vak = self.vak or ""
        if self.locatie_type == "adres":
            locatie_zoek_tekst.append(
                f"{straatnaam} {huisnummer}{huisletter}{toevoeging}".strip()
            )
        elif self.locatie_type == "graf":
            locatie_zoek_tekst.append(f"{vak} {grafnummer}".strip())
        return ",".join(self.bron_signaal_ids + locatie_zoek_tekst)

    def set_zoek_tekst(self):
        self.zoek_tekst = self.get_zoek_tekst()

    def coordinates(self):
        melding_serialized = MeldingAliasSerializer(self)
        return (
            list(
                reversed(
                    melding_serialized.data.get("geometrie", {}).get("coordinates", [])
                )
            )
            if melding_serialized.data.get("geometrie")
            else None
        )

    def update_zoek_data(self):
        melding = self.response_json
        referentie_locatie = melding.get("referentie_locatie") or {}
        thumbnail_afbeelding = melding.get("thumbnail_afbeelding") or {}
        signalen = melding.get("signalen_voor_melding") or []
        bron_signaal_ids = [
            signaal.get("bron_signaal_id")
            for signaal in signalen
            if signaal.get("bron_signaal_id")
        ]
        self.thumbnail_afbeelding_relative_url = thumbnail_afbeelding.get(
            "afbeelding_verkleind_relative_url"
        )
        self.bron_signaal_ids = bron_signaal_ids
        self.locatie_type = referentie_locatie.get("locatie_type")
        self.geometrie = (
            GEOSGeometry(json.dumps(referentie_locatie.get("geometrie")))
            if referentie_locatie.get("geometrie")
            else None
        )
        self.plaatsnaam = referentie_locatie.get("plaatsnaam")
        self.postcode = referentie_locatie.get("postcode")
        self.wijknaam = referentie_locatie.get("wijknaam")
        self.buurtnaam = referentie_locatie.get("buurtnaam")
        self.straatnaam = referentie_locatie.get("straatnaam")
        self.huisnummer = referentie_locatie.get("huisnummer")
        self.huisletter = referentie_locatie.get("huisletter")
        self.toevoeging = referentie_locatie.get("toevoeging")
        self.begraafplaats = referentie_locatie.get("begraafplaats")
        self.grafnummer = referentie_locatie.get("grafnummer")
        self.vak = referentie_locatie.get("vak")
        self.lichtmast_id = referentie_locatie.get("lichtmast_id")

        self.set_zoek_tekst()
        self.set_locatie_verbose()
        self.melding_uuid = melding.get("uuid")

    def __str__(self) -> str:
        return self.bron_url


class MeldingAliasSerializer(serializers.ModelSerializer):
    geometrie = GeometryField()

    class Meta:
        model = MeldingAlias
        fields = ["geometrie"]


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
        response = MORCoreService().haal_data(self.bron_url, raw_response=True)
        if response.status_code != 200:
            raise BijlageAlias.BijlageNietValide(
                f"Response status_code: {response.status_code}"
            )
        self.response_json = response.json()

    def __str__(self) -> str:
        return self.bron_url
