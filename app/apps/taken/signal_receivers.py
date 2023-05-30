import logging

from apps.taken.managers import aangemaakt, gebeurtenis_toegevoegd, status_aangepast
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(status_aangepast, dispatch_uid="taak_status_aangepast")
def status_aangepast_handler(sender, taak, status, vorige_status, *args, **kwargs):
    logger.debug(f"status_aangepast_handler: {taak} - {vorige_status} -> {status}")


@receiver(aangemaakt, dispatch_uid="taak_aangemaakt")
def aangemaakt_handler(sender, taak, *args, **kwargs):
    logger.debug(f"aangemaakt_handler: {taak}")


@receiver(gebeurtenis_toegevoegd, dispatch_uid="gebeurtenis_toegevoegd")
def gebeurtenis_toegevoegd_handler(sender, taak, taakgebeurtenis, *args, **kwargs):
    logger.debug(f"gebeurtenis_toegevoegd_handler: {taak}")
