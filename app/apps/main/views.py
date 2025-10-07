import logging
import math
import os
import uuid
from datetime import datetime

import requests
from apps.authenticatie.models import AFSTAND_SORTING_KEY
from apps.instellingen.models import Instelling
from apps.main.forms import TaakBehandelForm, TakenLijstFilterForm
from apps.main.services import MORCoreService, PDOKService, TaakRService
from apps.main.utils import melding_naar_tijdlijn
from apps.taken.filters import FILTERS_BY_KEY
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
from django.contrib.gis.db.models import ExpressionWrapper, FloatField
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.core import signing
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import FormView, ListView

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


def root(request):
    if request.user.has_perms(["authorisatie.taken_lijst_bekijken"]):
        return redirect(reverse("taken_overzicht"), False)
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


class TakenOverzicht(
    PermissionRequiredMixin,
    FormView,
    ListView,
):
    template_name = "taken/overzicht/basis.html"
    permission_required = "authorisatie.taken_lijst_bekijken"
    queryset = Taak.objects.taken_lijst()
    form_class = TakenLijstFilterForm
    paginate_by = 50
    success_url = "/"

    def get(self, request, *args, **kwargs):
        self.initial = {}
        self.form_data = {}
        self.initial_filter_data = None
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "request": self.request,
            }
        )
        return kwargs

    def get_initial_filter_data(self):
        if self.initial_filter_data is None:
            profiel_selected_filter_opties = self.request.user.profiel.taken_filter_data
            actieve_filters = [
                f
                for f in self.request.user.profiel.context.filters.get("fields", [])
                if f in FILTERS_BY_KEY.keys()
            ]
            self.initial_filter_data = {
                f: profiel_selected_filter_opties[f]
                for f in actieve_filters
                if profiel_selected_filter_opties.get(f)
            }
        return self.initial_filter_data

    def get_gps(self):
        try:
            gps = self.form_data["gps"].split(",")
            return Point(
                float(gps[1]),
                float(gps[0]),
                srid=4326,
            )
        except Exception:
            return

    def get_queryset(self):
        queryset = super().get_queryset()
        profiel = self.request.user.profiel

        if not self.request.session.get("deactivate_filters"):
            queryset = queryset.filter(**profiel.taken_filter_query_data)
        queryset = queryset.taken_zoeken(self.request.session.get("q"))

        gps = self.get_gps()
        if gps:
            queryset = queryset.annotate(
                afstand=ExpressionWrapper(
                    Distance("melding__geometrie", gps), output_field=FloatField()
                )
            )
        if gps or (not gps and profiel.taken_sorting != AFSTAND_SORTING_KEY):
            queryset = queryset.order_by(profiel.taken_sorting_order_by)

        selected_taak_uuid = self.request.GET.get(
            "taakUuid", self.form_data.get("selected_taak_uuid", "")
        )
        try:
            clean_selected_taak_uuid = uuid.UUID(selected_taak_uuid)
        except Exception:
            clean_selected_taak_uuid = None

        selected_taak = queryset.filter(uuid=clean_selected_taak_uuid).first()
        if clean_selected_taak_uuid and selected_taak:
            self.initial.update({"selected_taak_uuid": str(selected_taak.uuid)})
            index = list(queryset.values_list("id", flat=True)).index(selected_taak.id)
            page = math.floor(index / self.paginate_by) + 1
            self.kwargs["page"] = page

        return queryset

    def get_context_data(self, **kwargs):
        if self.request.GET.get("toon_alle_taken"):
            self.request.session["toon_alle_taken"] = True

        self.initial.update(self.request.user.profiel.taken_filter_validated_data)
        self.initial["q"] = self.request.session.get("q")
        if self.request.session.get("gps"):
            del self.request.session["gps"]
        self.initial["deactivate_filters"] = self.request.session.get(
            "deactivate_filters"
        )

        self.initial["kaart_modus"] = self.request.user.profiel.ui_instellingen.get(
            "kaart_modus", "toon_alles"
        )
        self.initial["sorteer_opties"] = self.request.user.profiel.ui_instellingen.get(
            "sortering", "Adres-reverse"
        )
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "profiel_taaktype_uuid_list": list(
                    self.request.user.profiel.taaktypes.values_list("uuid", flat=True)
                ),
            }
        )
        return context

    def form_invalid(self, form):
        logger.error("TakenOverzicht: FORM INVALID")
        logger.error(form.errors.as_json())
        return super().form_invalid(form)

    def form_valid(self, form):
        form.save()
        self.form_data = form.cleaned_data

        self.kwargs["page"] = form.cleaned_data.get("page", 1)

        self.object_list = self.get_queryset()
        context = self.get_context_data()

        context.update(form.changed_fields())

        response = render(
            self.request,
            "taken/overzicht/basis_stream.html",
            context=context,
        )
        response.headers["Content-Type"] = "text/vnd.turbo-stream.html"
        return response


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
            "profiel_taaktype_uuid_list": list(
                request.user.profiel.taaktypes.values_list("uuid", flat=True)
            ),
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
            "taken/taak_afhandelen.html",
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
            return redirect("taken_overzicht")
        else:
            logger.error(f"taak_afhandelen: for errors: {form.errors}")

    return render(
        request,
        "taken/taak_afhandelen.html",
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
