import json
import logging

import requests
from apps.authenticatie.models import Gebruiker
from apps.context.filters import FilterManager
from apps.main.forms import (
    KaartModusForm,
    SorteerFilterForm,
    TaakBehandelForm,
    TaakToewijzenForm,
    TaakToewijzingIntrekkenForm,
)
from apps.main.utils import (
    get_actieve_filters,
    get_filters,
    get_kaart_modus,
    get_sortering,
    melding_naar_tijdlijn,
    set_actieve_filters,
    set_kaart_modus,
    set_sortering,
    to_base64,
)
from apps.meldingen.service import MeldingenService
from apps.release_notes.models import ReleaseNote
from apps.taken.models import Taak, Taakstatus, Taaktype
from device_detector import DeviceDetector
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Value
from django.db.models.functions import Concat
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import View
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


def informatie(request):
    return render(
        request,
        "auth/informatie.html",
        {},
    )


# Verander hier de instellingen voor de nieuwe homepagina.
@login_required
def root(request):
    if request.user.has_perms(["authorisatie.taken_lijst_bekijken"]):
        return redirect(reverse("incident_index"), False)
    if request.user.has_perms(["authorisatie.beheer_bekijken"]):
        return redirect(reverse("beheer"), False)
    return render(
        request,
        "home.html",
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


@login_required
@permission_required("authorisatie.taken_lijst_bekijken", raise_exception=True)
def filter(request, status="nieuw"):
    filters = (
        get_filters(request.user.profiel.context)
        if request.user.profiel.context
        else []
    )
    # haal actieve filters op uit profiel
    actieve_filters = get_actieve_filters(request.user, filters, status)

    foldout_states = []
    request_type = "get"
    if request.POST:
        request_type = "post"
        actieve_filters = {f: request.POST.getlist(f) for f in filters}
        foldout_states = json.loads(request.POST.get("foldout_states", "[]"))

    taken = Taak.objects.get_taken_recent(request.user)

    filter_manager = FilterManager(taken, actieve_filters, foldout_states)

    taken_gefilterd = filter_manager.filter_taken()

    # sla actieve filters op in profiel
    set_actieve_filters(request.user, filter_manager.active_filters, status)

    return render(
        request,
        "filters/form.html",
        {
            "filter_manager": filter_manager,
            "this_url": reverse("filter_part", kwargs={"status": status}),
            "taken_aantal": taken_gefilterd.count(),
            "foldout_states": json.dumps(foldout_states),
            "request_type": request_type,
        },
    )


@login_required
@permission_required("authorisatie.taken_lijst_bekijken", raise_exception=True)
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


@login_required
@permission_required("authorisatie.taken_lijst_bekijken", raise_exception=True)
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


@login_required
@permission_required("authorisatie.taken_lijst_bekijken", raise_exception=True)
def taken_lijst(request, status="nieuw"):
    taken = Taak.objects.get_taken_recent(request.user)

    filters = (
        get_filters(request.user.profiel.context)
        if request.user.profiel.context
        else []
    )

    actieve_filters = get_actieve_filters(request.user, filters, status)

    filter_manager = FilterManager(taken, actieve_filters)

    taken_gefilterd = filter_manager.filter_taken()

    taken_aantal = len(taken_gefilterd)
    paginator = Paginator(taken_gefilterd, 500)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # get css order numbers for adres of taak
    taken_sorted_by_adres = {
        id: i
        for i, id in enumerate(
            taken_gefilterd.annotate(
                adres=Concat(
                    "melding__response_json__locaties_voor_melding__0__straatnaam",
                    Value(" "),
                    "melding__response_json__locaties_voor_melding__0__huisnummer",
                    output_field=models.CharField(),
                )
            )
            .order_by("adres")
            .values_list("id", flat=True)
        )
    }

    taken_paginated = page_obj.object_list
    return render(
        request,
        "incident/part_list_base.html",
        {
            "this_url": reverse("taken_lijst_part", kwargs={"status": status}),
            "taken": taken_paginated,
            "taken_aantal": taken_aantal,
            "page_obj": page_obj,
            "filter_manager": filter_manager,
            "taken_sorted_by_adres": taken_sorted_by_adres,
        },
    )


@login_required
def sorteer_filter(request):
    sortering = get_sortering(request.user)
    form = SorteerFilterForm({"sorteer_opties": sortering})

    if request.POST:
        form = SorteerFilterForm(request.POST)
        if form.is_valid():
            sortering = form.cleaned_data.get("sorteer_opties")
            set_sortering(request.user, sortering)
    return render(
        request,
        "snippets/sorteer_filter_form.html",
        {"form": form},
    )


@login_required
def kaart_modus(request):
    kaart_modus = get_kaart_modus(request.user)
    form = KaartModusForm({"kaart_modus": kaart_modus})
    request_type = "get"
    if request.POST:
        request_type = "post"
        form = KaartModusForm(request.POST, {"kaart_modus": kaart_modus})
        if form.is_valid():
            kaart_modus = form.cleaned_data.get("kaart_modus")
            set_kaart_modus(request.user, kaart_modus)
    return render(
        request,
        "snippets/kaart_modus_form.html",
        {
            "form": form,
            "request_type": request_type,
        },
    )


@login_required
@permission_required("authorisatie.taak_bekijken", raise_exception=True)
def taak_detail(request, id):
    taak = get_object_or_404(Taak, pk=id)
    melding_response = MeldingenService().get_by_uri(taak.melding.bron_url)
    melding = melding_response.json()
    tijdlijn_data = melding_naar_tijdlijn(melding)
    ua = request.META.get("HTTP_USER_AGENT")
    device = DeviceDetector(ua).parse()
    return render(
        request,
        "taken/taak_detail.html",
        {
            "id": id,
            "taak": taak,
            "melding": melding,
            "tijdlijn_data": tijdlijn_data,
            "device_os": device.os_name().lower(),
        },
    )


@login_required
@permission_required("authorisatie.taak_toewijzen", raise_exception=True)
def taak_toewijzen(request, id):
    taak = get_object_or_404(Taak, pk=id)
    valide_gebruikers = Gebruiker.objects.taak_toewijzen_gebruikers()
    form = TaakToewijzenForm(gebruikers=valide_gebruikers)
    if request.POST:
        form = TaakToewijzenForm(request.POST, gebruikers=valide_gebruikers)
        if form.is_valid():
            taak_status_aanpassen_response = MeldingenService().taak_status_aanpassen(
                taakopdracht_url=taak.taakopdracht,
                status="toegewezen",
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
                uitvoerder=form.cleaned_data.get("uitvoerder"),
            )
            if taak_status_aanpassen_response.status_code == 200:
                return render(
                    request,
                    "taken/taak_toewijzen.html",
                    {
                        "taak": taak,
                    },
                )

    return render(
        request,
        "taken/taak_toewijzen.html",
        {
            "form": form,
            "taak": taak,
        },
    )


@login_required
@permission_required("authorisatie.taak_toewijzing_intrekken", raise_exception=True)
def taak_toewijzing_intrekken(request, id):
    taak = get_object_or_404(Taak, pk=id)
    form = TaakToewijzingIntrekkenForm()
    if request.POST:
        form = TaakToewijzingIntrekkenForm(request.POST)
        if form.is_valid():
            taak_status_aanpassen_response = MeldingenService().taak_status_aanpassen(
                taakopdracht_url=taak.taakopdracht,
                status="openstaand",
                gebruiker=request.user.email,
            )
            if taak_status_aanpassen_response.status_code == 200:
                return render(
                    request,
                    "taken/taak_toewijzing_intrekken.html",
                    {
                        "taak": taak,
                    },
                )

    return render(
        request,
        "taken/taak_toewijzing_intrekken.html",
        {
            "form": form,
            "taak": taak,
        },
    )


@login_required
@permission_required("authorisatie.taak_afronden", raise_exception=True)
def incident_modal_handle(request, id):
    context = request.user.profiel.context
    resolutie = request.GET.get("resolutie", "opgelost")
    taak = get_object_or_404(Taak, pk=id)
    if taak.taakstatus.naam == Taakstatus.NaamOpties.VOLTOOID:
        # Voorkom het voltooien van een taak die reeds voltooid is.
        return http_404(request)

    # Alle taken voor deze melding
    openstaande_taken_voor_melding = Taak.objects.filter(
        melding__response_json__id=taak.melding.response_json.get("id"),
        taakstatus__naam__in=Taakstatus.niet_voltooid_statussen(),
    )

    # Alle taaktype ids voor deze melding
    openstaande_taaktype_ids_voor_melding = list(
        {
            taaktype_id
            for taaktype_id in openstaande_taken_voor_melding.values_list(
                "taaktype__id", flat=True
            )
            .order_by("taaktype__id")
            .distinct()
        }
    )

    # Exclude alle taaktype ids voor vervolgtaken
    volgende_taaktypes = taak.taaktype.volgende_taaktypes.all().exclude(
        id__in=openstaande_taaktype_ids_voor_melding
    )

    form = TaakBehandelForm(
        volgende_taaktypes=volgende_taaktypes,
        initial={"resolutie": resolutie},
    )

    # Alle andere actieve /openstaande taken voor deze melding
    actieve_vervolg_taken = openstaande_taken_voor_melding.filter(
        taaktype__in=context.taaktypes.all(),
    ).exclude(
        id=taak.id,
    )

    if request.POST:
        form = TaakBehandelForm(
            request.POST,
            volgende_taaktypes=volgende_taaktypes,
            initial={"resolutie": resolutie},
        )
        if form.is_valid():
            # Afhandelen bijlagen
            bijlagen = request.FILES.getlist("bijlagen", [])
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})

            # Taak status aanpassen
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

            # Aanmaken extra taken
            if (
                taak_status_aanpassen_response.status_code == 200
                and form.cleaned_data.get("nieuwe_taak")
            ):
                taken = form.cleaned_data.get("nieuwe_taak", [])
                for vervolg_taak in taken:
                    taaktype = Taaktype.objects.filter(id=vervolg_taak).first()
                    taaktype_url = (
                        drf_reverse(
                            "v1:taaktype-detail",
                            kwargs={"uuid": taaktype.uuid},
                            request=request,
                        )
                        if taaktype
                        else None
                    )

                    if taaktype_url:
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

            return redirect("incident_index")

    return render(
        request,
        "incident/modal_handle.html",
        {
            "taak": taak,
            "form": form,
            "actieve_vervolg_taken": actieve_vervolg_taken,
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


class HomepageView(PermissionRequiredMixin, View):
    # Might change to LoginRequiredMixin
    permission_required = "authorisatie.homepage_bekijken"
    template_name = "homepage_nieuw.html"

    def get(self, request, *args, **kwargs):
        request.session["origine"] = "home"
        release_notes = self.get_release_notes()
        context = {
            "release_notes": release_notes,
        }
        return render(request, self.template_name, context)

    def get_release_notes(self):
        five_weeks_ago = timezone.now() - timezone.timedelta(weeks=5)

        release_notes = ReleaseNote.objects.filter(
            publicatie_datum__gte=five_weeks_ago
        ).order_by("-publicatie_datum")[:6]

        return release_notes
