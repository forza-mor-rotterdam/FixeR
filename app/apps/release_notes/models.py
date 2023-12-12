from django.db import models
from utils.images import get_upload_path
from utils.models import BasisModel


class ReleaseNote(BasisModel):
    titel = models.CharField(max_length=255)
    beschrijving = models.TextField(blank=True, max_length=500)
    publicatie_datum = models.DateTimeField(null=True, blank=True)
    afbeelding = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )
    versie = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        formatted_date = self.aangemaakt_op.strftime("%d-%m-%Y %H:%M:%S")
        return f"{self.titel} - {formatted_date}"
