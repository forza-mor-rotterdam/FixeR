from datetime import timedelta

from apps.aliassen.models import MeldingAlias
from apps.main.templatetags.gebruikers_tags import _get_gebruiker_object_middels_email
from apps.taken.managers import TaakManager
from apps.taken.querysets import TaakQuerySet
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.sites.models import Site
from django.core import signing
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django_celery_results.models import TaskResult
from rest_framework.reverse import reverse as drf_reverse
from utils.diversen import absolute
from utils.django_celery_results import restart_task
from utils.fields import ListJSONField
from utils.models import BasisModel


class Taakgebeurtenis(BasisModel):
    """
    Taakgebeurtenissen bouwen de history op van een taak
    """

    class ResolutieOpties(models.TextChoices):
        OPGELOST = "opgelost", "Opgelost"
        NIET_OPGELOST = "niet_opgelost", "Niet opgelost"
        GEANNULEERD = "geannuleerd", "Geannuleerd"
        NIET_GEVONDEN = "niet_gevonden", "Niets aangetroffen"

    taakstatus = models.OneToOneField(
        to="taken.Taakstatus",
        related_name="taakgebeurtenis_voor_taakstatus",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    omschrijving_intern = models.CharField(max_length=5000, null=True, blank=True)
    bijlage_paden = ArrayField(
        base_field=models.CharField(max_length=255),
        default=list,
        blank=True,
        null=True,
    )
    gebruiker = models.CharField(max_length=200, null=True, blank=True)
    taak = models.ForeignKey(
        to="taken.Taak",
        related_name="taakgebeurtenissen_voor_taak",
        on_delete=models.CASCADE,
    )
    resolutie = models.CharField(
        max_length=50,
        choices=ResolutieOpties.choices,
        blank=True,
        null=True,
    )
    notificatie_verstuurd = models.BooleanField(default=True)
    notificatie_error = models.CharField(max_length=5000, null=True, blank=True)
    vervolg_taaktypes = ListJSONField(default=list)

    task_taakopdracht_notificatie = models.OneToOneField(
        to="django_celery_results.TaskResult",
        related_name="taakgebeurtenis",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def get_task_taakopdracht_notificatie(self):
        from apps.taken.tasks import task_taakopdracht_notificatie_v2

        task_taakopdracht_notificatie_taskresult = (
            task_taakopdracht_notificatie_v2.delay(
                taakgebeurtenis_uuid=str(self.uuid),
            )
        )
        taskresults = TaskResult.objects.filter(
            task_id=task_taakopdracht_notificatie_taskresult.task_id
        )
        return taskresults[0] if taskresults else None

    def start_task_taakopdracht_notificatie(self):
        if not self.task_taakopdracht_notificatie:
            self.task_taakopdracht_notificatie = (
                self.get_task_taakopdracht_notificatie()
            )
            self.save(update_fields=["task_taakopdracht_notificatie"])
        else:
            aangemaakt, message = restart_task(self.task_taakopdracht_notificatie)
            if not aangemaakt:
                return (
                    f"Het is niet gelukt om de bestaande tasks te herstarten: {message}"
                )

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taakgebeurtenis"
        verbose_name_plural = "Taakgebeurtenissen"

        indexes = [
            models.Index(fields=["aangemaakt_op"]),
        ]


class Taaktype(BasisModel):
    omschrijving = models.CharField(max_length=200)
    toelichting = models.CharField(
        max_length=2000,
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

    def taaktype_url(self, request=None):
        if request:
            return drf_reverse(
                "v1:taaktype-detail",
                kwargs={"uuid": self.uuid},
                request=request,
            )
        domain = Site.objects.get_current().domain
        url_basis = f"{settings.PROTOCOL}://{domain}{settings.PORT}"
        pad = drf_reverse(
            "v1:taaktype-detail",
            kwargs={"uuid": self.uuid},
        )
        return f"{url_basis}{pad}"

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
        VOLTOOID_MET_FEEDBACK = "voltooid_met_feedback", "Voltooid met feedback"

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

    @classmethod
    def niet_voltooid_statussen(cls):
        return [
            choice[0]
            for choice in Taakstatus.NaamOpties.choices
            if choice[0]
            not in [
                Taakstatus.NaamOpties.VOLTOOID,
                Taakstatus.NaamOpties.VOLTOOID_MET_FEEDBACK,
            ]
        ]

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
            case Taakstatus.NaamOpties.VOLTOOID:
                return [
                    Taakstatus.NaamOpties.VOLTOOID_MET_FEEDBACK,
                ]
            case _:
                return []

    def clean(self):
        errors = {}
        huidige_status = self.taak.taakstatus.naam if self.taak.taakstatus else ""
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

        indexes = [
            models.Index(fields=["naam"]),
            models.Index(fields=["aangemaakt_op"]),
            models.Index(
                fields=["aangemaakt_op", "naam"], name="aangemaakt_op__naam_idx"
            ),
            models.Index(
                fields=["naam", "aangemaakt_op"], name="naam__aangemaakt_op_idx"
            ),
        ]


LOCATIE_TYPE_CHOICES = (
    ("adres", "adres"),
    ("lichtmast", "lichtmast"),
    ("graf", "graf"),
)


class TaakZoekData(BasisModel):
    locatie_type = models.CharField(
        max_length=50, choices=LOCATIE_TYPE_CHOICES, default=LOCATIE_TYPE_CHOICES[0][0]
    )
    # Locatie met hoogste gewicht
    plaatsnaam = models.CharField(max_length=255, null=True, blank=True)
    straatnaam = models.CharField(max_length=255, null=True, blank=True)
    huisnummer = models.IntegerField(null=True, blank=True)
    huisletter = models.CharField(max_length=1, null=True, blank=True)
    toevoeging = models.CharField(max_length=4, null=True, blank=True)
    postcode = models.CharField(max_length=7, null=True, blank=True)
    wijknaam = models.CharField(max_length=255, null=True, blank=True)
    buurtnaam = models.CharField(max_length=255, null=True, blank=True)
    # B&C Locatie info
    begraafplaats = models.CharField(max_length=50, null=True, blank=True)
    grafnummer = models.CharField(max_length=10, null=True, blank=True)
    vak = models.CharField(max_length=10, null=True, blank=True)
    # Lichtmast
    lichtmast_id = models.CharField(max_length=255, null=True, blank=True)
    # Geometrie
    geometrie = models.GeometryField(null=True, blank=True)
    # MeldR nummerers afkomstig uit signalen_voor_melding.bron_signaal_id
    bron_signaal_ids = ArrayField(
        models.CharField(max_length=500, blank=True), blank=True, null=True
    )

    melding_alias = models.ForeignKey(
        MeldingAlias,
        related_name="taak_zoek_data",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taak zoek data"
        verbose_name_plural = "Taak zoek data"
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


class Taak(BasisModel):
    class ResolutieOpties(models.TextChoices):
        OPGELOST = "opgelost", "Opgelost"
        NIET_OPGELOST = "niet_opgelost", "Niet opgelost"
        GEANNULEERD = "geannuleerd", "Geannuleerd"
        NIET_GEVONDEN = "niet_gevonden", "Niets aangetroffen"

    afgesloten_op = models.DateTimeField(null=True, blank=True)
    verwijderd_op = models.DateTimeField(null=True, blank=True)
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
    titel = models.CharField(max_length=200)
    bericht = models.CharField(
        max_length=5000,
        blank=True,
        null=True,
    )
    additionele_informatie = models.JSONField(default=dict)
    geometrie = models.GeometryField(null=True, blank=True)

    taak_zoek_data = models.ForeignKey(
        TaakZoekData,
        related_name="taak",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    objects = TaakQuerySet.as_manager()
    acties = TaakManager()

    cached_laatste_taakgebeurtenis = None
    cached_eerste_taakgebeurtenis = None
    cached_laatste_taakgebeurtenis_gebruiker = None
    cached_eerste_taakgebeurtenis_gebruiker = None

    def __str__(self) -> str:
        return f"{self.taaktype.omschrijving} - {self.titel}({self.pk})"

    @property
    def laatste_taakgebeurtenis(self):
        if not self.cached_laatste_taakgebeurtenis:
            self.cached_laatste_taakgebeurtenis = (
                self.taakgebeurtenissen_voor_taak.order_by("-aangemaakt_op").first()
            )
        if self.cached_laatste_taakgebeurtenis:
            return self.cached_laatste_taakgebeurtenis

    @property
    def eerste_taakgebeurtenis(self):
        if not self.cached_eerste_taakgebeurtenis:
            self.cached_eerste_taakgebeurtenis = (
                self.taakgebeurtenissen_voor_taak.order_by("aangemaakt_op").first()
            )
        if self.cached_eerste_taakgebeurtenis:
            return self.cached_eerste_taakgebeurtenis

    def laatste_taakgebeurtenis_omschrijving_intern(self):
        if self.laatste_taakgebeurtenis:
            return self.laatste_taakgebeurtenis.omschrijving_intern

    def laatste_taakgebeurtenis_gebruiker(self):
        if not self.laatste_taakgebeurtenis:
            return {}
        if not self.cached_laatste_taakgebeurtenis_gebruiker:
            self.cached_laatste_taakgebeurtenis_gebruiker = (
                _get_gebruiker_object_middels_email(
                    self.laatste_taakgebeurtenis.gebruiker
                )
            )
        return self.cached_laatste_taakgebeurtenis_gebruiker

    def eerste_taakgebeurtenis_gebruiker(self):
        if not self.eerste_taakgebeurtenis:
            return {}
        if not self.cached_eerste_taakgebeurtenis_gebruiker:
            self.cached_eerste_taakgebeurtenis_gebruiker = (
                _get_gebruiker_object_middels_email(
                    self.eerste_taakgebeurtenis.gebruiker
                )
            )
        return self.cached_eerste_taakgebeurtenis_gebruiker

    @classmethod
    def behandel_opties(cls):
        return (
            (
                Taak.ResolutieOpties.OPGELOST,
                "De taak is afgerond",
            ),
            (
                Taak.ResolutieOpties.NIET_GEVONDEN,
                "Niets aangetroffen",
            ),
            (
                Taak.ResolutieOpties.NIET_OPGELOST,
                "Kan niet worden uitgevoerd",
            ),
        )

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taak"
        verbose_name_plural = "Taken"
        indexes = [
            models.Index(fields=["aangemaakt_op"]),
            models.Index(fields=["verwijderd_op"]),
            models.Index(fields=["taakstatus"]),
            models.Index(fields=["taaktype"]),
            models.Index(fields=["melding"]),
        ]


class TaakDeellink(BasisModel):
    taak = models.ForeignKey(
        to="taken.Taak",
        related_name="taakdeellinks_voor_taak",
        on_delete=models.CASCADE,
    )
    gedeeld_door = models.CharField(max_length=200)
    signed_data = models.CharField(unique=True, max_length=500)
    bezoekers = ArrayField(
        base_field=models.EmailField(
            blank=True,
            null=True,
        ),
        default=list,
    )

    def get_signed_data(gebruiker_email):
        return signing.dumps(gebruiker_email, salt=settings.SECRET_KEY)

    def actief(self):
        try:
            signing.loads(
                self.signed_data,
                max_age=settings.SIGNED_DATA_MAX_AGE_SECONDS,
                salt=settings.SECRET_KEY,
            )
            return (
                (
                    self.aangemaakt_op
                    + timedelta(seconds=settings.SIGNED_DATA_MAX_AGE_SECONDS)
                )
                - timezone.now(),
                self.aangemaakt_op
                + timedelta(seconds=settings.SIGNED_DATA_MAX_AGE_SECONDS),
            )
        except signing.BadSignature:
            ...

    def get_absolute_url(self, request):
        url_basis = absolute(request).get("ABSOLUTE_ROOT")
        pad = reverse(
            "taak_detail_preview",
            kwargs={"uuid": self.taak.uuid, "signed_data": self.signed_data},
        )
        return f"{url_basis}{pad}"
