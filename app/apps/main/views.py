import json
import logging
import os
from datetime import datetime

import requests
from apps.context.filters import FilterManager
from apps.instellingen.models import Instelling
from apps.main.forms import (
    KaartModusForm,
    SorteerFilterForm,
    TaakBehandelForm,
    TakenLijstFilterForm,
)
from apps.main.mixins import StreamViewMixin
from apps.main.services import MORCoreService, PDOKService, TaakRService
from apps.main.utils import (
    get_actieve_filters,
    get_filters,
    get_kaart_modus,
    get_sortering,
    melding_naar_tijdlijn,
    set_actieve_filters,
    set_kaart_modus,
    set_sortering,
)
from apps.release_notes.models import ReleaseNote
from apps.taken.models import Taak, TaakDeellink, Taakstatus
from device_detector import DeviceDetector
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.core import signing
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import FormView, ListView, View

logger = logging.getLogger(__name__)


@login_required
def wijken_en_buurten(request):
    service = PDOKService()
    response = service.get_buurten_middels_gemeentecode()
    return JsonResponse(response)


def http_403(request):
    return render(
        request,
        "403.html",
    )


def http_404(request):
    current_time = datetime.now()
    server_id = os.getenv("APP_ENV", "Onbekend")

    return render(
        request,
        "404.html",
        {
            "current_time": current_time,
            "server_id": server_id,
            "user_agent": request.META.get("HTTP_USER_AGENT", "Onbekend"),
            "path": request.build_absolute_uri(request.path),
        },
    )


def http_410(request):
    return render(
        request,
        "410.html",
    )


def http_500(request):
    current_time = datetime.now()
    server_id = os.getenv("APP_ENV", "Onbekend")

    return render(
        request,
        "500.html",
        {
            "current_time": current_time,
            "server_id": server_id,
            "user_agent": request.META.get("HTTP_USER_AGENT", "Onbekend"),
            "path": request.build_absolute_uri(request.path),
        },
    )


def navigeer(request, lat, long):
    ua = request.META.get("HTTP_USER_AGENT", "")
    device = DeviceDetector(ua).parse()
    return render(
        request,
        "taken/navigeer.html",
        {
            "lat": lat,
            "long": long,
            "device_os": device.os_name().lower(),
        },
    )


# Verander hier de instellingen voor de nieuwe homepagina.
# @login_required
def root(request):
    if request.user.has_perms(["authorisatie.taken_lijst_bekijken"]):
        return redirect(reverse("taken"), False)
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
def taken(request):
    gebruiker = request.user
    if (
        not gebruiker.profiel.onboarding_compleet
        or gebruiker.profiel.wijken_or_taaktypes_empty
    ) and gebruiker.profiel.context.template != "benc":  # Skip onboarding if B&C
        return redirect(reverse("onboarding"), False)
    MORCoreService().set_gebruiker(gebruiker=gebruiker.serialized_instance())

    return render(request, "taken/taken.html", {})


class TakenOverzicht(
    PermissionRequiredMixin,
    StreamViewMixin,
    ListView,
    FormView,
):
    template_name = "taken/overzicht/basis.html"
    permission_required = "authorisatie.taken_lijst_bekijken"
    queryset = Taak.objects.taken_lijst()
    form_class = TakenLijstFilterForm
    paginate_by = 50

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "profiel": self.profiel,
            }
        )
        return kwargs

    def get_context_data(self, **kwargs):
        profiel_selected_filter_opties = {}

        if self.request.GET.get("toon_alle_taken"):
            self.request.session["toon_alle_taken"] = True

        try:
            profiel_selected_filter_opties = self.request.user.profiel.filters.get(
                "nieuw", {}
            )
            self.profiel = self.request.user.profiel
        except Exception:
            logger.warning(
                f"Er ging iets mis met het ophalen van de geselecteerde opties uit het profiel van de gebruiker: gebruiker={self.request.user.email}"
            )

        self.initial = {
            f: profiel_selected_filter_opties[f]
            for f in self.actieve_filters
            if profiel_selected_filter_opties.get(f)
        }

        kwargs = super().get_context_data(**kwargs)

        return kwargs

    def form_invalid(self, form):
        logger.error("TakenLijst: FORM INVALID")
        logger.error(form.errors.as_json())
        return super().form_invalid(form)

    def form_valid(self, form):
        print(form.cleaned_data)

        context = self.get_context_data(kwargs={})

        context.pop("form", None)
        return render(
            self.request,
            "taken/overzicht/basis_stream.html",
            context=context,
        )


@login_required
@permission_required("authorisatie.taken_lijst_bekijken", raise_exception=True)
def taken_filter(request):
    taken = Taak.objects.taken_lijst()

    filters = (
        get_filters(request.user.profiel.context)
        if request.user.profiel.context
        else []
    )
    actieve_filters = get_actieve_filters(request.user, filters)
    foldout_states = []

    if request.POST:
        request.session["toon_alle_taken"] = True
        request_filters = {f: request.POST.getlist(f) for f in filters}
        foldout_states = json.loads(request.POST.get("foldout_states", "[]"))
        for filter_name, new_value in request_filters.items():
            if new_value != actieve_filters.get(filter_name):
                actieve_filters[filter_name] = new_value
        set_actieve_filters(request.user, actieve_filters)

    filter_manager = FilterManager(
        taken, actieve_filters, foldout_states, profiel=request.user.profiel
    )
    taken_gefilterd = filter_manager.filter_taken()
    taken_gefilterd = taken_gefilterd.taken_zoeken(request.session.get("q"))

    taken_aantal = taken_gefilterd.count()
    return render(
        request,
        "taken/taken_filter_form.html",
        {
            "taken_aantal": taken_aantal,
            "filter_manager": filter_manager,
            "foldout_states": json.dumps(foldout_states),
        },
    )


@login_required
@permission_required("authorisatie.taken_lijst_bekijken", raise_exception=True)
def taken_lijst(request):
    try:
        pnt = Point(
            float(request.GET.get("lon", 0)),
            float(request.GET.get("lat", 0)),
            srid=4326,
        )
    except Exception:
        pnt = Point(0, 0, srid=4326)

    if request.GET.get("toon_alle_taken"):
        request.session["toon_alle_taken"] = True

    sortering = get_sortering(request.user)
    sort_reverse = len(sortering.split("-")) > 1
    sortering = sortering.split("-")[0]
    sorting_fields = {
        "Postcode": "melding__postcode",
        "Adres": "melding__locatie_verbose",
        "Datum": "taakstatus__aangemaakt_op",
        "Afstand": "afstand",
    }
    taken = Taak.objects.taken_lijst()
    filters = (
        get_filters(request.user.profiel.context)
        if request.user.profiel.context
        else []
    )
    actieve_filters = get_actieve_filters(request.user, filters)
    filter_manager = FilterManager(taken, actieve_filters, profiel=request.user.profiel)
    taken_gefilterd = filter_manager.filter_taken()

    taken_gefilterd = taken_gefilterd.taken_zoeken(request.session.get("q"))

    if sortering == "Afstand":
        taken_gefilterd = taken_gefilterd.annotate(
            afstand=Distance("melding__geometrie", pnt)
        )
    taken_gefilterd = taken_gefilterd.order_by(
        f"{'-' if sort_reverse else ''}{sorting_fields.get(sortering)}"
    )

    # paginate
    # @Remco @TODO Set to 5 for easier testing
    paginator = Paginator(taken_gefilterd, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    taken_paginated = page_obj.object_list
    taken_gefilterd_total = taken_gefilterd.count()
    if request.session.get("taken_gefilterd"):
        del request.session["taken_gefilterd"]

    return render(
        request,
        "taken/taken_lijst.html",
        {
            "taken_gefilterd_total": taken_gefilterd_total,
            "taken": taken_paginated,
            "page_obj": page_obj,
            "toon_alle_taken": request.session.get("toon_alle_taken", False),
        },
    )


@login_required
@permission_required("authorisatie.taken_lijst_bekijken", raise_exception=True)
def taak_zoeken(request):
    body = json.loads(request.body)
    request.session["q"] = body.get("q", "")
    return JsonResponse({"q": request.session.get("q", "")})


@login_required
def sorteer_filter(request):
    sortering = get_sortering(request.user)
    form = SorteerFilterForm({"sorteer_opties": sortering}, gebruiker=request.user)
    request_type = "get"
    if request.POST:
        request_type = "post"
        form = SorteerFilterForm(request.POST, gebruiker=request.user)
        if form.is_valid():
            sortering = form.cleaned_data.get("sorteer_opties")
            set_sortering(request.user, sortering)
    return render(
        request,
        "snippets/sorteer_filter_form.html",
        {
            "form": form,
            "request_type": request_type,
        },
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
def taak_detail(request, uuid):
    taak = get_object_or_404(Taak, uuid=uuid)
    if taak.verwijderd_op:
        return render(request, "410.html", {}, status=410)
    ua = request.META.get("HTTP_USER_AGENT", "")
    device = DeviceDetector(ua).parse()
    taakdeellinks = TaakDeellink.objects.filter(taak=taak)
    return render(
        request,
        "taken/taak_detail.html",
        {
            "id": id,
            "taak": taak,
            "device_os": device.os_name().lower(),
            "taakdeellinks": taakdeellinks,
            "taakdeellinks_bezoekers": [
                b for link in taakdeellinks for b in link.bezoekers
            ],
        },
    )


@login_required
@permission_required("authorisatie.taak_bekijken", raise_exception=True)
def taak_detail_melding_tijdlijn(request, uuid):
    taak = get_object_or_404(Taak, uuid=uuid)
    if taak.verwijderd_op:
        return render(request, "410.html", {}, status=410)
    tijdlijn_data = melding_naar_tijdlijn(taak.melding.response_json)

    return render(
        request,
        "taken/taak_detail_melding_tijdlijn.html",
        {
            "id": id,
            "taak": taak,
            "tijdlijn_data": tijdlijn_data,
            "melding": taak.melding.response_json,
        },
    )


class WhatsappSchemeRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = ["whatsapp", "https"]


@permission_required("authorisatie.taak_delen", raise_exception=True)
def taak_delen(request, uuid):
    taak = get_object_or_404(Taak, uuid=uuid)
    if taak.verwijderd_op:
        return render(request, "410.html", {}, status=410)
    gebruiker_email = request.user.email
    """
    Standaard worden links die gedeeld worden alleen in FixeR opgeslagen
    Met de code hieronder kan ook MOR-Core deze info opslaan in context met de melding

    response = MORCoreService().taak_gebeurtenis_toevoegen(
        taakopdracht_url=taak.taakopdracht,
        gebeurtenis_type="gedeeld",
        gebruiker=gebruiker_email,
    )
    if response.status_code not in [200]:
        return JsonResponse({})
    """

    ua = request.META.get("HTTP_USER_AGENT", "")
    device = DeviceDetector(ua).parse()
    whatsapp_url = "whatsapp://" if device.is_mobile() else settings.WHATSAPP_URL

    taak_gedeeld = TaakDeellink.objects.create(
        taak=taak,
        gedeeld_door=gebruiker_email,
        signed_data=TaakDeellink.get_signed_data(gebruiker_email),
    )

    return WhatsappSchemeRedirect(
        f"{whatsapp_url}send?text={taak_gedeeld.get_absolute_url(request)}",
    )


def taak_detail_preview(request, uuid, signed_data):
    taak = get_object_or_404(Taak, uuid=uuid)
    if taak.verwijderd_op:
        return render(request, "410.html", {}, status=410)
    gebruiker_email = None
    link_actief = False

    taak_gedeeld = TaakDeellink.objects.filter(
        taak=taak,
        signed_data=signed_data,
    ).first()
    if taak_gedeeld:
        link_actief = taak_gedeeld.actief()

    # links die gedeeld zijn voor dat het TaakDeellink object geimplementeerd was
    else:
        try:
            gebruiker_email = signing.loads(
                signed_data, max_age=settings.SIGNED_DATA_MAX_AGE_SECONDS
            )
            link_actief = True
        except signing.BadSignature:
            ...

    # redirect ingelogde gebruikers
    if request.user.has_perms(["authorisatie.taak_bekijken"]):
        return redirect(reverse("taak_detail", args=[taak.uuid]))

    # sla alle gebruikers op in het taakdeellink object
    if taak_gedeeld and link_actief:
        taak_gedeeld.bezoekers.append(
            request.user.email if request.user.is_authenticated else None
        )
        taak_gedeeld.save()

    ua = request.META.get("HTTP_USER_AGENT", "")
    device = DeviceDetector(ua).parse()
    return render(
        request,
        "taken/taak_detail_preview.html",
        {
            "taak": taak,
            "device_os": device.os_name().lower(),
            "signed_data": signed_data,
            "gebruiker_email": (
                taak_gedeeld.gedeeld_door if taak_gedeeld else gebruiker_email
            ),
            "link_actief": link_actief,
            "taak_gedeeld": taak_gedeeld,
        },
    )


@user_passes_test(lambda u: u.is_superuser)
def clear_melding_token_from_cache(request):
    cache.delete("meldingen_token")
    return HttpResponse("melding_token removed from cache")


@login_required
@permission_required("authorisatie.taak_afronden", raise_exception=True)
def taak_afhandelen(request, uuid):
    resolutie = request.GET.get("resolutie", "opgelost")
    taak = get_object_or_404(Taak, uuid=uuid)
    if taak.verwijderd_op:
        return render(request, "410.html", {}, status=410)
    taaktypes = TaakRService().get_taaktypes(
        params={
            "taakapplicatie_taaktype_url": taak.taaktype.taaktype_url(request),
        },
        force_cache=True,
    )
    volgende_taaktypes = []
    actieve_vervolg_taken = []
    if taak.taakstatus.naam == "voltooid":
        messages.warning(request, "Deze taak is ondertussen al afgerond.")
        return render(
            request,
            "incident/modal_handle.html",
            {
                "taak": taak,
            },
        )

    if taaktypes:
        openstaande_taaktype_urls_voor_melding = [
            to.get("taaktype")
            for to in taak.melding.response_json.get("taakopdrachten_voor_melding", [])
            if to.get("status", {}).get("naam") == "nieuw"
        ]
        alle_volgende_taaktypes = [
            (
                TaakRService()
                .get_taaktype_by_url(taaktype_url)
                .get("taakapplicatie_taaktype_url"),
                TaakRService().get_taaktype_by_url(taaktype_url).get("omschrijving"),
            )
            for taaktype_url in taaktypes[0].get("volgende_taaktypes", [])
            if TaakRService().get_taaktype_by_url(taaktype_url).get("actief")
        ]
        volgende_taaktypes = [
            taaktype
            for taaktype in alle_volgende_taaktypes
            if taaktype[0] not in openstaande_taaktype_urls_voor_melding
        ]
        actieve_vervolg_taken = [
            taaktype
            for taaktype in alle_volgende_taaktypes
            if taaktype[0] in openstaande_taaktype_urls_voor_melding
        ]

    form = TaakBehandelForm(
        volgende_taaktypes=volgende_taaktypes,
        initial={"resolutie": resolutie},
    )

    if request.POST:
        form = TaakBehandelForm(
            request.POST,
            request.FILES,
            volgende_taaktypes=volgende_taaktypes,
            initial={"resolutie": resolutie},
        )
        if form.is_valid():
            volgende_taaktypes_lookup = {
                taaktype[0]: taaktype[1] for taaktype in volgende_taaktypes
            }
            vervolg_taaktypes = [
                {
                    "taaktype_url": taaktype_url,
                    "omschrijving": volgende_taaktypes_lookup.get(taaktype_url),
                    "bericht": form.cleaned_data.get("omschrijving_intern"),
                }
                for taaktype_url in form.cleaned_data.get("nieuwe_taak", [])
            ]

            bijlagen = request.FILES.getlist("bijlagen", [])
            bijlage_paden = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlage_paden.append(file_name)

            taak = Taak.acties.status_aanpassen(
                status=Taakstatus.NaamOpties.VOLTOOID,
                resolutie=form.cleaned_data.get("resolutie"),
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
                bijlage_paden=bijlage_paden,
                taak=taak,
                vervolg_taaktypes=vervolg_taaktypes,
            )
            return redirect("taken")
        else:
            logger.error(f"taak_afhandelen: for errors: {form.errors}")

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


def _meldingen_bestand(request, modified_path):
    instelling = Instelling.actieve_instelling()
    if not instelling:
        raise Exception(
            "De MOR-Core url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
        )
    url = f"{instelling.mor_core_basis_url}{modified_path}"
    cache_key = f"meldingen_bestand_{url}"
    response = cache.get(cache_key)
    if not response:
        response = requests.get(url, headers=MORCoreService().get_headers())
        cache.set(cache_key, response, 600)
    return HttpResponse(
        response,
        content_type=response.headers.get("content-type"),
        headers={
            "Content-Disposition": "attachment",
        },
        status=response.status_code,
        reason=response.reason,
    )


def meldingen_bestand(request):
    modified_path = request.path.replace(settings.MOR_CORE_URL_PREFIX, "")
    if request.GET.get("signed-data"):
        try:
            signing.loads(
                request.GET.get("signed-data"),
                max_age=settings.SIGNED_DATA_MAX_AGE_SECONDS,
                salt=settings.SECRET_KEY,
            )
            return _meldingen_bestand(request, modified_path)
        except signing.BadSignature:
            ...
    return meldingen_bestand_protected(request)


@login_required
@permission_required("authorisatie.taak_bekijken", raise_exception=True)
def meldingen_bestand_protected(request):
    modified_path = request.path.replace(settings.MOR_CORE_PROTECTED_URL_PREFIX, "")
    return _meldingen_bestand(request, modified_path)


@login_required
def infosheet_mock(request):
    return render(
        request,
        "infosheet/infosheet_mock.html",
        {},
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

    # Get release notes published within 5 weeks and not in future
    def get_release_notes(self):
        release_notes = [
            release_note
            for release_note in ReleaseNote.objects.all().order_by("-publicatie_datum")
            if release_note.is_published()
        ][:6]

        return release_notes
