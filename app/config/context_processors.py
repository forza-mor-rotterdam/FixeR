import logging

from apps.instellingen.models import Instelling
from apps.main.services import LocatieService, MercureService
from apps.release_notes.models import ReleaseNote
from device_detector import DeviceDetector
from django.conf import settings
from django.utils import timezone
from utils.diversen import absolute

logger = logging.getLogger(__name__)


def general_settings(context):
    session_expiry_max_timestamp = context.session.get("_session_init_timestamp_", 0)
    if session_expiry_max_timestamp:
        session_expiry_max_timestamp += settings.SESSION_EXPIRE_MAXIMUM_SECONDS
    session_expiry_timestamp = context.session.get("_session_current_timestamp_", 0)
    if session_expiry_timestamp:
        session_expiry_timestamp += settings.SESSION_EXPIRE_SECONDS

    user = getattr(context, "user", None)

    mercure_service = None
    subscriber_token = None
    try:
        mercure_service = MercureService()
    except MercureService.ConfigException:
        ...

    if mercure_service:
        subscriber_token = mercure_service.get_subscriber_token()

    # Add logic to calculate the count of unwatched release notes
    unwatched_count = 0
    if user and getattr(user, "is_authenticated", False):
        unwatched_count = ReleaseNote.count_unwatched(user)

    deploy_date_formatted = None
    if settings.DEPLOY_DATE:
        deploy_date = timezone.datetime.strptime(
            settings.DEPLOY_DATE, "%d-%m-%Y-%H-%M-%S"
        )
        deploy_date_formatted = deploy_date.strftime("%d-%m-%Y %H:%M:%S")

    instelling = Instelling.actieve_instelling()
    locatieservice = LocatieService(instelling=instelling)
    wijken_response = locatieservice.wijken()
    if wijken_response.get("error"):
        logger.warning(
            f"Er ging iets mis met het ophalen van wijken: {wijken_response}"
        )
    wijkcode_by_wijknaam = (
        {
            wijk.get("naam"): wijk.get("code")
            for wijk in wijken_response.get("results", [])
            if wijk.get("code") and wijk.get("naam")
        }
        if not wijken_response.get("error")
        else {}
    )

    ua = context.META.get("HTTP_USER_AGENT", "")
    device = DeviceDetector(ua).parse()

    profiel_taaktype_uuids = []
    if user and hasattr(user, "profiel"):
        profiel_taaktype_uuids = [
            str(uuid)
            for uuid in user.profiel.profiel_taaktypes.values_list("uuid", flat=True)
        ]

    return {
        "DEVICE_OS": device.os_name().lower(),
        "UI_SETTINGS": settings.UI_SETTINGS,
        "DEBUG": settings.DEBUG,
        "DEV_SOCKET_PORT": settings.DEV_SOCKET_PORT,
        "GET": context.GET,
        "ABSOLUTE_ROOT": absolute(context).get("ABSOLUTE_ROOT"),
        "SESSION_EXPIRY_MAX_TIMESTAMP": session_expiry_max_timestamp,
        "SESSION_EXPIRY_TIMESTAMP": session_expiry_timestamp,
        "SESSION_CHECK_INTERVAL_SECONDS": settings.SESSION_CHECK_INTERVAL_SECONDS,
        "APP_MERCURE_PUBLIC_URL": settings.APP_MERCURE_PUBLIC_URL,
        "GIT_SHA": settings.GIT_SHA,
        "MERCURE_SUBSCRIBER_TOKEN": subscriber_token,
        "UNWATCHED_COUNT": unwatched_count,
        "APP_ENV": settings.APP_ENV,
        "TAAKR_URL": instelling.taakr_basis_url,
        "WIJKCODE_BY_WIJKNAAM": wijkcode_by_wijknaam,
        "DEPLOY_DATE": deploy_date_formatted,
        "MOR_CORE_URL_PREFIX": settings.MOR_CORE_URL_PREFIX,
        "MOR_CORE_PROTECTED_URL_PREFIX": settings.MOR_CORE_PROTECTED_URL_PREFIX,
        "PROFIEL_TAAKTYPE_UUIDS": profiel_taaktype_uuids,
    }
