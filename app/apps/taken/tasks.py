import celery
from apps.main.services import MORCoreService
from apps.taken.models import Taak, Taakgebeurtenis, Taakstatus
from celery import shared_task
from celery.utils.log import get_task_logger
from dateutil import parser

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6


DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6
RETRY_BACKOFF_MAX = 60 * 30
RETRY_BACKOFF = 120


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY
    retry_backoff_max = RETRY_BACKOFF_MAX
    retry_backoff = RETRY_BACKOFF
    retry_jitter = True


@shared_task(bind=True)
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


@shared_task(bind=True)
def update_taakopdracht_data(self, taak_id):
    taak = Taak.objects.get(id=taak_id)
    get_taakopdracht_response = MORCoreService().haal_data(
        taak.taakopdracht,
    )
    status_code = 200
    if isinstance(get_taakopdracht_response, dict) and get_taakopdracht_response.get(
        "error"
    ):
        status_code = get_taakopdracht_response.get("error", {}).get("status_code")

    taak.additionele_informatie["taakopdracht"] = get_taakopdracht_response
    taak.additionele_informatie["taakopdracht_status_code"] = str(status_code)

    taak.save(update_fields=["additionele_informatie"])

    return {
        "taak_id": taak_id,
    }


@shared_task(bind=True)
def update_taak_status_met_taakopdracht_status(self, taak_id):
    taak = Taak.objects.get(id=taak_id)

    taakopdracht_status_naam = (
        taak.additionele_informatie.get("taakopdracht", {})
        .get("status", {})
        .get("naam")
    )
    if (
        taakopdracht_status_naam in ("voltooid", "voltooid_met_feedback")
        and taakopdracht_status_naam != taak.taakstatus.naam
    ):
        taakstatus = Taakstatus.objects.create(
            naam=taakopdracht_status_naam,
            taak=taak,
        )
        resolutie = taak.additionele_informatie.get("taakopdracht", {}).get("resolutie")
        gebruiker = (
            taak.additionele_informatie.get("taakopdracht", {})
            .get("taakgebeurtenissen_voor_taakopdracht", [{}])[0]
            .get("gebruiker")
        )
        afgesloten_op = None
        try:
            afgesloten_op = parser.parse(
                taak.additionele_informatie.get("taakopdracht", {}).get("afgesloten_op")
            )
        except Exception:
            ...
        Taakgebeurtenis.objects.create(
            taakstatus=taakstatus,
            resolutie=resolutie,
            gebruiker=gebruiker,
            taak=taak,
        )
        taak.taakstatus = taakstatus
        taak.resolutie = resolutie
        taak.afgesloten_op = afgesloten_op
        taak.bezig_met_verwerken = False
        taak.save()

    return {
        "taak_id": taak_id,
    }
