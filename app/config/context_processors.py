import logging

from apps.release_notes.models import ReleaseNote
from apps.services.mercure import MercureService
from django.conf import settings
from django.urls import reverse
from utils.diversen import absolute

logger = logging.getLogger(__name__)


def general_settings(context):
    session_expiry_max_timestamp = context.session.get("_session_init_timestamp_", 0)
    if session_expiry_max_timestamp:
        session_expiry_max_timestamp += settings.SESSION_EXPIRE_MAXIMUM_SECONDS
    session_expiry_timestamp = context.session.get("_session_current_timestamp_", 0)
    if session_expiry_timestamp:
        session_expiry_timestamp += settings.SESSION_EXPIRE_SECONDS

    template_basis = None
    if (
        hasattr(context, "user")
        and hasattr(context.user, "profiel")
        and hasattr(context.user.profiel, "context")
        and hasattr(context.user.profiel.context, "template")
    ):
        template_basis = context.user.profiel.context.template

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
    if hasattr(context, "user") and context.user.is_authenticated:
        unwatched_count = ReleaseNote.count_unwatched(context.user)

    return {
        "MELDINGEN_URL": settings.MELDINGEN_URL,
        "UI_SETTINGS": settings.UI_SETTINGS,
        "DEBUG": settings.DEBUG,
        "DEV_SOCKET_PORT": settings.DEV_SOCKET_PORT,
        "GET": context.GET,
        "ABSOLUTE_ROOT": absolute(context).get("ABSOLUTE_ROOT"),
        "SESSION_EXPIRY_MAX_TIMESTAMP": session_expiry_max_timestamp,
        "SESSION_EXPIRY_TIMESTAMP": session_expiry_timestamp,
        "SESSION_CHECK_INTERVAL_SECONDS": settings.SESSION_CHECK_INTERVAL_SECONDS,
        "LOGOUT_URL": reverse("oidc_logout"),
        "LOGIN_URL": f"{reverse('oidc_authentication_init')}?next={absolute(context).get('FULL_URL')}",
        "TEMPLATE_BASIS": template_basis,
        "APP_MERCURE_PUBLIC_URL": settings.APP_MERCURE_PUBLIC_URL,
        "GIT_SHA": settings.GIT_SHA,
        "MERCURE_SUBSCRIBER_TOKEN": subscriber_token,
        "UNWATCHED_COUNT": unwatched_count,
        "APP_ENV": settings.APP_ENV,
    }
