import logging

from apps.authenticatie.forms import (
    AfdelingForm,
    BevestigenForm,
    GebruikerAanmakenForm,
    GebruikerAanpassenForm,
    GebruikerBulkImportForm,
    GebruikerProfielForm,
    ProfielfotoForm,
    WerklocatieForm,
)
from apps.context.forms import TaaktypesFilteredForm
from apps.meldingen.service import MeldingenService
from apps.taaktype.models import Afdeling
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from formtools.wizard.views import SessionWizardView

Gebruiker = get_user_model()
logger = logging.getLogger(__name__)


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
        context["geauthoriseerde_gebruikers"] = object_list.filter(groups__isnull=False)
        context["ongeauthoriseerde_gebruikers"] = object_list.filter(
            groups__isnull=True
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
class GebruikerAanpassenView(GebruikerAanmakenAanpassenView, UpdateView):
    form_class = GebruikerAanpassenForm
    template_name = "authenticatie/gebruiker_aanpassen.html"

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        context = obj.profiel.context if hasattr(obj, "profiel") else None
        initial["context"] = context
        initial["group"] = obj.groups.all().first()
        return initial


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_aanmaken", raise_exception=True),
    name="dispatch",
)
class GebruikerAanmakenView(GebruikerAanmakenAanpassenView, CreateView):
    template_name = "authenticatie/gebruiker_aanmaken.html"
    form_class = GebruikerAanmakenForm


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
        context = super().get_context_data(**kwargs)
        context["email_beheer"] = settings.EMAIL_BEHEER
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
        MeldingenService().set_gebruiker(
            gebruiker=self.request.user.serialized_instance(),
        )
        messages.success(self.request, "Gebruikersgegevens succesvol opgeslagen.")
        return super().form_valid(form)


FORMS = [
    # ("profielfoto", ProfielfotoForm),
    ("afdeling", AfdelingForm),
    ("taken", TaaktypesFilteredForm),
    ("werklocatie", WerklocatieForm),
    ("bevestigen", BevestigenForm),
]

TEMPLATES = {
    # "profielfoto": "onboarding/profielfoto_form.html",
    "afdeling": "onboarding/afdeling_form.html",
    "taken": "onboarding/taken_form.html",
    "werklocatie": "onboarding/werklocatie_form.html",
    "bevestigen": "onboarding/bevestigen_form.html",
}


@method_decorator(login_required, name="dispatch")
class OnboardingView(SessionWizardView):
    form_list = FORMS
    template_name = "onboarding/multipart_form.html"
    file_storage = FileSystemStorage(location=settings.MEDIA_ROOT)

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = {form.prefix: form.cleaned_data for form in form_list}

        profielfoto_data = form_data.get("profielfoto")
        afdeling_data = form_data.get("afdeling")
        taken_data = form_data.get("taken")
        werklocatie_data = form_data.get("werklocatie")
        bevestigen_data = form_data.get("bevestigen")

        selected_taaktypes = set()
        if taken_data:
            for key, value in taken_data.items():
                if key.startswith("taaktypes_"):
                    selected_taaktypes.update(value)

        gebruiker = self.request.user
        profiel = gebruiker.profiel
        # Set profile data based on collected form data
        if profielfoto_data:
            profiel.profielfoto = profielfoto_data.get("profielfoto")
        if afdeling_data:
            profiel.afdelingen.set(afdeling_data.get("afdelingen", []))
        if selected_taaktypes:
            profiel.context.taaktypes.set(selected_taaktypes)
        if werklocatie_data:
            profiel.stadsdeel = werklocatie_data.get("stadsdeel")
            profiel.context.filters.set(werklocatie_data.get("wijken", []))
        if bevestigen_data:
            pass
        profiel.save()

        messages.success(self.request, "Je instellingen zijn succesvol opgeslagen.")
        return redirect("onboarding-compleet")

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        if self.request.user.is_authenticated:
            if step == "taken":
                if self.get_cleaned_data_for_step("afdeling"):
                    # Pass selected Afdelingen to TaaktypesFilteredForm
                    afdelingen_selected = []
                    for form_key, form_value in self.get_cleaned_data_for_step(
                        "afdeling"
                    ).items():
                        if form_key.startswith("afdelingen_"):
                            afdelingen_selected.extend(form_value)
                    kwargs["afdelingen_selected"] = afdelingen_selected
                else:  # For testing!
                    afdelingen_selected = Afdeling.objects.filter(
                        onderdeel="schoon"
                    ).all()
                    kwargs["afdelingen_selected"] = afdelingen_selected
            elif step == "bevestigen":
                previous_steps_data = {}
                form_data = [
                    form.cleaned_data if isinstance(form, forms.Form) else {}
                    for form in self.get_form_list()
                ]
                for form_data_item in form_data[
                    :-1
                ]:  # Exclude the last form (BevestigenForm)
                    previous_steps_data.update(form_data_item)
                kwargs["previous_steps_data"] = previous_steps_data
        return kwargs

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if step == "bevestigen":
            previous_steps_data = {}
            form_data = [
                form.cleaned_data if isinstance(form, forms.Form) else {}
                for form in self.get_form_list()
            ]
            for form_data_item in form_data[
                :-1
            ]:  # Exclude the last form (BevestigenForm)
                previous_steps_data.update(form_data_item)
            initial["previous_steps_data"] = previous_steps_data
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            progress = (self.steps.index / (self.steps.count - 1)) * 100
        except ZeroDivisionError:
            progress = 100
        context["progress"] = progress
        print(
            f"Total steps: {self.steps.count}, Current step: {self.steps.index+1}, Progress: {context['progress']}"
        )
        return context


@login_required
def onboarding_compleet(request):
    # This context can be expanded based on the information you want to display
    context = {
        "user": request.user,
    }
    return render(request, "onboarding/compleet.html", context)
