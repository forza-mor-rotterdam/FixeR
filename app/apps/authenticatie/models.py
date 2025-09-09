from apps.authenticatie.managers import GebruikerManager
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.forms.models import model_to_dict
from django.utils.html import mark_safe
from utils.fields import DictJSONField
from utils.images import get_upload_path
from utils.models import BasisModel

DATUM_SORTING_KEY = "Datum"
DATUM_REVERSE_SORTING_KEY = "Datum-reverse"
AFSTAND_SORTING_KEY = "Afstand"
ADRES_SORTING_KEY = "Adres"
ADRES_REVERSE_SORTING_KEY = "Adres-reverse"
POSTCODE_SORTING_KEY = "Postcode"
POSTCODE_REVERSE_SORTING_KEY = "Postcode-reverse"


class Gebruiker(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    telefoonnummer = models.CharField(max_length=17, blank=True, null=True)
    verwijderd_op = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = GebruikerManager()

    cached_rechtengroep = None
    cached_rol = None
    cached_serialized_instance = None
    cached_context = None

    def __str__(self):
        if self.first_name:
            return f"{self.first_name}{' ' if self.last_name else ''}{self.last_name}"
        return self.email

    @property
    def context(self):
        if not self.cached_context:
            self.cached_context = self.profiel.context
        return self.cached_context

    @property
    def rechtengroep(self):
        if not self.cached_rechtengroep:
            self.cache_rechtengroep = mark_safe(
                f"{self.groups.all().first().name if self.groups.all() else ''}"
            )
        return self.cached_rechtengroep

    @property
    def rol(self):
        if not self.cached_rol:
            self.cached_rol = mark_safe(f"{self.context.naam if self.context else ''}")
        return self.cached_rol

    def serialized_instance(self):
        if not self.is_authenticated:
            return None
        if not self.cached_serialized_instance:
            dict_instance = model_to_dict(
                self, fields=["email", "first_name", "last_name", "telefoonnummer"]
            )
            dict_instance.update(
                {
                    "naam": self.__str__(),
                    "rol": (
                        self.profiel.context.naam
                        if hasattr(self, "profiel")
                        and hasattr(self.profiel, "context")
                        and hasattr(self.profiel.context, "naam")
                        else None
                    ),
                    "rechten": (
                        self.groups.all().first().name if self.groups.all() else None
                    ),
                }
            )
            self.cached_serialized_instance = dict_instance
        return self.cached_serialized_instance


User = get_user_model()


class Profiel(BasisModel):
    """
    Profiel model voor Gebruikers
    """

    gebruiker = models.OneToOneField(
        to=User,
        related_name="profiel",
        on_delete=models.CASCADE,
    )

    filters = DictJSONField(default=dict)
    ui_instellingen = DictJSONField(default=dict)
    context = models.ForeignKey(
        to="context.Context",
        related_name="profielen_voor_context",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    profielfoto = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )

    onboarding_compleet = models.BooleanField(default=False)

    class StadsdeelOpties(models.TextChoices):
        VOLLEDIG = "volledig", "Heel Rotterdam"
        NOORD = "noord", "Noord"
        ZUID = "zuid", "Zuid"

    stadsdeel = models.CharField(
        max_length=50,
        choices=StadsdeelOpties.choices,
        null=True,
        blank=True,
    )

    afdelingen = ArrayField(
        models.CharField(max_length=500, blank=True), blank=True, null=True
    )

    wijken = ArrayField(
        models.CharField(max_length=500, blank=True), blank=True, null=True
    )
    taaktypes = models.ManyToManyField(
        to="taken.Taaktype",
        related_name="profielen_voor_taaktypes",
        blank=True,
    )

    def __str__(self):
        if self.gebruiker:
            return f"Profiel voor: {self.gebruiker}"
        return f"Profiel id: {self.pk}"

    def get_taaktypes(self):
        taaktypes = self.taaktypes if not self.is_benc else self.context.taaktypes
        return taaktypes.values("id", "omschrijving")

    @property
    def taken_filters(self):
        from apps.taken.filters import FILTERS

        return [
            f(profiel=self)
            for f in FILTERS
            if f.key() in self.context.filters.get("fields", [])
        ]

    @property
    def taken_filter_data(self):
        status = "nieuw"
        return self.filters.get(status, {})

    @property
    def taken_filter_validated_data(self):
        taken_filter_validated_data = {
            f.key(): self.taken_filter_data[f.key()]
            for f in self.taken_filters
            if self.taken_filter_data.get(f.key())
        }
        return taken_filter_validated_data

    @property
    def taken_filter_query_data(self):
        return {
            f.filter_lookup(): self.taken_filter_validated_data.get(f.key())
            for f in self.taken_filters
            if self.taken_filter_validated_data.get(f.key())
        } | {
            "melding__begraafplaats__isnull": not self.is_benc,
        }

    @property
    def is_benc(self):
        from apps.context.models import Context

        return self.context.template == Context.TemplateOpties.BENC

    @property
    def taken_sorting_choices(self):
        return (
            (
                (DATUM_REVERSE_SORTING_KEY, "Datum (nieuwste bovenaan)"),
                (DATUM_SORTING_KEY, "Datum (oudste bovenaan)"),
                (AFSTAND_SORTING_KEY, "Afstand"),
                (ADRES_SORTING_KEY, "T.h.v. Adres (a-z)"),
                (ADRES_REVERSE_SORTING_KEY, "T.h.v. Adres (z-a)"),
                (POSTCODE_SORTING_KEY, "Postcode (1000-9999)"),
                (POSTCODE_REVERSE_SORTING_KEY, "Postcode (9999-1000)"),
            )
            if not self.is_benc
            else (
                (DATUM_REVERSE_SORTING_KEY, "Datum (nieuwste bovenaan)"),
                (DATUM_SORTING_KEY, "Datum (oudste bovenaan)"),
            )
        )

    @property
    def taken_sorting_order_by(self):
        mapping = {
            POSTCODE_SORTING_KEY: "melding__postcode",
            ADRES_SORTING_KEY: "melding__locatie_verbose",
            DATUM_SORTING_KEY: "taakstatus__aangemaakt_op",
            AFSTAND_SORTING_KEY: "afstand",
        }
        sorting_direction = "-" if len(self.taken_sorting.split("-")) > 1 else ""
        sorting = self.taken_sorting.split("-")[0]
        return f"{sorting_direction}{mapping.get(sorting, 'melding__locatie_verbose')}"

    @property
    def taken_sorting(self):
        return self.ui_instellingen.get("sortering", DATUM_REVERSE_SORTING_KEY)
