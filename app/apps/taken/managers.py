import logging

from django.contrib.gis.db import models
from django.db import transaction
from django.dispatch import Signal

logger = logging.getLogger(__name__)

aangemaakt = Signal()
status_aangepast = Signal()
gebeurtenis_toegevoegd = Signal()


class TaakManager(models.Manager):
    def aanmaken(self, serializer, db="default"):
        from apps.aliassen.models import MeldingAlias
        from apps.taken.models import Taakgebeurtenis, Taakstatus

        with transaction.atomic():
            meldingalias, meldingalias_aangemaakt = MeldingAlias.objects.get_or_create(
                bron_url=serializer.validated_data.get("melding")
            )
            serializer.validated_data["melding"] = meldingalias
            taak = serializer.save()
            taakstatus = Taakstatus.objects.create(
                taak=taak,
            )
            Taakgebeurtenis.objects.create(
                taak=taak,
                taakstatus=taakstatus,
            )
            taak.taakstatus = taakstatus
            taak.save()
            transaction.on_commit(
                lambda: aangemaakt.send_robust(
                    sender=self.__class__,
                    taak=taak,
                )
            )
        return taak
