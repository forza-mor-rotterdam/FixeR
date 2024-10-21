import celery
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache

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


@shared_task(bind=True, base=BaseTaskWithRetryBackoff)
def task_update_wijken_en_buurten(self):
    from apps.main.services import PDOKService

    service = PDOKService()
    response = service.get_buurten_middels_gemeentecode()
    cache.set(
        settings.WIJKEN_EN_BUURTEN_CACHE_KEY,
        response,
        settings.WIJKEN_EN_BUURTEN_CACHE_TIMEOUT,
    )

    return f"Update wijken en buurten voltooid, gemeentecode={settings.WIJKEN_EN_BUURTEN_GEMEENTECODE}, cache timeout={settings.WIJKEN_EN_BUURTEN_CACHE_TIMEOUT}"
