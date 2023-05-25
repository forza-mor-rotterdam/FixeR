from datetime import datetime

import requests
from apps.main.forms import HANDLED_OPTIONS, HandleForm
from apps.meldingen.service import MeldingenService
from apps.meldingen.utils import get_meldingen_token
from apps.taken.models import Taak
from django.conf import settings
from django.core.cache import cache
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

    return render(
        request,
        "filters/form.html",
        {},
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


def incident_list_page(request):

    return render(
        request,
        "incident/index.html",
        {},
    )


def incident_list(request):

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
    print(incidents)
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

    # temp: spoed key only available in list items, set cache for it
    for i in incidents_sorted:
        cache_key = f"incident_{i.get('id')}_list_item"
        cache.set(cache_key, i, 60 * 60 * 24)

    print(grouped_by)
    print(incidents_sorted)
    return render(
        request,
        "incident/part_list.html"
        if not grouped_by
        else "incident/part_list_grouped.html",
        {
            "incidents": incidents_sorted,
            "filters": [],
            "sort_by": sort_by_with_reverse,
            "sort_options": sort_options,
            "groups": groups,
            "grouped_by": grouped_by,
            "taken": Taak.objects.all(),
        },
    )


def incident_detail(request, id):

    incident = MeldingenService().get_melding(id)

    return render(
        request,
        "incident/detail.html",
        {
            "id": id,
            "incident": incident,
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
