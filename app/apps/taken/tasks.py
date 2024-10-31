import celery
from apps.main.services import MORCoreService
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
def move_resolutie_to_taakgebeurtenis(self):
    from apps.taken.models import Taak, Taakgebeurtenis

    for taak in Taak.objects.exclude(resolutie__isnull=True):
        taakgebeurtenis = Taakgebeurtenis.objects.filter(
            taak=taak, taakstatus__naam="voltooid"
        ).first()
        if taakgebeurtenis:
            taakgebeurtenis.resolutie = taak.resolutie
            taakgebeurtenis.save()


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_taak_status_voltooid(
    self,
    taak_id,
    resolutie,
    gebruiker_email,
    omschrijving_intern="",
    bijlage_paden=[],
    vervolg_taaktypes=[],
    vervolg_taak_bericht="",
):
    from apps.main.utils import to_base64

    taak = Taak.objects.get(id=taak_id)
    taak.bezig_met_verwerken = True
    taak.save(update_fields=["bezig_met_verwerken"])

    bijlagen = [{"bestand": to_base64(b)} for b in bijlage_paden]

    taak_status_aanpassen_response = MORCoreService().taak_status_aanpassen(
        taakopdracht_url=taak.taakopdracht,
        status="voltooid",
        resolutie=resolutie,
        gebruiker=gebruiker_email,
        omschrijving_intern=omschrijving_intern,
        bijlagen=bijlagen,
    )
    if taak_status_aanpassen_response.get("error"):
        taak.bezig_met_verwerken = False
        taak.save(update_fields=["bezig_met_verwerken"])
        raise Exception(
            f"task taak_status_aanpassen: fout={taak_status_aanpassen_response.get('error')}, taak_id={taak_id}, taakopdracht_url={taak.taakopdracht}"
        )

    for vervolg_taaktype in vervolg_taaktypes:
        task_taak_aanmaken.delay(
            melding_uuid=taak.melding.response_json.get("uuid"),
            taaktype_url=vervolg_taaktype.get("taaktype_url"),
            titel=vervolg_taaktype.get("omschrijving"),
            bericht=vervolg_taak_bericht,
            gebruiker_email=gebruiker_email,
        )
    return {
        "taak_id": taak_id,
        "taakopdracht_url": taak.taakopdracht,
        "melding_uuid": taak.melding.response_json.get("uuid"),
    }


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_taak_aanmaken(
    self, melding_uuid, taaktype_url, titel, bericht, gebruiker_email
):
    taak_aanmaken_response = MORCoreService().taak_aanmaken(
        melding_uuid=melding_uuid,
        taaktype_url=taaktype_url,
        titel=titel,
        bericht=bericht,
        gebruiker=gebruiker_email,
    )
    if taak_aanmaken_response.status_code != 200:
        raise Exception(
            f"task taak_aanmaken: status_code={taak_aanmaken_response.status_code}, taaktype_url={taaktype_url}, melding_uuid={melding_uuid}, repsonse_text={taak_aanmaken_response.text}"
        )
    return {
        "taaktype_url": taaktype_url,
        "melding_uuid": melding_uuid,
    }


@shared_task(bind=True, base=BaseTaskWithRetry)
def compare_and_update_status(self, taak_id):
    taak = Taak.objects.get(id=taak_id)
    get_taakopdracht_response = MORCoreService().get_taakopdracht_data(
        taak.taakopdracht
    )
    if get_taakopdracht_response.status_code == 200:
        taakopdracht = get_taakopdracht_response.json()

        if taak.taakstatus.naam != taakopdracht.get("status").get("naam"):
            taakgebeurtenis = (
                taak.taakgebeurtenissen_voor_taak.filter(taakstatus=taak.taakstatus)
                .order_by("-aangemaakt_op")
                .first()
            )
            if taakgebeurtenis:
                update_data = {
                    "taakopdracht_url": taak.taakopdracht,
                    "status": {"naam": taak.taakstatus.naam},
                    "resolutie": taakgebeurtenis.resolutie,
                    "omschrijving_intern": taakgebeurtenis.omschrijving_intern,
                    "gebruiker": taakgebeurtenis.gebruiker,
                    "bijlagen": [],
                }
                taak_status_aanpassen_response = MORCoreService().taak_status_aanpassen(
                    **update_data,
                )
                if taak_status_aanpassen_response.status_code != 200:
                    logger.error(
                        f"Celery compare and update status error, taak_status_aanpassen_response: status_code={taak_status_aanpassen_response.status_code}, taak_id={taak_id}, taakopdracht_id={taakopdracht.get('id')}, update_data={update_data}"
                    )
                    return {
                        "taak.id": taak_id,
                        "taakopdracht.id": taakopdracht.get("id"),
                        "taak_status_aanpassen_response.error_code": taak_status_aanpassen_response.status_code,
                    }

                else:
                    logger.warning(
                        f"Taakopdracht in Mor-Core updated successfully for FixeR taak_id: {taak_id} and MOR-Core taakopdracht_id: {taakopdracht.get('id')}."
                    )
                    return {
                        "taak.id": taak_id,
                        "taakopdracht.id": taakopdracht.get("id"),
                    }

    else:
        logger.error(
            f"Celery compare and update status error, get_taakopdracht_response: status_code={get_taakopdracht_response.status_code}, taak_id={taak_id}"
        )
        return {
            "taak.id": taak_id,
            "get_taakopdracht_response.error_code": get_taakopdracht_response.status_code,
        }
