from django.conf import settings


def general_settings(request):
    return {
        "MELDINGEN_URL": settings.MELDINGEN_URL,
    }
