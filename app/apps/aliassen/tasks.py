import celery
from celery import shared_task
from celery.utils.log import get_task_logger

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
