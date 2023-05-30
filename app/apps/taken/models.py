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

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taaktype"
        verbose_name_plural = "Taaktypes"

    def __str__(self) -> str:
        return f"{self.omschrijving}({self.pk})"


class Taakstatus(BasisModel):
    class NaamOpties(models.TextChoices):
        NIEUW = "nieuw", "Nieuw"
        BEZIG = "bezig", "Bezig"
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

    # def save(self, *args, **kwargs):
    #     self.full_clean()
    #     return super().save(*args, **kwargs)

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
    melding = models.ForeignKey(
        to="aliassen.MeldingAlias",
        related_name="taken_voor_meldingalias",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
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

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taak"
        verbose_name_plural = "Taken"
