from apps.release_notes.models import Bijlage
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from utils.models import BasisModel


class Afdeling(BasisModel):
    """
    Afdeling model voor Taaktypes
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


class TaaktypeMiddel(BasisModel):
    """
    TaaktypeMiddel model voor Taaktypes
    """

    naam = models.CharField(max_length=100)

    def __str__(self):
        return self.naam


class TaaktypeReden(BasisModel):
    """
    TaaktypeReden model voor Taaktypes
    """

    class TypeOpties(models.TextChoices):
        WAAROM_WEL = "waarom_wel", "Waarom wel"
        WAAROM_NIET = "waarom_niet", "Waarom niet"

    toelichting = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )
    type = models.CharField(
        max_length=50,
        choices=TypeOpties.choices,
    )
    bijlagen = GenericRelation(Bijlage)

    taaktype = models.ForeignKey(
        to="taken.Taaktype",
        related_name="taaktyperedenen_voor_taaktype",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.id}_{self.toelichting if self.toelichting else ''}"
