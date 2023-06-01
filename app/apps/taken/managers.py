import logging

from django.contrib.gis.db import models
from django.db import OperationalError, transaction
from django.dispatch import Signal
from django.utils import timezone

logger = logging.getLogger(__name__)

aangemaakt = Signal()
status_aangepast = Signal()
gebeurtenis_toegevoegd = Signal()


class TaakManager(models.Manager):
    class TaakInGebruik(Exception):
        ...

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

    def status_aanpassen(self, serializer, taak, db="default"):
        from apps.taken.models import Taak

        with transaction.atomic():
            try:
                locked_taak = (
                    Taak.objects.using(db)
                    .select_for_update(nowait=True)
                    .get(pk=taak.pk)
                )
            except OperationalError:
                raise TaakManager.TaakInGebruik

            vorige_status = locked_taak.taakstatus
            print("status_aanpassen")
            print(taak)
            resolutie = serializer.validated_data.pop("resolutie", None)
            bijlagen = serializer.validated_data.pop("bijlagen", None)
            print(bijlagen)
            print(serializer.validated_data)
            taakgebeurtenis = serializer.save(
                taak=locked_taak,
            )

            locked_taak.taakstatus = taakgebeurtenis.taakstatus

            if not locked_taak.taakstatus.volgende_statussen():
                locked_taak.afgesloten_op = timezone.now().isoformat()
                if resolutie in [ro[0] for ro in Taak.ResolutieOpties.choices]:
                    locked_taak.resolutie = resolutie
            locked_taak.save()

            transaction.on_commit(
                lambda: status_aangepast.send_robust(
                    sender=self.__class__,
                    taak=locked_taak,
                    status=taakgebeurtenis.taakstatus,
                    vorige_status=vorige_status,
                )
            )

        return taak
