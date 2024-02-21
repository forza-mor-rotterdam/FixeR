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

    if not isinstance(cache_timeout, int):
        cache_timeout = 0

    datetime_to_update = timezone.now() - timedelta(seconds=cache_timeout)
    all_melding_alias_items = MeldingAlias.objects.all()
    melding_alias_items_for_update = all_melding_alias_items.filter(
        aangepast_op__lte=datetime_to_update
    )
    for melding_alias in melding_alias_items_for_update:
        melding_alias.save()
        if melding_alias.response_json.get(
            "locaties_voor_melding"
        ) and melding_alias.response_json.get("locaties_voor_melding")[0].get(
            "geometrie"
        ):
            melding_alias.taken_voor_meldingalias.all().update(
                geometrie=GEOSGeometry(
                    json.dumps(
                        melding_alias.response_json.get("locaties_voor_melding")[0].get(
                            "geometrie"
                        )
                    )
                )
            )

    return f"updated/totaal={melding_alias_items_for_update.count()}/{all_melding_alias_items.count()}"
