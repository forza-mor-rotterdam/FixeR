import celery
from apps.meldingen.service import MeldingenService
from apps.taken.models import Taak
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
def compare_and_update_status(self, taak_id):
    taak = Taak.objects.get(id=taak_id)

    taakopdracht_response = MeldingenService().get_taakopdracht_data(taak.taakopdracht)
    if taakopdracht_response.status_code == 200:
        taakopdracht = taakopdracht_response.json()

        taakgebeurtenis = (
            taak.taakgebeurtenissen_voor_taak.filter(taakstatus=taak.taakstatus)
            .order_by("-aangemaakt_op")
            .first()
        )

        if taakgebeurtenis:
            if taak.taakstatus.naam == "voltooid" and (
                taak.taakstatus.naam != taakopdracht.get("status").get("naam")
            ):
                update_data = {
                    "taakopdracht_url": taak.taakopdracht,
                    "status": taak.taakstatus.naam,
                    "resolutie": "opgelost",
                    "omschrijving_intern": taakgebeurtenis.omschrijving_intern,
                    "gebruiker": taakgebeurtenis.gebruiker,
                    "bijlagen": [],
                }
                taak_status_aanpassen_response = (
                    MeldingenService().taak_status_aanpassen(
                        **update_data,
                    )
                )
                if taak_status_aanpassen_response.status_code != 200:
                    logger.error(
                        f"incident_modal_handle taak_status_aanpassen: status_code={taak_status_aanpassen_response.status_code}, taak_id={taak_id}, taakopdracht_id={taakopdracht.get('id')}, update_data={update_data}"
                    )
                else:
                    logger.info(
                        f"Taakopdracht in Mor-Core updated successfully for  FixeR taak_id: {taak_id} and MOR-Core taakopdracht_id: {taakopdracht.get('id')}."
                    )

            else:
                logger.warning(
                    f"Not a voltooide status or taak and taakopdracht status match. Taak taakstatus: {taak.taakstatus.naam}, taakopdracht status: {taakopdracht.get('status').get('naam')}"
                )
        else:
            logger.warning("No Taakgebeurtenis found for the current Taakstatus.")
    else:
        logger.error(
            f"No taakopdracht response: status_code={taakopdracht_response.status_code}, taak_id={taak_id}"
        )
