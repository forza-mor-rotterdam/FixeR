def absolute(request):
    urls = {
        "ABSOLUTE_ROOT": request.build_absolute_uri("/")[:-1].strip("/"),
        "FULL_URL_WITH_QUERY_STRING": request.build_absolute_uri(),
        "FULL_URL": request.build_absolute_uri("?"),
    }

    return urls


def gebruikersnaam(gebruiker):
    if gebruiker.first_name or gebruiker.last_name:
        first_name = gebruiker.first_name if gebruiker.first_name else ""
        last_name = gebruiker.last_name if gebruiker.last_name else ""
        return f"{first_name} {last_name}".strip()
    return gebruiker.email


def gebruikersinitialen(gebruiker):
    full_initials = "@"
    if isinstance(gebruiker, dict):
        first = gebruiker.get("first_name") or ""
        last = gebruiker.get("last_name") or ""
    else:
        first = getattr(gebruiker, "first_name", "") or ""
        last = getattr(gebruiker, "last_name", "") or ""

    first_initial = first[0] if first else "@"
    last_initial = last[0] if last else ""
    full_initials = f"{first_initial}{last_initial}".strip()

    return full_initials


def truncate_tekst(text, length=200):
    if len(text) > length:
        return f"{text[:length]}..."
    return text
