import logging
from datetime import datetime

import requests
from apps.main.forms import (
    HANDLED_OPTIONS,
    TAAK_BEHANDEL_RESOLUTIE,
    TAAK_BEHANDEL_STATUS,
    TaakBehandelForm,
)
from apps.main.utils import filter_taken, get_filter_options, to_base64, melding_naar_tijdlijn
from apps.meldingen.service import MeldingenService
from apps.meldingen.utils import get_meldingen_token
from apps.taken.models import Taak
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.paginator import Paginator


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
    if request.user and request.user.is_authenticated:
        return redirect(reverse("incident_index"))
    return redirect(reverse("incident_index"))


@login_required
def ui_settings_handler(request):

    return render(
        request,
        "snippets/form_pageheader.html",
        {},
    )


@login_required
def filter(request, openstaand="openstaand"):
    taken = Taak.objects.filter(afgesloten_op__isnull=(openstaand == "openstaand"))
    form_url = (
        reverse("filter_part")
        if (openstaand == "openstaand")
        else reverse("filter_part", kwargs={"openstaand": "niet_openstaand"})
    )
    actieve_filters = {
        "locatie": [],
        "taken": [],
    }
    actieve_filters.update(request.session.get("actieve_filters", {}))

    if request.POST:
        actieve_filters["locatie"] = request.POST.getlist("locatie")
        actieve_filters["taken"] = request.POST.getlist("taken")

    taken_gefilterd = filter_taken(taken, actieve_filters)

    filter_options_fields = (
        (
            "locatie",
            "melding__response_json__locaties_voor_melding__0__begraafplaats",
            "melding__response_json__meta_uitgebreid__begraafplaats__choices",
        ),
        (
            "taken",
            "taaktype__id",
            "taaktype__omschrijving",
        ),
    )
    filter_opties = get_filter_options(taken_gefilterd, taken, filter_options_fields)
    actieve_filters = {
        k: [
            af
            for af in v
            if af in [fok for fok, fov in filter_opties.get(k, {}).items()]
        ]
        for k, v in actieve_filters.items()
    }

    request.session["actieve_filters"] = actieve_filters
    
    return render(
        request,
        "filters/form.html",
        {
            "filter_opties": filter_opties,
            "actieve_filters": actieve_filters,
            "filters_count": len([ll for k, v in actieve_filters.items() for ll in v]),
            "taken_gefilterd": taken_gefilterd,
            "form_url": form_url,
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


@login_required
def taken_overzicht(request):

    taken = Taak.objects.filter(afgesloten_op__isnull=True)
    actieve_filters = {
        "locatie": [],
        "taken": [],
    }
    actieve_filters.update(request.session.get("actieve_filters", {}))

    if request.POST:
        actieve_filters["locatie"] = request.POST.getlist("locatie")
        actieve_filters["taken"] = request.POST.getlist("taken")

    taken_gefilterd = filter_taken(taken, actieve_filters)

    filter_options_fields = (
        (
            "locatie",
            "melding__response_json__locaties_voor_melding__0__begraafplaats",
            "melding__response_json__meta_uitgebreid__begraafplaats__choices",
        ),
        (
            "taken",
            "taaktype__id",
            "taaktype__omschrijving",
        ),
    )
    filter_opties = get_filter_options(taken_gefilterd, taken, filter_options_fields)
    actieve_filters = {
        k: [
            af
            for af in v
            if af in [fok for fok, fov in filter_opties.get(k, {}).items()]
        ]
        for k, v in actieve_filters.items()
    }
    
    return render(
        request,
        "incident/index.html",
        {
            "filter_url": reverse("filter_part"),
            "filters_count": len([ll for k, v in actieve_filters.items() for ll in v]),
        },
    )


@login_required
def taken_afgerond_overzicht(request):
    return render(
        request,
        "incident/index_afgerond.html",
        {
            "filter_url": reverse(
                "filter_part", kwargs={"openstaand": "niet_openstaand"}
            ),
        },
    )


@login_required
def actieve_taken(request):
    grouped_by = False

    taken = Taak.objects.filter(afgesloten_op__isnull=True)

    actieve_filters = request.session.get("actieve_filters", {})
    taken_gefilterd = filter_taken(taken, actieve_filters)

    paginator = Paginator(taken_gefilterd, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    taken_paginated = page_obj.object_list
    return render(
        request,
        "incident/part_list.html"
        if not grouped_by
        else "incident/part_list_grouped.html",
        {
            
            "filter_url": reverse("filter_part"),
            "sort_options": sort_options,
            "taken": taken_paginated,
            "page_obj": page_obj,
            "filters_count": len([ll for k, v in actieve_filters.items() for ll in v]),
        },
    )

@login_required
def afgeronde_taken(request):
    grouped_by = False
    taken = Taak.objects.filter(afgesloten_op__isnull=False).order_by("-afgesloten_op")

    actieve_filters = request.session.get("actieve_filters", {})
    taken_gefilterd = filter_taken(taken, actieve_filters)

    paginator = Paginator(taken_gefilterd, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    taken_paginated = page_obj.object_list
    return render(
        request,
        "incident/part_list.html"
        if not grouped_by
        else "incident/part_list_grouped.html",
        {
            # "incidents": incidents_sorted,
            # "sort_by": sort_by_with_reverse,
            # "groups": groups,
            # "grouped_by": grouped_by,
            "sort_options": sort_options,
            "taken": taken_paginated,
            "page_obj": page_obj,
            "filters_count": len([ll for k, v in actieve_filters.items() for ll in v]),
        },
    )


@login_required
def taak_detail(request, id):
    taak = Taak.objects.get(pk=id)
    melding_response = MeldingenService().get_by_uri(taak.melding.bron_url)
    melding = melding_response.json()
    tijdlijn_data = melding_naar_tijdlijn(melding)

    return render(
        request,
        "incident/detail.html",
        {
            "id": id,
            "taak": taak,
            "melding": melding,
            "tijdlijn_data": tijdlijn_data,
        },
    )


@login_required
def incident_list_item(request, id):
    taak = Taak.objects.get(pk=id)
    return render(
        request,
        "incident/list_item.html",
        {
            "incident": taak,
        },
    )


@login_required
def incident_modal_handle(request, id, handled_type="handled"):
    taak = Taak.objects.get(pk=id)
    form = TaakBehandelForm()
    warnings = []
    errors = []
    messages = []
    form_submitted = False
    is_handled = False

    if request.POST:
        form = TaakBehandelForm(request.POST)
        if form.is_valid():
            bijlagen = request.FILES.getlist("bijlagen", [])
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})
            taak_status_aanpassen_response = MeldingenService().taak_status_aanpassen(
                taakopdracht_url=taak.taakopdracht,
                status=TAAK_BEHANDEL_STATUS.get(form.cleaned_data.get("status")),
                resolutie=TAAK_BEHANDEL_RESOLUTIE.get(form.cleaned_data.get("status")),
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlagen=bijlagen_base64,
                gebruiker=request.user.email,
            )
            if taak_status_aanpassen_response.status_code != 200:
                logger.error(
                    f"taak_status_aanpassen: status code: {taak_status_aanpassen_response.status_code}, taak id: {id}"
                )
            form.cleaned_data.get("handle_choice", 1)
            return redirect("incident_index")
    return render(
        request,
        "incident/modal_handle.html",
        {
            "taak": taak,
            "handled_type": handled_type,
            "form": form,
            "form_submitted": form_submitted,
            "HANDLED_OPTIONS": HANDLED_OPTIONS,
            "parent_context": {
                "form_submitted": form_submitted,
                "errors": errors,
                "warnings": warnings,
                "messages": messages,
                "handled_type": handled_type,
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
    headers = {"Authorization": f"Token {get_meldingen_token()}"}
    response = requests.get(url, stream=True, headers=headers)
    return StreamingHttpResponse(
        response.raw,
        content_type=response.headers.get("content-type"),
        status=response.status_code,
        reason=response.reason,
    )
