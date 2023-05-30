from django.conf import settings


def general_settings(request):
    return {
        "DEBUG": settings.DEBUG,
        "MELDINGEN_URL": settings.MELDINGEN_URL,
        "DEV_SOCKET_PORT": settings.DEV_SOCKET_PORT,
    }
