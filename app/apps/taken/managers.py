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
        from apps.taken.models import Taakgebeurtenis, Taakstatus, TaakZoekData

        with transaction.atomic():
            meldingalias, meldingalias_aangemaakt = MeldingAlias.objects.get_or_create(
                bron_url=serializer.validated_data.get("melding")
            )
            taak_zoek_data_instance, _ = TaakZoekData.objects.get_or_create(
                melding_alias=meldingalias,
            )

            serializer.validated_data["melding"] = meldingalias
            serializer.validated_data["taak_zoek_data"] = taak_zoek_data_instance
            gebruiker = serializer.validated_data.pop("gebruiker", None)
            omschrijving_intern = serializer.validated_data.pop(
                "omschrijving_intern", None
            )
            taak = serializer.save()

            taakstatus = Taakstatus.objects.create(
                taak=taak,
            )
            Taakgebeurtenis.objects.create(
                taak=taak,
                taakstatus=taakstatus,
                gebruiker=gebruiker,
                omschrijving_intern=omschrijving_intern,
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

    def status_aanpassen(
        self,
        status,
        resolutie,
        omschrijving_intern,
        gebruiker,
        bijlage_paden,
        taak,
        vervolg_taaktypes,
        db="default",
    ):
        from apps.taken.models import Taak, Taakgebeurtenis, Taakstatus

        with transaction.atomic():
            try:
                locked_taak = (
                    Taak.objects.using(db)
                    .select_for_update(nowait=True)
                    .get(pk=taak.pk)
                )
            except OperationalError:
                raise TaakManager.TaakInGebruik(
                    f"De taak is op dit moment in gebruik, probeer het later nog eens. taak nummer: {taak.id}, taak uuid: {taak.uuid}"
                )

            vorige_status = locked_taak.taakstatus

            taakstatus_instance = Taakstatus.objects.create(
                taak=locked_taak,
                naam=status,
            )
            taakgebeurtenis = Taakgebeurtenis.objects.create(
                taak=locked_taak,
                taakstatus=taakstatus_instance,
                omschrijving_intern=omschrijving_intern,
                gebruiker=gebruiker,
                bijlage_paden=bijlage_paden,
                notificatie_verstuurd=False,
                vervolg_taaktypes=vervolg_taaktypes,
            )

            locked_taak.taakstatus = taakgebeurtenis.taakstatus

            if (
                Taakstatus.NaamOpties.VOLTOOID_MET_FEEDBACK
                in locked_taak.taakstatus.volgende_statussen()
                or not locked_taak.taakstatus.volgende_statussen()
            ):
                locked_taak.afgesloten_op = timezone.now().isoformat()
                if resolutie in [
                    ro[0] for ro in Taakgebeurtenis.ResolutieOpties.choices
                ]:
                    locked_taak.resolutie = resolutie
                    taakgebeurtenis.resolutie = resolutie
                    taakgebeurtenis.save()
            locked_taak.save()

            transaction.on_commit(
                lambda: status_aangepast.send_robust(
                    sender=self.__class__,
                    taak=locked_taak,
                    taakgebeurtenis=taakgebeurtenis,
                    status=taakgebeurtenis.taakstatus,
                    vorige_status=vorige_status,
                )
            )

        return taak
