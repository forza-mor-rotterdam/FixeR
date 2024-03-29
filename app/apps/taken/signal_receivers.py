import logging

from apps.services.mercure import MercureService
from apps.taken.managers import aangemaakt, gebeurtenis_toegevoegd, status_aangepast
from apps.taken.models import Taak
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Taak)
def taak_post_save(sender, instance, created, **kwargs):
    taak_url = reverse("taak_detail", args=(instance.id,))
    mercure_service = None
    try:
        mercure_service = MercureService()
    except MercureService.ConfigException:
        ...

    if mercure_service:
        mercure_service.publish(taak_url, {"url": taak_url, "taak_id": instance.id})


@receiver(status_aangepast, dispatch_uid="taak_status_aangepast")
def status_aangepast_handler(sender, taak, status, vorige_status, *args, **kwargs):
    logger.debug(f"status_aangepast_handler: {taak} - {vorige_status} -> {status}")


@receiver(aangemaakt, dispatch_uid="taak_aangemaakt")
def aangemaakt_handler(sender, taak, *args, **kwargs):
    logger.debug(f"aangemaakt_handler: {taak}")


@receiver(gebeurtenis_toegevoegd, dispatch_uid="gebeurtenis_toegevoegd")
def gebeurtenis_toegevoegd_handler(sender, taak, taakgebeurtenis, *args, **kwargs):
    logger.debug(f"gebeurtenis_toegevoegd_handler: {taak}")
