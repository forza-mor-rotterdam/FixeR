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


class TaaktypeVoorbeeldsituatie(BasisModel):
    """
    TaaktypeVoorbeeldsituatie model voor Taaktypes
    """

    from apps.release_notes.models import Bijlage

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

    # taaktype = models.ForeignKey(
    #     to="taken.Taaktype",
    #     related_name="voorbeeldsituatie_voor_taaktype",
    #     on_delete=models.CASCADE,
    #     to_field="id",
    #     blank=True,
    #     null=True,
    # )

    def __str__(self):
        return f"{self.id}_{self.toelichting if self.toelichting else ''}"
