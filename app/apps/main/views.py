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
from apps.taken.models import Taak
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

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
    # request.user.token
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
def filter(request, openstaand="openstaand"):
    taaktypes = (
        request.user.profiel.context.taaktypes.all()
        if request.user.profiel.context
        else []
    )
    filters = (
        get_filters(request.user.profiel.context)
        if request.user.profiel.context
        else []
    )
    actieve_filters = get_actieve_filters(request.user, filters)

    foldout_states = []
    if request.POST:
        actieve_filters = {f: request.POST.getlist(f) for f in filters}
        foldout_states = json.loads(request.POST.get("foldout_states", "[]"))

    form_url = (
        reverse("filter_part")
        if (openstaand == "openstaand")
        else reverse("filter_part", kwargs={"openstaand": "niet_openstaand"})
    )

    taken = Taak.objects.filter(
        afgesloten_op__isnull=(openstaand == "openstaand"),
        taaktype__in=taaktypes,
    )
    taken = filter_taken(taken, actieve_filters)

    filter_options_fields = [f for f in FILTERS if f[0] in actieve_filters]
    filter_opties = get_filter_options(taken, taken, filter_options_fields)

    actieve_filters = {
        k: [
            af
            for af in v
            if af in [fok for fok, fov in filter_opties.get(k, {}).items()]
        ]
        for k, v in actieve_filters.items()
    }

    # sla actieve filters op in profiel
    set_actieve_filters(request.user, actieve_filters)

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
            "actieve_filters_aantal": get_actieve_filters_aantal(actieve_filters),
            "taken_aantal": taken.count(),
            "foldout_states": json.dumps(foldout_states),
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


@permission_required("authorisatie.taken_lijst_bekijken")
def taken_overzicht(request):
    return render(
        request,
        "incident/index.html",
    )


@permission_required("authorisatie.taken_lijst_bekijken")
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


@permission_required("authorisatie.taken_lijst_bekijken")
def actieve_taken(request):
    grouped_by = False

    taaktypes = (
        request.user.profiel.context.taaktypes.all()
        if request.user.profiel.context
        else []
    )
    taken = Taak.objects.filter(
        afgesloten_op__isnull=True,
        taaktype__in=taaktypes,
    )
    filters = (
        get_filters(request.user.profiel.context)
        if request.user.profiel.context
        else []
    )
    actieve_filters = get_actieve_filters(request.user, filters)
    taken_gefilterd = filter_taken(taken, actieve_filters)

    paginator = Paginator(taken_gefilterd, 50)
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
            "taken_totaal": taken,
            "page_obj": page_obj,
            "filters_count": len([ll for k, v in actieve_filters.items() for ll in v]),
        },
    )


@permission_required("authorisatie.taken_lijst_bekijken")
def afgeronde_taken(request):
    grouped_by = False
    taaktypes = (
        request.user.profiel.context.taaktypes.all()
        if request.user.profiel.context
        else []
    )
    taken = Taak.objects.filter(
        afgesloten_op__isnull=False,
        taaktype__in=taaktypes,
        resolutie__in=[
            Taak.ResolutieOpties.NIET_OPGELOST,
            Taak.ResolutieOpties.OPGELOST,
        ],
    ).order_by("-afgesloten_op")

    filters = (
        get_filters(request.user.profiel.context)
        if request.user.profiel.context
        else []
    )
    actieve_filters = get_actieve_filters(request.user, filters)
    taken_gefilterd = filter_taken(taken, actieve_filters)

    paginator = Paginator(taken_gefilterd, 50)
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
            "taken_totaal": taken,
            "filters_count": len([ll for k, v in actieve_filters.items() for ll in v]),
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
        "incident/detail.html",
        {
            "id": id,
            "taak": taak,
            "melding": melding,
            "tijdlijn_data": tijdlijn_data,
        },
    )


@permission_required("authorisatie.taak_bekijken")
def incident_list_item(request, id):
    taak = get_object_or_404(Taak, pk=id)
    return render(
        request,
        "incident/list_item.html",
        {
            "incident": taak,
        },
    )


@permission_required("authorisatie.taak_afronden")
def incident_modal_handle(request, id, handled_type="handled"):
    taak = get_object_or_404(Taak, pk=id)
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
    headers = {"Authorization": f"Token {MeldingenService().haal_token()}"}
    response = requests.get(url, stream=True, headers=headers)
    return StreamingHttpResponse(
        response.raw,
        content_type=response.headers.get("content-type"),
        status=response.status_code,
        reason=response.reason,
    )
