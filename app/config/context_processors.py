import logging

import jwt
from django.conf import settings
from django.urls import reverse
from utils.diversen import absolute

logger = logging.getLogger(__name__)


def general_settings(context):
    oidc_id_token = context.session.get("oidc_id_token")
    token_decoded = {}
    try:
        token_decoded = jwt.decode(oidc_id_token, options={"verify_signature": False})
    except Exception:
        logger.error("oidc_id_token is niet valide")

    return {
        "MELDINGEN_URL": settings.MELDINGEN_URL,
        "DEBUG": settings.DEBUG,
        "DEV_SOCKET_PORT": settings.DEV_SOCKET_PORT,
        "CHECK_SESSION_IFRAME": settings.CHECK_SESSION_IFRAME,
        "GET": context.GET,
        "ABSOLUTE_ROOT": absolute(context).get("ABSOLUTE_ROOT"),
        "OIDC_RP_CLIENT_ID": settings.OIDC_RP_CLIENT_ID,
        "SESSION_STATE": token_decoded.get("session_state"),
        "LOGOUT_URL": reverse("oidc_logout"),
        "LOGIN_URL": f"{reverse('oidc_authentication_init')}?next={absolute(context).get('FULL_URL')}",
    }
