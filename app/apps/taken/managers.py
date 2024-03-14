import json
import logging

from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
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
            serializer.validated_data["melding"] = meldingalias
            gebruiker = serializer.validated_data.pop("gebruiker", None)
            taak = serializer.save()

            location_data = meldingalias.response_json.get("locaties_voor_melding")[0]
            signalen = meldingalias.response_json.get("signalen_voor_melding", [])
            signaal_ids = [signaal.get("bron_signaal_id") for signaal in signalen]

            taak_zoek_data_instance, _ = TaakZoekData.objects.update_or_create(
                melding_alias=meldingalias,
                defaults={
                    "geometrie": GEOSGeometry(
                        json.dumps(location_data.get("geometrie"))
                    )
                    if location_data.get("geometrie")
                    else None,
                    "locatie_type": location_data.get("locatie_type"),
                    "plaatsnaam": location_data.get("plaatsnaam"),
                    "straatnaam": location_data.get("straatnaam"),
                    "huisnummer": location_data.get("huisnummer"),
                    "huisletter": location_data.get("huisletter"),
                    "toevoeging": location_data.get("toevoeging"),
                    "postcode": location_data.get("postcode"),
                    "wijknaam": location_data.get("wijknaam"),
                    "buurtnaam": location_data.get("buurtnaam"),
                    "begraafplaats": location_data.get("begraafplaats"),
                    "grafnummer": location_data.get("grafnummer"),
                    "vak": location_data.get("vak"),
                    "lichtmast_id": location_data.get("lichtmast_id"),
                    "bron_signaal_ids": signaal_ids,
                },
            )

            taak.taak_zoek_data = taak_zoek_data_instance

            taakstatus = Taakstatus.objects.create(
                taak=taak,
            )
            Taakgebeurtenis.objects.create(
                taak=taak,
                taakstatus=taakstatus,
                gebruiker=gebruiker,
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
        from apps.aliassen.tasks import task_maak_bijlagealias
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
            resolutie = serializer.validated_data.pop("resolutie", None)
            bijlagen = serializer.validated_data.pop("bijlagen", None)
            uitvoerder = serializer.validated_data.pop("uitvoerder", None)
            taakgebeurtenis = serializer.save(
                taak=locked_taak,
            )
            for bijlage in bijlagen:
                task_maak_bijlagealias.delay(bijlage, taakgebeurtenis.pk)

            locked_taak.taakstatus = taakgebeurtenis.taakstatus
            locked_taak.additionele_informatie["uitvoerder"] = uitvoerder

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
