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
        first_name_initial = (
            gebruiker.get("first_name", "@")[0]
            if gebruiker.get("first_name", "@")
            else "@"
        )
        # last_name_initial = gebruiker.get("last_name", "*")[0]
        full_initials = f"{first_name_initial}".strip()
    elif hasattr(gebruiker, "first_name") or hasattr(gebruiker, "last_name"):
        first_name_initial = gebruiker.first_name[0] if gebruiker.first_name else "@"
        # last_name_initial = gebruiker.last_name[0] if gebruiker.last_name else "*"
        full_initials = f"{first_name_initial}".strip()
    return full_initials


def truncate_tekst(text, length=200):
    if len(text) > length:
        return f"{text[:length]}..."
    return text
