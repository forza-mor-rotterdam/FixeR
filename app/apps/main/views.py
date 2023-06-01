from datetime import datetime
from itertools import chain

import requests
from apps.main.forms import HANDLED_OPTIONS, HandleForm
from apps.main.utils import filter_taken, get_filter_options
from apps.meldingen.service import MeldingenService
from apps.meldingen.utils import get_meldingen_token
from apps.taken.models import Taak
from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse


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


def ui_settings_handler(request):

    return render(
        request,
        "snippets/form_pageheader.html",
        {},
    )


def filter(request):
    taken = Taak.objects.filter(afgesloten_op__isnull=True)

    actieve_filters = {
        "locatie": [],
        "taken": [],
    }
    actieve_filters.update(request.session.get("actieve_filters", {}))

    if request.POST:
        actieve_filters["locatie"] = list(chain(*request.POST.getlist("locatie")))
        actieve_filters["taken"] = [
            int(t) for t in list(chain(*request.POST.getlist("taken")))
        ]
        request.session["actieve_filters"] = actieve_filters

    taken_gefilterd = filter_taken(taken, actieve_filters)

    filter_options_fields = (
        (
            "begraafplaats",
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
    print(filter_opties)
    print(actieve_filters)
    return render(
        request,
        "filters/form.html",
        {
            "filter_opties": filter_opties,
            "actieve_filters": actieve_filters,
            "filters_count": len([ll for k, v in actieve_filters.items() for ll in v]),
            "taken_gefilterd": taken_gefilterd,
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


def taken_overzicht(request):

    return render(
        request,
        "incident/index.html",
        {},
    )


def actieve_taken(request):

    sort_by_with_reverse_session = request.session.get("sort_by", f"-{DAYS}")
    sort_by_with_reverse = request.GET.get("sort-by", sort_by_with_reverse_session)
    request.session["sort_by"] = sort_by_with_reverse

    sort_by = sort_by_with_reverse.lstrip("-")
    sort_reverse = (
        len(sort_by_with_reverse.split("-", 1)) > 1
        and sort_by_with_reverse.split("-", 1)[0] == ""
    )

    grouped_by_session = request.session.get("grouped_by", "false")

    grouped_by = request.GET.get("grouped-by", grouped_by_session)
    request.session["grouped_by"] = grouped_by
    grouped_by = grouped_by == "true"

    selected_order_option = sort_function.get(sort_by, sort_function[DAYS])[0]

    # get incidents if we have filters
    incidents = []
    incidents_sorted = []
    groups = []

    incidents = MeldingenService().get_melding_lijst().get("results", [])

    incidents_sorted = sorted(
        incidents, key=selected_order_option, reverse=sort_reverse
    )
    if grouped_by:
        groups = sorted(
            [
                *set(
                    [
                        sort_function[sort_by][1](i)
                        if sort_function[sort_by][1]
                        else sort_function[sort_by][0](i)
                        for i in incidents_sorted
                    ]
                )
            ]
        )

        groups = [
            {
                "title": sort_function[sort_by][2](g)
                if sort_function[sort_by][2]
                else g,
                "items": [
                    i
                    for i in incidents_sorted
                    if g
                    == (
                        sort_function[sort_by][1](i)
                        if sort_function[sort_by][1]
                        else sort_function[sort_by][0](i)
                    )
                ],
            }
            for g in groups
        ]
        if sort_reverse:
            groups.reverse()

    taken = Taak.objects.filter(afgesloten_op__isnull=True)

    actieve_filters = request.session.get("actieve_filters", {})
    taken_gefilterd = filter_taken(taken, actieve_filters)

    return render(
        request,
        "incident/part_list.html"
        if not grouped_by
        else "incident/part_list_grouped.html",
        {
            "incidents": incidents_sorted,
            "sort_by": sort_by_with_reverse,
            "sort_options": sort_options,
            "groups": groups,
            "grouped_by": grouped_by,
            "taken": taken_gefilterd,
        },
    )


def taak_detail(request, id):

    MeldingenService().get_melding(id)
    taak = Taak.objects.get(pk=id)

    return render(
        request,
        "incident/detail.html",
        {
            "id": id,
            "taak": taak,
        },
    )


def incident_list_item(request, id):
    taak = Taak.objects.get(pk=id)
    print(taak.melding)
    melding = MeldingenService().get_by_uri(taak.melding)

    return render(
        request,
        "incident/list_item.html",
        {
            "incident": taak,
            "melding": melding,
        },
    )


def incident_modal_handle(request, id, handled_type="handled"):
    taak = Taak.objects.get(pk=id)
    form = HandleForm(handled_type=handled_type)
    warnings = []
    errors = []
    messages = []
    form_submitted = False
    is_handled = False

    if request.POST:
        form = HandleForm(request.POST, handled_type=handled_type)
        if form.is_valid():
            form.cleaned_data.get("handle_choice", 1)

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


def incident_mutation_lines(request, id):

    return render(
        request,
        "incident/mutation_lines.html",
        {
            "id": id,
        },
    )


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
