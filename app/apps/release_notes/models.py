import logging
import mimetypes
import os
from os.path import exists

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
from sorl.thumbnail import get_thumbnail
from utils.images import get_upload_path
from utils.models import BasisModel

logger = logging.getLogger(__name__)


class Bijlage(BasisModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    bestand = models.FileField(
        upload_to=get_upload_path, null=False, blank=False, max_length=255
    )
    afbeelding = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )
    afbeelding_verkleind = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )

    mimetype = models.CharField(max_length=30, blank=False, null=False)
    is_afbeelding = models.BooleanField(default=False)

    class BestandPadFout(Exception):
        ...

    class AfbeeldingVersiesAanmakenFout(Exception):
        ...

    def _is_afbeelding(self):
        try:
            Image.open(self.bestand)
        except UnidentifiedImageError:
            return False
        return True

    def _heic_to_jpeg(self, file_field):
        register_heif_opener()

        with Image.open(file_field.path) as image:
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Remove .heic extension and add .jpg
            new_file_name = f"{os.path.splitext(file_field.name)[0]}.jpg"

            image.save(os.path.join(settings.MEDIA_ROOT, new_file_name), "JPEG")

        return new_file_name

    def aanmaken_afbeelding_versies(self):
        logger.info("aanmaken_afbeelding_versies")
        mt = mimetypes.guess_type(self.bestand.path, strict=True)
        logger.info(mt)

        if exists(self.bestand.path):
            logger.info(self.bestand.path)
            bestand = self.bestand.path
            self.is_afbeelding = self._is_afbeelding()
            if mt:
                self.mimetype = mt[0]
            if self.mimetype == "image/heic":
                bestand = self._heic_to_jpeg(self.bestand)
                self.is_afbeelding = True

            logger.info(f"is afbeelding: {self.is_afbeelding}")
            # Dont convert to jpeg if the image is a gif.
            if self.mimetype == "image/gif":
                return
            if self.is_afbeelding:
                try:
                    self.afbeelding_verkleind.name = get_thumbnail(
                        bestand,
                        settings.THUMBNAIL_KLEIN,
                        format="JPEG",
                        quality=99,
                    ).name
                    self.afbeelding.name = get_thumbnail(
                        bestand,
                        settings.THUMBNAIL_STANDAARD,
                        format="JPEG",
                        quality=80,
                    ).name
                except Exception as e:
                    raise Bijlage.AfbeeldingVersiesAanmakenFout(
                        f"aanmaken_afbeelding_versies: get_thumbnail fout: {e}"
                    )
        else:
            raise Bijlage.BestandPadFout(
                f"aanmaken_afbeelding_versies: bestand path bestaat niet, bijlage id: {self.pk}"
            )

    class Meta:
        verbose_name = "Bijlage"
        verbose_name_plural = "Bijlagen"


class ReleaseNote(BasisModel):
    titel = models.CharField(max_length=255)
    beschrijving = models.TextField(blank=True, max_length=500)
    publicatie_datum = models.DateTimeField(null=True, blank=True)
    bijlagen = GenericRelation(Bijlage)
    versie = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        formatted_date = self.aangemaakt_op.strftime("%d-%m-%Y %H:%M:%S")
        return f"{self.titel} - {formatted_date}"
