def absolute(request):
    urls = {
        "ABSOLUTE_ROOT": request.build_absolute_uri("/")[:-1].strip("/"),
        "FULL_URL_WITH_QUERY_STRING": request.build_absolute_uri(),
        "FULL_URL": request.build_absolute_uri("?"),
    }

    return urls


def gebruikersnaam(gebruiker):
    naam_volledig = gebruiker_naam_volledig(gebruiker)
    if naam_volledig:
        return naam_volledig
    return (
        gebruiker.get("email", "@") if isinstance(gebruiker, dict) else gebruiker.email
    )


def gebruiker_is_anoniem(gebruiker):
    if not gebruiker:
        return True
    if isinstance(gebruiker, dict):
        return not [v for v in gebruiker.values() if v and "anoniem" not in v.lower()]
    return False


def gebruiker_voornaam_achternaam(gebruiker):
    name = ""
    if isinstance(gebruiker, dict):
        name = (gebruiker.get("naam", "") or "").strip()
        name_parts = name.split()
        first = next(
            iter(
                [
                    v
                    for k, v in gebruiker.items()
                    if v and k in ["first_name", "voornaam"]
                ]
            ),
            "",
        )
        last = next(
            iter(
                [
                    v
                    for k, v in gebruiker.items()
                    if v and k in ["last_name", "achternaam"]
                ]
            ),
            "",
        )
        if not first and len(name_parts) > 1:
            first = name_parts[0]
        if not last and len(name_parts) > 1:
            last = name_parts[-1]
    else:
        first = getattr(gebruiker, "first_name", "") or ""
        last = getattr(gebruiker, "last_name", "") or ""
    return first, last, name


def gebruiker_naam_volledig(gebruiker):
    is_anoniem = gebruiker_is_anoniem(gebruiker)
    if is_anoniem:
        return "Anoniem"
    voornaam, achternaam, naam = gebruiker_voornaam_achternaam(gebruiker)
    if naam:
        return naam
    return f"{voornaam.capitalize()} {achternaam.capitalize()}".strip()


def gebruikersinitialen(gebruiker):
    is_anoniem = gebruiker_is_anoniem(gebruiker)
    if is_anoniem:
        return "--"

    voornaam, achternaam, naam = gebruiker_voornaam_achternaam(gebruiker)
    voornaam = voornaam.split()[-1] if voornaam else voornaam
    achternaam = achternaam.split()[-1] if achternaam else achternaam

    if naam and not voornaam and not achternaam:
        return naam[0]
    if not voornaam and not achternaam:
        return "@"
    if not voornaam and achternaam:
        return achternaam[0]
    if voornaam and not achternaam:
        return voornaam[0]
    return f"{voornaam[0]}{achternaam[0]}".strip()


def truncate_tekst(text, length=200):
    if len(text) > length:
        return f"{text[:length]}..."
    return text
