import json
from datetime import timedelta

import celery
from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6

LOCK_EXPIRE = 5


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_maak_bijlagealias(self, bijlage_url, taakgebeurtenis_id):
    from apps.aliassen.models import BijlageAlias
    from apps.taken.models import Taakgebeurtenis

    bijlage_instance = BijlageAlias.objects.create(
        bron_url=bijlage_url,
        taak_gebeurtenis=Taakgebeurtenis.objects.get(pk=taakgebeurtenis_id),
    )

    return f"BijlageAlias id: {bijlage_instance.pk}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_update_melding_alias_data(self, cache_timeout=0):
    from apps.aliassen.models import MeldingAlias
    from apps.taken.models import TaakZoekData

    if not isinstance(cache_timeout, int):
        cache_timeout = 0

    datetime_to_update = timezone.now() - timedelta(seconds=cache_timeout)
    all_melding_alias_items = MeldingAlias.objects.all()
    melding_alias_items_for_update = all_melding_alias_items.filter(
        aangepast_op__lte=datetime_to_update
    )
    for melding_alias in melding_alias_items_for_update:
        melding_alias.save()
        location_data = melding_alias.response_json.get("locaties_voor_melding")[0]
        signalen = melding_alias.response_json.get("signalen_voor_melding", [])
        signaal_ids = [signaal.get("bron_signaal_id") for signaal in signalen]

        # Retrieve or create TaakZoekData instance based on the unique identifier
        taak_zoek_data_instance, _ = TaakZoekData.objects.update_or_create(
            melding_alias=melding_alias,
            defaults={
                "geometrie": GEOSGeometry(json.dumps(location_data.get("geometrie")))
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
        # Associate the retrieved TaakZoekData instance with all Taak instances associated with the melding_alias
        for taak in melding_alias.taken_voor_meldingalias.all():
            taak.taak_zoek_data = taak_zoek_data_instance
            taak.save()

    return f"updated/totaal={melding_alias_items_for_update.count()}/{all_melding_alias_items.count()}"
