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

    @property
    def wijken_or_taaktypes_empty(self):
        buurt_empty = not self.wijken or all(not wijk for wijk in self.wijken)
        taken_empty = not self.taaktypes.exists()
        return buurt_empty or taken_empty
