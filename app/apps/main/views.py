import json
import logging
from datetime import datetime

import requests
from apps.context.constanten import FILTERS
from apps.main.forms import (
    HANDLED_OPTIONS,
    TAAK_BEHANDEL_RESOLUTIE,
    TAAK_BEHANDEL_STATUS,
    TaakBehandelForm,
)
from apps.main.utils import (
    filter_taken,
    get_actieve_filters,
    get_actieve_filters_aantal,
    get_filter_options,
    get_filters,
    melding_naar_tijdlijn,
    set_actieve_filters,
    to_base64,
)
from apps.meldingen.service import MeldingenService
from apps.taken.models import Taak, Taaktype
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework.reverse import reverse as drf_reverse

logger = logging.getLogger(__name__)


def http_404(request):
    return render(
        request,
        "404.html",
    )


def http_500(request):
    return render(
        request,
        "500.html",
    )


def http_response(request):
    return HttpResponse("<h1>Hello HttpResponse</h1>")


def root(request):
    if request.user.has_perms(["authorisatie.taken_lijst_bekijken"]):
        return redirect(reverse("incident_index"))
    if request.user.has_perms(["authorisatie.beheer_bekijken"]):
        return redirect(reverse("beheer"))
    return redirect(reverse("account"))


@login_required
def account(request):
    return render(
        request,
        "auth/account.html",
        {},
    )


@login_required
def ui_settings_handler(request):
    profiel = request.user.profiel
    if request.POST:
        profiel.ui_instellingen.update(
            {"fontsize": request.POST.get("fontsize", "fz-medium")}
        )
        profiel.save()

    return render(
        request,
        "snippets/form_pageheader.html",
        {"profile": profiel},
    )


@permission_required("authorisatie.taken_lijst_bekijken")
def filter(request, status="nieuw"):
    filters = (
        get_filters(request.user.profiel.context)
        if request.user.profiel.context
        else []
    )
    actieve_filters = get_actieve_filters(request.user, filters, status)

    foldout_states = []
    if request.POST:
        actieve_filters = {f: request.POST.getlist(f) for f in filters}
        foldout_states = json.loads(request.POST.get("foldout_states", "[]"))

    try:
        standaard_taken = getattr(Taak.objects, f"get_taken_{status}")(request.user)
    except Exception as e:
        raise Exception(e)

    taken = filter_taken(standaard_taken, actieve_filters)

    filter_options_fields = [f for f in FILTERS if f[0] in actieve_filters]
    filter_opties = get_filter_options(taken, standaard_taken, filter_options_fields)

    actieve_filters = {
        k: [
            af
            for af in v
            if af in [fok for fok, fov in filter_opties.get(k, {}).items()]
        ]
        for k, v in actieve_filters.items()
    }

    # sla actieve filters op in profiel
    set_actieve_filters(request.user, actieve_filters, status)

    filters = [
        {
            "naam": f,
            "opties": filter_opties.get(f, {}),
            "actief": actieve_filters.get(f, {}),
            "folded": f"foldout_{f}" not in foldout_states,
        }
        for f in filters
    ]

    return render(
        request,
        "filters/form.html",
        {
            "filters": filters,
            "this_url": reverse("filter_part", kwargs={"status": status}),
            "actieve_filters_aantal": get_actieve_filters_aantal(actieve_filters),
            "taken_aantal": taken.count(),
            "foldout_states": json.dumps(foldout_states),
        },
    )


STREET_NAME = "streetName"
DAYS = "days"
SUBJECT = "subject"
STATUS = "status"
SPEED = "speed"

sort_function = {
    STREET_NAME: (
        lambda x: x.get("locatie", {}).get("adres", {}).get("straatNaam", ""),
        None,
        None,
    ),
    DAYS: (
        lambda x: x.get("werkdagenSindsRegistratie", 0),
        lambda x: datetime.strptime(
            x.get("datumMelding"), "%Y-%m-%dT%H:%M:%S"
        ).strftime("%Y%m01"),
        lambda x: datetime.strptime(x, "%Y%m01").strftime("%B %Y"),
    ),
    SUBJECT: (lambda x: x.get("onderwerp", {}).get("omschrijving", ""), None, None),
    STATUS: (lambda x: x.get("status", ""), None, None),
    SPEED: (
        lambda x: x.get("spoed", False),
        None,
        lambda x: "Spoed" if x else "Geen spoed",
    ),
}

sort_options = (
    (f"-{DAYS}", "Oud > nieuw"),
    (f"{DAYS}", "Nieuw > oud"),
    (f"{STREET_NAME}", "Straat (a-z)"),
    (f"-{STREET_NAME}", "Straat (z-a)"),
    (f"{SUBJECT}", "Onderwerp (a-z)"),
    (f"-{SUBJECT}", "Onderwerp (z-a)"),
    (f"{STATUS}", "Status (a-z)"),
    (f"-{STATUS}", "Status (z-a)"),
    (f"-{SPEED}", "Spoed"),
)


@permission_required("authorisatie.taken_lijst_bekijken")
def taken_overzicht(request):
    url_kwargs = {"status": "nieuw"}
    return render(
        request,
        "taken/taken_lijst.html",
        {
            "taken_lijst_url": reverse("taken_lijst_part", kwargs=url_kwargs),
            "filter_url": reverse("filter_part", kwargs=url_kwargs),
        },
    )


@permission_required("authorisatie.taken_lijst_bekijken")
def taken_afgerond_overzicht(request):
    url_kwargs = {"status": "voltooid"}
    return render(
        request,
        "taken/taken_lijst.html",
        {
            "taken_lijst_url": reverse(
                "taken_lijst_part",
                kwargs=url_kwargs,
            ),
            "filter_url": reverse(
                "filter_part",
                kwargs=url_kwargs,
            ),
        },
    )


@permission_required("authorisatie.taken_lijst_bekijken")
def taken_lijst(request, status="nieuw"):
    grouped_by = False

    try:
        taken = getattr(Taak.objects, f"get_taken_{status}")(request.user)
    except Exception as e:
        raise Exception(e)

    filters = (
        get_filters(request.user.profiel.context)
        if request.user.profiel.context
        else []
    )
    actieve_filters = get_actieve_filters(request.user, filters, status)
    taken_gefilterd = filter_taken(taken, actieve_filters)
    taken_aantal = len(taken_gefilterd)
    paginator = Paginator(taken_gefilterd, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # get css order numbers for adres of taak
    taken_sorted_by_adres = {
        id: i
        for i, id in enumerate(
            taken_gefilterd.order_by(
                "melding__response_json__locaties_voor_melding__straatnaam"
            ).values_list("id", flat=True)
        )
    }

    taken_paginated = page_obj.object_list
    return render(
        request,
        "incident/part_list.html"
        if not grouped_by
        else "incident/part_list_grouped.html",
        {
            "this_url": reverse("taken_lijst_part", kwargs={"status": status}),
            "sort_options": sort_options,
            "taken": taken_paginated,
            "taken_aantal": taken_aantal,
            "page_obj": page_obj,
            "filters_count": len([ll for k, v in actieve_filters.items() for ll in v]),
            "taken_sorted_by_adres": taken_sorted_by_adres,
        },
    )


@permission_required("authorisatie.taak_bekijken")
def taak_detail(request, id):
    taak = get_object_or_404(Taak, pk=id)
    melding_response = MeldingenService().get_by_uri(taak.melding.bron_url)
    melding = melding_response.json()
    tijdlijn_data = melding_naar_tijdlijn(melding)

    return render(
        request,
        "taken/taak_detail.html",
        {
            "id": id,
            "taak": taak,
            "melding": melding,
            "tijdlijn_data": tijdlijn_data,
        },
    )


@permission_required("authorisatie.taak_afronden")
def incident_modal_handle(request, id):
    resolutie = request.GET.get("resolutie", "opgelost")
    taak = get_object_or_404(Taak, pk=id)
    form = TaakBehandelForm(
        volgende_taaktypes=taak.taaktype.volgende_taaktypes.all().exclude(
            id=taak.taaktype.id
        ),
        initial={"resolutie": resolutie},
    )
    warnings = []
    errors = []
    messages = []
    form_submitted = False
    is_handled = False

    if request.POST:
        form = TaakBehandelForm(
            request.POST,
            volgende_taaktypes=taak.taaktype.volgende_taaktypes.all().exclude(
                id=taak.taaktype.id
            ),
            initial={"resolutie": resolutie},
        )
        if form.is_valid():
            bijlagen = request.FILES.getlist("bijlagen", [])
            taaktype = Taaktype.objects.filter(
                id=form.cleaned_data.get("nieuwe_taak")
            ).first()
            taaktype_url = (
                drf_reverse(
                    "v1:taaktype-detail",
                    kwargs={"uuid": taaktype.uuid},
                    request=request,
                )
                if taaktype
                else None
            )
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})
            taak_status_aanpassen_response = MeldingenService().taak_status_aanpassen(
                taakopdracht_url=taak.taakopdracht,
                status="voltooid",
                resolutie=form.cleaned_data.get("resolutie"),
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlagen=bijlagen_base64,
                gebruiker=request.user.email,
            )
            if taak_status_aanpassen_response.status_code != 200:
                logger.error(
                    f"taak_status_aanpassen: status code: {taak_status_aanpassen_response.status_code}, taak id: {id}"
                )
            if (
                taak_status_aanpassen_response.status_code == 200
                and taaktype_url
                and form.cleaned_data.get("nieuwe_taak_toevoegen")
            ):
                taak_aanmaken_response = MeldingenService().taak_aanmaken(
                    melding_uuid=taak.melding.response_json.get("uuid"),
                    taaktype_url=taaktype_url,
                    titel=taaktype.omschrijving,
                    bericht=form.cleaned_data.get("omschrijving_nieuwe_taak"),
                    gebruiker=request.user.email,
                )
                if taak_aanmaken_response.status_code != 200:
                    logger.error(
                        f"taak_aanmaken: status code: {taak_aanmaken_response.status_code}, taak id: {id}, text: {taak_aanmaken_response.text}"
                    )

            form.cleaned_data.get("handle_choice", 1)
            return redirect("incident_index")
    return render(
        request,
        "incident/modal_handle.html",
        {
            "taak": taak,
            "form": form,
            "form_submitted": form_submitted,
            "HANDLED_OPTIONS": HANDLED_OPTIONS,
            "parent_context": {
                "form_submitted": form_submitted,
                "errors": errors,
                "warnings": warnings,
                "messages": messages,
                "is_handled": is_handled,
            },
        },
    )


@login_required
def config(request):
    return render(
        request,
        "config.html",
    )


def meldingen_bestand(request):
    url = f"{settings.MELDINGEN_URL}{request.path}"
    headers = {"Authorization": f"Token {MeldingenService().haal_token()}"}
    response = requests.get(url, stream=True, headers=headers)
    return StreamingHttpResponse(
        response.raw,
        content_type=response.headers.get("content-type"),
        status=response.status_code,
        reason=response.reason,
    )
