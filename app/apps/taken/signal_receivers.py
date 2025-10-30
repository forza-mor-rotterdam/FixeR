import logging

from apps.taken.managers import aangemaakt, gebeurtenis_toegevoegd, status_aangepast
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# @receiver(post_save, sender=Taak)
# def taak_post_save(sender, instance, created, **kwargs):
#     taak_url = reverse("taak_detail", args=(instance.uuid,))
#     mercure_service = None
#     try:
#         mercure_service = MercureService()
#     except MercureService.ConfigException:
#         ...

#     if mercure_service:
#         mercure_service.publish(taak_url, {"url": taak_url, "taak_id": instance.uuid})


@receiver(status_aangepast, dispatch_uid="taak_status_aangepast")
def status_aangepast_handler(
    sender, taak, taakgebeurtenis, status, vorige_status, *args, **kwargs
):
    if kwargs.get("raw"):
        return
    logger.debug(f"status_aangepast_handler: {taak} - {vorige_status} -> {status}")

    taakgebeurtenis.start_task_taakopdracht_notificatie()


@receiver(aangemaakt, dispatch_uid="taak_aangemaakt")
def aangemaakt_handler(sender, taak, *args, **kwargs):
    if kwargs.get("raw"):
        return
    logger.debug(f"aangemaakt_handler: {taak}")


@receiver(gebeurtenis_toegevoegd, dispatch_uid="gebeurtenis_toegevoegd")
def gebeurtenis_toegevoegd_handler(sender, taak, taakgebeurtenis, *args, **kwargs):
    if kwargs.get("raw"):
        return
    logger.debug(f"gebeurtenis_toegevoegd_handler: {taak}")
