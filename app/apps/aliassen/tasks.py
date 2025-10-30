import uuid

import celery
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6
RETRY_BACKOFF_MAX = 60 * 30
RETRY_BACKOFF = 120


class BaseTaskWithRetryBackoff(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY
    retry_backoff_max = RETRY_BACKOFF_MAX
    retry_backoff = RETRY_BACKOFF
    retry_jitter = True


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


@shared_task(bind=True)
def task_update_melding_alias_data_voor_reeks(
    self,
    start_index=None,
    eind_index=None,
    order_by="id",
    filters={},
    meldingalias_ids=[],
):
    from apps.aliassen.models import MeldingAlias

    if not meldingalias_ids:
        meldingalias_ids = list(
            MeldingAlias.objects.order_by(
                *[order_key.strip(" ") for order_key in order_by.split(",")]
            )
            .filter(**filters)
            .values_list("id", flat=True)
        )[start_index:eind_index]
    for meldingalias_id in meldingalias_ids:
        task_update_melding_alias_data.delay(meldingalias_id)

    return f"Haal melding data en update melding alias fields voor indexes, start_index={start_index}, eind_index={eind_index}, meldingalias_ids={len(meldingalias_ids)}"


@shared_task(bind=True)
def task_update_melding_zoek_data_voor_reeks(
    self,
    start_index=None,
    eind_index=None,
    order_by="id",
    filters={},
    meldingalias_ids=[],
):
    from apps.aliassen.models import MeldingAlias

    if not meldingalias_ids:
        meldingalias_ids = list(
            MeldingAlias.objects.order_by(
                *[order_key.strip(" ") for order_key in order_by.split(",")]
            )
            .filter(**filters)
            .values_list("id", flat=True)
        )[start_index:eind_index]
    for meldingalias_id in meldingalias_ids:
        task_update_melding_zoek_data.delay(meldingalias_id)

    return f"Update melding zoek & filter data voor indexes, start_index={start_index}, eind_index={eind_index}, meldingalias_ids={len(meldingalias_ids)}"


@shared_task(bind=True, base=BaseTaskWithRetryBackoff)
def task_update_melding_alias_data(self, meldingalias_id):
    from apps.aliassen.models import MeldingAlias

    meldingalias = MeldingAlias.objects.filter(pk=meldingalias_id).first()
    if meldingalias:
        meldingalias.valideer_bron_url()
        meldingalias.save()
        meldingalias.update_zoek_data()
        meldingalias.save()
    else:
        return f"Warning: MeldingAlias niet gevonden o.b.v. meldingalias_id '{meldingalias_id}'"
    return f"MeldingAlias data with id={meldingalias_id}, updated"


@shared_task(bind=True, base=BaseTaskWithRetryBackoff)
def task_update_melding_alias_data_v2(self, meldingalias_uuid):
    from apps.aliassen.models import MeldingAlias

    meldingaliassen = MeldingAlias.objects.filter(uuid=uuid.UUID(meldingalias_uuid))
    if meldingaliassen:
        meldingalias = meldingaliassen[0]
        meldingalias.valideer_bron_url()
        meldingalias.save()
        if meldingalias.response_status_code not in [200, 404, 400]:
            raise Exception(
                f"meldingalias.response_status_code not in [200, 404, 400], code={meldingalias.response_status_code}, meldingalias_uuid={meldingalias_uuid}"
            )
        meldingalias.update_zoek_data()
        meldingalias.save()
    else:
        return f"Warning: MeldingAlias niet gevonden o.b.v. meldingalias_uuid '{meldingalias_uuid}'"
    return f"MeldingAlias data with uuid={meldingalias_uuid}, updated"


@shared_task(bind=True, base=BaseTaskWithRetryBackoff)
def task_update_melding_zoek_data(self, meldingalias_id):
    from apps.aliassen.models import MeldingAlias

    meldingalias = MeldingAlias.objects.filter(pk=meldingalias_id).first()
    if meldingalias:
        meldingalias.update_zoek_data()
        meldingalias.save()
    else:
        return f"Warning: MeldingAlias niet gevonden o.b.v. meldingalias_id '{meldingalias_id}'"
    return f"MeldingAlias zoek data with id={meldingalias_id}, updated"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_vind_en_fix_meldingalias_duplicaten(self):
    from apps.aliassen.models import MeldingAlias
    from apps.taken.models import Taak
    from django.db.models import Count

    mas = (
        MeldingAlias.objects.values("bron_url")
        .annotate(Count("id"))
        .order_by()
        .filter(id__count__gt=1)
    )
    urls = [ms.get("bron_url") for ms in mas]
    logger.info("urls")
    logger.info(urls)
    for url in urls:
        melding_alias = MeldingAlias.objects.filter(bron_url=url).first()
        logger.info("melding_alias")
        logger.info(melding_alias)
        taken = [taak for taak in Taak.objects.filter(melding__bron_url=url)]
        logger.info("taken")
        logger.info(taken)
        for taak in taken:
            logger.info("taak")
            logger.info(taak.melding.id)
            taak.melding = melding_alias
        Taak.objects.bulk_update(taken, fields=["melding"])

    melding_alias_to_be_deleted = MeldingAlias.objects.annotate(
        taken_count=Count("taken_voor_meldingalias")
    ).filter(
        taken_count=0,
        bron_url__in=urls,
    )
    deleted_melding_alias_ids = [
        str(id) for id in list(melding_alias_to_be_deleted.values_list("id", flat=True))
    ]
    logger.info("deleted_melding_alias_ids")
    logger.info(deleted_melding_alias_ids)
    melding_alias_deleted = MeldingAlias.objects.filter(
        id__in=deleted_melding_alias_ids
    ).delete()
    logger.info("melding_alias_deleted")
    logger.info(melding_alias_deleted)

    return f"Dubbele MeldingAlias: aantal={len(urls)}, bron_urls={', '.join(urls)}, verwijderde MeldingAlias ids={', '.join(deleted_melding_alias_ids)}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_vind_meldingalias_duplicaten(self):
    from apps.aliassen.models import MeldingAlias
    from django.db.models import Count

    mas = (
        MeldingAlias.objects.values("bron_url")
        .annotate(Count("id"))
        .order_by()
        .filter(id__count__gt=1)
    )
    urls = [ms.get("bron_url") for ms in mas]
    return f"Dubbele MeldingAlias: aantal={len(urls)}, bron_urls={', '.join(urls)}"
