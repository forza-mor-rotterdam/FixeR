from apps.services.onderwerpen import render_onderwerp
from apps.taken.managers import TaakManager
from apps.taken.querysets import TaakQuerySet
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from utils.models import BasisModel


class Taakgebeurtenis(BasisModel):
    """
    Taakgebeurtenissen bouwen de history op van een taak
    """

    taakstatus = models.OneToOneField(
        to="taken.Taakstatus",
        related_name="taakgebeurtenis_voor_taakstatus",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    omschrijving_intern = models.CharField(max_length=5000, null=True, blank=True)
    gebruiker = models.CharField(max_length=200, null=True, blank=True)
    taak = models.ForeignKey(
        to="taken.Taak",
        related_name="taakgebeurtenissen_voor_taak",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taakgebeurtenis"
        verbose_name_plural = "Taakgebeurtenissen"


class Taaktype(BasisModel):
    omschrijving = models.CharField(max_length=200)
    toelichting = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )
    additionele_informatie = models.JSONField(default=dict)

    volgende_taaktypes = models.ManyToManyField(
        to="taken.Taaktype",
        related_name="vorige_taaktypes_voor_taaktype",
        blank=True,
    )
    actief = models.BooleanField(default=True)

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taaktype"
        verbose_name_plural = "Taaktypes"

    def __str__(self) -> str:
        return f"{self.omschrijving}"


class Taakstatus(BasisModel):
    class NaamOpties(models.TextChoices):
        NIEUW = "nieuw", "Nieuw"
        TOEGEWEZEN = "toegewezen", "Toegewezen"
        OPENSTAAND = "openstaand", "Openstaand"
        VOLTOOID = "voltooid", "Voltooid"

    naam = models.CharField(
        max_length=50,
        choices=NaamOpties.choices,
        default=NaamOpties.NIEUW,
    )
    taak = models.ForeignKey(
        to="taken.Taak",
        related_name="taakstatussen_voor_taak",
        on_delete=models.CASCADE,
    )

    def volgende_statussen(self):
        naam_opties = [no[0] for no in Taakstatus.NaamOpties.choices]
        if self.naam not in naam_opties:
            return naam_opties

        if self.naam not in naam_opties:
            return naam_opties

        match self.naam:
            case Taakstatus.NaamOpties.NIEUW:
                return [
                    Taakstatus.NaamOpties.TOEGEWEZEN,
                    Taakstatus.NaamOpties.VOLTOOID,
                ]
            case Taakstatus.NaamOpties.TOEGEWEZEN:
                return [
                    Taakstatus.NaamOpties.OPENSTAAND,
                    Taakstatus.NaamOpties.VOLTOOID,
                ]
            case Taakstatus.NaamOpties.OPENSTAAND:
                return [
                    Taakstatus.NaamOpties.TOEGEWEZEN,
                    Taakstatus.NaamOpties.VOLTOOID,
                ]
            case _:
                return []

    def clean(self):
        errors = {}
        huidige_status = self.taak.status.naam if self.taak.status else ""
        nieuwe_status = self.naam

        if nieuwe_status == huidige_status:
            error_msg = "Status verandering niet toegestaan: van `{from_state}` naar `{to_state}`.".format(
                from_state=huidige_status, to_state=nieuwe_status
            )
            errors["taakstatus"] = ValidationError(error_msg, code="invalid")

        if errors:
            raise ValidationError(errors)

    class TaakStatusVeranderingNietToegestaan(Exception):
        pass

    def __str__(self) -> str:
        return f"{self.naam}({self.pk})"

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taakstatus"
        verbose_name_plural = "Taakstatussen"


class Taak(BasisModel):
    class ResolutieOpties(models.TextChoices):
        OPGELOST = "opgelost", "Opgelost"
        NIET_OPGELOST = "niet_opgelost", "Niet opgelost"
        GEANNULEERD = "geannuleerd", "Geannuleerd"
        NIET_GEVONDEN = "niet_gevonden", "Niets aangetroffen"

    afgesloten_op = models.DateTimeField(null=True, blank=True)
    melding = models.ForeignKey(
        to="aliassen.MeldingAlias",
        related_name="taken_voor_meldingalias",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    taakopdracht = models.URLField()
    taaktype = models.ForeignKey(
        to="taken.Taaktype",
        related_name="taken_voor_taaktype",
        on_delete=models.CASCADE,
    )
    taakstatus = models.OneToOneField(
        to="taken.Taakstatus",
        related_name="taak_voor_taakstatus",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    resolutie = models.CharField(
        max_length=50,
        choices=ResolutieOpties.choices,
        blank=True,
        null=True,
    )
    titel = models.CharField(max_length=100)
    bericht = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )
    additionele_informatie = models.JSONField(default=dict)

    objects = TaakQuerySet.as_manager()
    acties = TaakManager()

    def __str__(self) -> str:
        return f"{self.taaktype.omschrijving} - {self.titel}({self.pk})"

    def render_onderwerpen(self):
        return ", ".join(
            [
                render_onderwerp(onderwerp_url)
                for onderwerp_url in self.melding.response_json.get("onderwerpen", [])
            ]
        )

    def geometrie(self):
        locaties = self.melding.response_json.get("locaties_voor_melding")
        if not locaties or not locaties[0].get("geometrie"):
            return ""
        return locaties[0].get("geometrie")

    def adres(self):
        locaties = self.melding.response_json.get("locaties_voor_melding")
        if not locaties or not locaties[0].get("straatnaam"):
            return ""
        if locaties[0].get("huisnummer"):
            return f"{locaties[0].get('straatnaam')} {locaties[0].get('huisnummer')}"
        return locaties[0].get("straatnaam")

    def postcode_digits(self):
        locaties = self.melding.response_json.get("locaties_voor_melding")
        if not locaties or not locaties[0].get("postcode"):
            return 0
        try:
            return int(locaties[0].get("postcode")[0:4])
        except Exception:
            return 0

    def afbeelding_url(self):
        if not self.melding.response_json.get("bijlagen", []):
            return ""
        return self.melding.response_json.get("bijlagen", [])[0].get(
            "afbeelding_verkleind_relative_url"
        )

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taak"
        verbose_name_plural = "Taken"
