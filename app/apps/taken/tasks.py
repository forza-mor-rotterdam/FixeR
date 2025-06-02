import celery
from apps.main.services import MORCoreService
from apps.main.utils import to_base64
from apps.taken.models import Taak, Taakgebeurtenis, Taakstatus
from celery import chord, group, shared_task
from celery.utils.log import get_task_logger
from dateutil import parser
from django.core.cache import cache

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6


DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6
RETRY_BACKOFF_MAX = 60 * 30
RETRY_BACKOFF = 120


TASK_LOCK_KEY_NOTFICATIES_VOOR_TAKEN = "task_taakopdracht_notificatie_voor_taken_lijst"


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


@shared_task(bind=True)
def task_taakopdracht_notificatie_voor_taakgebeurtenissen(self, taakgebeurtenis_ids):
    from apps.taken.models import Taakgebeurtenis

    if not isinstance(taakgebeurtenis_ids, list):
        return "taakgebeurtenis_ids is geen list"

    task_lock_key = TASK_LOCK_KEY_NOTFICATIES_VOOR_TAKEN
    if cache.get(task_lock_key):
        return "task_taakopdracht_notificatie_voor_taken_lijst is nog bezig"
    else:
        cache.set(task_lock_key, True, 60)

    taakgebeurtenis_ids = list(
        Taakgebeurtenis.objects.filter(
            id__in=taakgebeurtenis_ids,
            notificatie_verstuurd=False,
        ).values_list("id", flat=True)
    )

    taakgebeurtenissen_group = group(
        task_taakopdracht_notificatie.si(taakgebeurtenis_id)
        for taakgebeurtenis_id in taakgebeurtenis_ids
    )
    taakgebeurtenissen_group()
    cache.delete(task_lock_key)
    return f"Bezig met het versturen van notificaties voor taakgebeurtenissen={taakgebeurtenis_ids}"


@shared_task(bind=True)
def task_taakopdracht_notificatie_voor_taak(self, taak_id):
    from apps.taken.models import Taak

    task_lock_key = (
        f"task_lock_task_taakopdracht_notificatie_voor_taak_taak_id_{taak_id}"
    )
    if cache.get(task_lock_key):
        return "task_taakopdracht_notificatie_voor_taak is nog bezig"
    else:
        cache.set(task_lock_key, True, 60)

    taak = Taak.objects.filter(id=taak_id).first()
    if not taak:
        return f"Taak met taak_id {taak_id}, is niet gevonden"

    # selecteer alle taakgebeurtenissen voor deze taak die nog niet gesynced zijn met mor-core en orden deze, zodat de eerst aangemaakte het eerst in de rij staat
    taakgebeurtenissen_voor_taak = list(
        taak.taakgebeurtenissen_voor_taak.filter(notificatie_verstuurd=False)
        .order_by("aangemaakt_op")
        .values_list("id", flat=True)
    )

    # happy, deze taak heeft al zijn taakgebeurtenissen gestuurd
    if not taakgebeurtenissen_voor_taak:
        return f"Alle notificaties voor taak met taak_id {taak_id}, notificaties zijn al verstuurd"

    # Er moeten nog taakgebeurtenis notifificaties gestuurd worden. In een normale situatie wordt er na een status wijziging in FixeR, 1 notificatie verstuurd.
    # Als mor-core niet beschikbaar was om notificaties te verwerken stapelen de taakgebeurtenissen zich op, en moeten ze achteraf gestuurd worden, het aantal taakgebeurtenissen hieronder is dan meer dan 1.
    taakgebeurtenissen_chord = chord(
        (
            task_taakopdracht_notificatie.si(taakgebeurtenis_id)
            for taakgebeurtenis_id in taakgebeurtenissen_voor_taak
        ),
        task_taakopdracht_notificatie_voor_taak_voltooid.si(
            taak_id, len(taakgebeurtenissen_voor_taak), task_lock_key
        ),
    )
    taakgebeurtenissen_chord()
    return f"Bezig met het verturen van {len(taakgebeurtenissen_voor_taak)} notificaties voor taak met taak_id {taak_id}"


@shared_task(bind=True)
def task_taakopdracht_notificatie_voor_taak_voltooid(
    self, taak_id, notificatie_aantal, task_lock_key
):
    cache.delete(task_lock_key)
    return f"Klaar met het verturen van {notificatie_aantal} notificaties voor taak met taak_id {taak_id}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_taakopdracht_notificatie(
    self,
    taakgebeurtenis_id,
):
    from apps.taken.models import Taakgebeurtenis

    task_lock_key = f"task_lock_task_taakopdracht_notificatie_taakgebeurtenis_id_{taakgebeurtenis_id}"
    if cache.get(task_lock_key):
        return "task_taakopdracht_notificatie is nog bezig"
    else:
        cache.set(task_lock_key, True, 60)

    taakgebeurtenis = Taakgebeurtenis.objects.get(id=taakgebeurtenis_id)
    taak = taakgebeurtenis.taak

    if taakgebeurtenis.notificatie_verstuurd:
        return "De notificatie voor deze taakgebeurtenis is al verstuurd"

    bijlagen = [{"bestand": to_base64(b)} for b in taakgebeurtenis.bijlage_paden]

    taak_status_aanpassen_response = MORCoreService().taakopdracht_notificatie(
        melding_url=taak.melding.bron_url,
        taakopdracht_url=taak.taakopdracht,
        status=taakgebeurtenis.taakstatus.naam if taakgebeurtenis.taakstatus else None,
        resolutie=taakgebeurtenis.resolutie,
        gebruiker=taakgebeurtenis.gebruiker,
        omschrijving_intern=taakgebeurtenis.omschrijving_intern,
        aangemaakt_op=taakgebeurtenis.aangemaakt_op.isoformat(),
        bijlagen=bijlagen,
    )
    if taak_status_aanpassen_response.get("error"):
        cache.delete(task_lock_key)
        raise Exception(
            f"task taakopdracht_notificatie: fout={taak_status_aanpassen_response.get('error')}, taak_uuid={taak.uuid}, taakopdracht_url={taak.taakopdracht}"
        )

    for vervolg_taaktype in taakgebeurtenis.vervolg_taaktypes:
        task_taak_aanmaken.delay(
            melding_uuid=taak.melding.response_json.get("uuid"),
            taaktype_url=vervolg_taaktype.get("taaktype_url"),
            titel=vervolg_taaktype.get("omschrijving"),
            bericht=vervolg_taaktype.get("bericht"),
            # bericht=vervolg_taak_bericht,
            # temporary use 'interne opmerkingen' also for all new tasks, after redesign of this modal we will reimplement a message per task
            gebruiker_email=taakgebeurtenis.gebruiker,
        )
    taakgebeurtenis.notificatie_verstuurd = True
    taakgebeurtenis.save(update_fields=["notificatie_verstuurd"])

    cache.delete(task_lock_key)
    return {
        "taak_id": taak.uuid,
        "taakopdracht_url": taak.taakopdracht,
        "melding_uuid": taak.melding.response_json.get("uuid"),
    }


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_taak_aanmaken(
    self, melding_uuid, taaktype_url, titel, bericht, gebruiker_email
):
    taak_aanmaken_response = MORCoreService().taak_aanmaken(
        melding_uuid=melding_uuid,
        taakapplicatie_taaktype_url=taaktype_url,
        titel=titel,
        bericht=bericht,
        gebruiker=gebruiker_email,
    )

    if isinstance(taak_aanmaken_response, dict) and taak_aanmaken_response.get("error"):
        error = taak_aanmaken_response.get("error", {})
        log_entry = f'task taak_aanmaken: status_code={error.get("status_code")}, taaktype_url={taaktype_url}, melding_uuid={melding_uuid}, bericht={error.get("bericht")}'
        logger.error(log_entry)
        raise Exception(log_entry)

    return {
        "taaktype_url": taaktype_url,
        "melding_uuid": melding_uuid,
    }


@shared_task(bind=True)
def start_update_taakopdracht_data_for_taak_ids(self, taak_ids=[]):
    for id in taak_ids:
        update_taakopdracht_data.delay(id)

    return {
        "taak_ids aantal": len(taak_ids),
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
        taak.save()

    return {
        "taak_id": taak_id,
    }


@shared_task(bind=True)
def task_verwijderd_op_voor_afgeronde_taken_voor_taak_ids(self, taak_ids=[]):
    taken = Taak.objects.filter(
        id__in=taak_ids,
        taakstatus__naam__in=[
            Taakstatus.NaamOpties.VOLTOOID,
            Taakstatus.NaamOpties.VOLTOOID_MET_FEEDBACK,
        ],
        verwijderd_op__isnull=False,
    )
    for taak in taken:
        taak.verwijderd_op = None
        taak.save()

    return {
        "taak_ids aantal": len(taak_ids),
    }
