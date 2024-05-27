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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = GebruikerManager()

    def __str__(self):
        if self.first_name:
            return f"{self.first_name}{' ' if self.last_name else ''}{self.last_name}"
        return self.email

    def rollen_verbose(self):
        return mark_safe(
            f"rol: <strong>{self.profiel.context.naam if self.profiel.context else '- geen rol - '}</strong>"
        )

    def rechten_verbose(self):
        return mark_safe(
            f"rechten: <strong>{self.groups.all().first().name if self.groups.all() else '- geen rechten - '}</strong>"
        )

    def afdelingen_verbose(self):
        return mark_safe(
            f"afdelingen: <strong>{self.profiel.afdeling.naam if self.profiel.afdeling else '- geen rol - '}</strong>"
        )

    @property
    def rechtengroep(self):
        return mark_safe(
            f"{self.groups.all().first().name if self.groups.all() else ''}"
        )

    @property
    def rol(self):
        return mark_safe(f"{self.profiel.context.naam if self.profiel.context else ''}")

    @property
    def afdelingen(self):
        return mark_safe(
            f"{self.profiel.afdeling.naam if self.afdeling.context else ''}"
        )

    def serialized_instance(self):
        if not self.is_authenticated:
            return None
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
                "afdeling": (
                    self.profiel.afdeling.naam
                    if hasattr(self, "profiel")
                    and hasattr(self.profiel, "afdeling")
                    and hasattr(self.profiel.afdeling, "naam")
                    else None
                ),
            }
        )

        return dict_instance


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
    afdelingen = models.ManyToManyField(
        to="authenticatie.ProfielAfdeling",
        related_name="profielen_voor_afdelingen",
        blank=True,
    )
    profielfoto = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )

    class WerklocatieOpties(models.TextChoices):
        VOLLEDIG = "volledig", "volledig"
        NOORD = "noord", "noord"
        ZUID = "zuid", "Zuid"

    werklocatie = models.CharField(
        max_length=50,
        choices=WerklocatieOpties.choices,
        null=True,
        blank=True,
    )
    buurten = ArrayField(
        models.CharField(max_length=500, blank=True), blank=True, null=True
    )

    def __str__(self):
        if self.gebruiker:
            return f"Profiel voor: {self.gebruiker}"
        return f"Profiel id: {self.pk}"


class ProfielAfdeling(BasisModel):
    """
    ProfielAfdeling model voor profielen
    """

    class OnderdeelOpties(models.TextChoices):
        SHOON = "schoon", "Schoon"
        HEEL = "heel", "Heel"
        VELIG = "veilig", "Veilig"

    naam = models.CharField(max_length=100)
    onderdeel = models.CharField(
        max_length=50,
        choices=OnderdeelOpties.choices,
    )

    def __str__(self):
        return self.naam
