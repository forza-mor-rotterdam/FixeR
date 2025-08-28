import logging

from apps.authenticatie.forms import (
    AfdelingForm,
    BevestigenForm,
    GebruikerAanmakenForm,
    GebruikerAanpassenForm,
    GebruikerBulkImportForm,
    GebruikerProfielForm,
    WelkomForm,
    WerklocatieForm,
)
from apps.context.forms import TaaktypesFilteredForm
from apps.instellingen.models import Instelling
from apps.main.services import MORCoreService, PDOKService, TaakRService
from apps.taken.models import Taaktype
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from formtools.wizard.views import SessionWizardView
from utils.diversen import absolute

Gebruiker = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.has_perms(["authorisatie.taken_lijst_bekijken"]):
            return redirect(reverse("taken_overzicht"), False)
        if request.user.has_perms(["authorisatie.beheer_bekijken"]):
            return redirect(reverse("beheer"), False)
        if request.user.is_authenticated:
            return redirect(reverse("root"), False)

        if settings.OIDC_ENABLED:
            return redirect(f"/oidc/authenticate/?next={request.GET.get('next', '/')}")
        if settings.ENABLE_DJANGO_ADMIN_LOGIN:
            return redirect(f"/admin/login/?next={request.GET.get('next', '/admin')}")

        return HttpResponse("Er is geen login ingesteld")


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login"), False)

        if settings.OIDC_ENABLED:
            return redirect("/oidc/logout/")
        if settings.ENABLE_DJANGO_ADMIN_LOGIN:
            return redirect(f"/admin/logout/?next={request.GET.get('next', '/')}")

        return HttpResponse("Er is geen logout ingesteld")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_bekijken", raise_exception=True),
    name="dispatch",
)
class GebruikerView(View):
    model = Gebruiker
    success_url = reverse_lazy("gebruiker_lijst")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_lijst_bekijken", raise_exception=True),
    name="dispatch",
)
class GebruikerLijstView(GebruikerView, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = self.object_list.select_related(
            "profiel__context"
        ).prefetch_related("groups")
        context["geauthoriseerde_gebruikers"] = object_list.filter(
            groups__isnull=False,
            verwijderd_op__isnull=True,
        )
        context["ongeauthoriseerde_gebruikers"] = object_list.filter(
            groups__isnull=True,
            verwijderd_op__isnull=True,
        )
        context["verwijderde_gebruikers"] = object_list.filter(
            verwijderd_op__isnull=False
        )
        return context


class GebruikerAanmakenAanpassenView(GebruikerView):
    def form_valid(self, form):
        if not hasattr(form.instance, "profiel"):
            form.instance.save()
        if form.cleaned_data.get("context"):
            form.instance.profiel.context = form.cleaned_data.get("context")
        else:
            form.instance.profiel.context = None
        form.instance.profiel.save()
        form.instance.groups.clear()
        if form.cleaned_data.get("group"):
            form.instance.groups.add(form.cleaned_data.get("group"))

        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_aanpassen", raise_exception=True),
    name="dispatch",
)
class GebruikerAanpassenView(
    SuccessMessageMixin, GebruikerAanmakenAanpassenView, UpdateView
):
    form_class = GebruikerAanpassenForm
    template_name = "authenticatie/gebruiker_aanpassen.html"
    success_message = "De gebruiker '%(email)s' is aangepast"

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        context = obj.profiel.context if hasattr(obj, "profiel") else None
        initial["context"] = context
        initial["group"] = obj.groups.all().first()
        return initial

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            email=self.object.email,
        )


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_aanmaken", raise_exception=True),
    name="dispatch",
)
class GebruikerAanmakenView(
    SuccessMessageMixin, GebruikerAanmakenAanpassenView, CreateView
):
    template_name = "authenticatie/gebruiker_aanmaken.html"
    form_class = GebruikerAanmakenForm
    success_message = "De gebruiker '%(email)s' is aangemaakt"


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_verwijderen", raise_exception=True),
    name="dispatch",
)
class GebruikerVerwijderenView(GebruikerAanmakenAanpassenView, UpdateView):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        object.verwijderd_op = timezone.now()
        object.groups.clear()
        object.save(update_fields=["verwijderd_op"])
        messages.success(
            request,
            f"De gebruiker '{object.email}' is verwijderd",
        )
        return redirect(reverse("gebruiker_lijst"))


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_terughalen", raise_exception=True),
    name="dispatch",
)
class GebruikerTerughalenView(GebruikerAanmakenAanpassenView, UpdateView):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        object.verwijderd_op = None
        object.save(update_fields=["verwijderd_op"])
        messages.success(
            request,
            f"De gebruiker '{object.email}' is teruggehaald",
        )
        return redirect(reverse("gebruiker_lijst"))


@login_required
@permission_required("authorisatie.gebruiker_aanmaken", raise_exception=True)
def gebruiker_bulk_import(request):
    form = GebruikerBulkImportForm()
    aangemaakte_gebruikers = None
    if request.POST:
        form = GebruikerBulkImportForm(request.POST, request.FILES)
        if form.is_valid():
            request.session["valid_rows"] = form.cleaned_data.get("csv_file", {}).get(
                "valid_rows", []
            )
        if request.session.get("valid_rows") and request.POST.get("aanmaken"):
            aangemaakte_gebruikers = form.submit(request.session.get("valid_rows"))
            messages.success(
                request,
                f"Er zijn {len(aangemaakte_gebruikers)} gebruikers met success aangepast of geïmporteerd",
            )
            del request.session["valid_rows"]
            form = None
    return render(
        request,
        "authenticatie/gebruiker_bulk_import.html",
        {
            "form": form,
            "aangemaakte_gebruikers": aangemaakte_gebruikers,
        },
    )


@method_decorator(login_required, name="dispatch")
class GebruikerProfielView(UpdateView):
    model = Gebruiker
    form_class = GebruikerProfielForm
    template_name = "authenticatie/gebruiker_profiel.html"
    success_url = reverse_lazy("gebruiker_profiel")

    def get_context_data(self, **kwargs):
        instelling = Instelling.actieve_instelling()
        if not instelling or not instelling.email_beheer:
            raise Exception(
                "De beheer_email kan niet worden gevonden, er zijn nog geen instellingen voor aangemaakt"
            )
        context = super().get_context_data(**kwargs)
        context["email_beheer"] = instelling.email_beheer
        return context

    def get_object(self, queryset=None):
        return self.request.user

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        context = obj.profiel.context if hasattr(obj, "profiel") else None
        initial["context"] = context
        initial["group"] = obj.groups.all().first()
        return initial

    def form_valid(self, form):
        MORCoreService().set_gebruiker(
            gebruiker=self.request.user.serialized_instance(),
        )
        messages.success(self.request, "Gebruikersgegevens succesvol opgeslagen.")
        return super().form_valid(form)


FORMS = [
    ("welkom", WelkomForm),
    # ("profielfoto", ProfielfotoForm),
    ("afdeling", AfdelingForm),
    ("taken", TaaktypesFilteredForm),
    ("werklocatie", WerklocatieForm),
    ("bevestigen", BevestigenForm),
]

TEMPLATES = {
    "welkom": "onboarding/welkom.html",
    # "profielfoto": "onboarding/profielfoto_form.html",
    "afdeling": "onboarding/afdeling_form.html",
    "taken": "onboarding/taken_form.html",
    "werklocatie": "onboarding/werklocatie_form.html",
    "bevestigen": "onboarding/bevestigen_form.html",
}


@method_decorator(login_required, name="dispatch")
class OnboardingView(SessionWizardView):
    form_list = FORMS
    file_storage = FileSystemStorage(location=settings.MEDIA_ROOT)
    afdelingen_data = None

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def dispatch(self, *args, **kwargs):
        if not self.afdelingen_data:
            self.afdelingen_data = TaakRService().get_afdelingen(
                taakapplicatie_basis_urls=[absolute(self.request).get("ABSOLUTE_ROOT")]
            )
        return super().dispatch(*args, **kwargs)

    def done(self, form_list, **kwargs):
        self.request.session["toon_alle_taken"] = False
        pdok_service = PDOKService()
        profiel_filters_base_key = "nieuw"
        gebruiker = self.request.user
        profiel = gebruiker.profiel
        form_data = {form.prefix: form.cleaned_data for form in form_list}

        profielfoto_data = form_data.get("profielfoto")
        afdeling_data = form_data.get("afdeling")
        taken_data = form_data.get("taken")
        werklocatie_data = form_data.get("werklocatie")
        # bevestig_data = form_data.get("bevestigen")

        selected_taaktypes = []
        buurtnamen = []
        profiel.taaktypes.clear()
        if taken_data:
            for key, value in taken_data.items():
                if key.startswith("taaktypes_"):
                    taaktype_ids = [str(taaktype.id) for taaktype in value]
                    taaktypes = Taaktype.objects.filter(id__in=taaktype_ids)
                    profiel.taaktypes.add(*taaktypes)
                    selected_taaktypes.extend(taaktype_ids)
        selected_taaktypes = [
            taaktype_id
            for taaktype_id in selected_taaktypes
            if taaktype_id
            in profiel.filters.get(profiel_filters_base_key, {}).get("taken", [])
        ]

        # Set profile data based on collected form data
        if profielfoto_data:
            profiel.profielfoto = profielfoto_data.get("profielfoto")
        if afdeling_data:
            profiel.afdelingen = afdeling_data.get("afdelingen", [])
        if werklocatie_data:
            profiel.stadsdeel = werklocatie_data.get("stadsdeel")
            wijkcodes = werklocatie_data.get("wijken", [])
            profiel.wijken = wijkcodes
            buurtnamen = [
                buurtnaam
                for buurtnaam in pdok_service.get_buurten_middels_wijkcodes(
                    settings.WIJKEN_EN_BUURTEN_GEMEENTECODE, wijkcodes
                )
                if buurtnaam
                in profiel.filters.get(profiel_filters_base_key, {}).get("buurt", [])
            ]

        profiel.filters = {
            profiel_filters_base_key: {
                "buurt": buurtnamen,
                "taken": selected_taaktypes,
                "taak_status": ["nieuw"],
                "begraafplaats": [],
            },
        }
        profiel.onboarding_compleet = True
        profiel.save()

        return redirect("taken")

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        if self.request.user.is_authenticated:
            if step in "afdeling":
                kwargs["afdelingen_data"] = self.afdelingen_data
            if step == "taken" and (
                afdeling_cleaned_data := self.get_cleaned_data_for_step("afdeling")
            ):
                kwargs["afdelingen_data"] = self.afdelingen_data

                kwargs["afdelingen_selected"] = afdeling_cleaned_data.get(
                    "afdelingen", []
                )
            elif step == "bevestigen":
                kwargs["afdelingen_data"] = self.afdelingen_data
                previous_steps_data = {}

                for step in self.steps.all[:-1]:
                    if step_cleaned_data := self.get_cleaned_data_for_step(step):
                        previous_steps_data.update(step_cleaned_data)
                kwargs["previous_steps_data"] = previous_steps_data
        return kwargs

    def get_taaktypes_initial(self, profiel):
        taaktypes_initial = {}
        for taaktype in profiel.taaktypes.all():
            for afdeling in self.afdelingen_data:
                if taaktype.taaktype_url(self.request) in [
                    tt["taakapplicatie_taaktype_url"]
                    for tt in afdeling.get("taaktypes_voor_afdelingen", [])
                ]:
                    field_name = f"taaktypes_{afdeling['naam']}"
                    if field_name not in taaktypes_initial:
                        taaktypes_initial[field_name] = []
                    taaktypes_initial[field_name].append(taaktype.id)
        return taaktypes_initial

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        profiel = self.request.user.profiel

        if profiel.onboarding_compleet:
            if step == "werklocatie":
                initial.update(
                    {
                        "stadsdeel": profiel.stadsdeel,
                        "wijken": profiel.wijken,
                    }
                )
            elif step == "afdeling":
                initial.update(
                    {
                        "afdelingen": profiel.afdelingen,
                    }
                )
            elif step == "taken":
                initial.update(self.get_taaktypes_initial(profiel))

            # elif step == "profielfoto":
            #     initial.update(
            #         {
            #             "profielfoto": profiel.profielfoto,
            #         }
            #     )

        return initial
