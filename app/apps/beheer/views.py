from apps.authenticatie.forms import GebruikerAanmakenForm, GebruikerAanpassenForm
from apps.context.forms import ContextAanmakenForm, ContextAanpassenForm
from apps.context.models import Context
from apps.taken.forms import TaaktypeAanmakenForm, TaaktypeAanpassenForm
from apps.taken.models import Taaktype
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

Gebruiker = get_user_model()


@permission_required("authorisatie.beheer_bekijken")
def beheer(request):
    return render(
        request,
        "beheer.html",
        {},
    )


@method_decorator(
    permission_required("authorisatie.gebruiker_bekijken"), name="dispatch"
)
class GebruikerView(View):
    model = Gebruiker
    success_url = reverse_lazy("gebruiker_lijst")


@method_decorator(
    permission_required("authorisatie.gebruiker_lijst_bekijken"), name="dispatch"
)
class GebruikerLijstView(GebruikerView, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = self.object_list
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


@method_decorator(
    permission_required("authorisatie.gebruiker_aanpassen"), name="dispatch"
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


@method_decorator(
    permission_required("authorisatie.gebruiker_aanmaken"), name="dispatch"
)
class GebruikerAanmakenView(GebruikerAanmakenAanpassenView, CreateView):
    template_name = "authenticatie/gebruiker_aanmaken.html"
    form_class = GebruikerAanmakenForm


@method_decorator(permission_required("authorisatie.context_bekijken"), name="dispatch")
class ContextView(View):
    model = Context
    success_url = reverse_lazy("context_lijst")


@method_decorator(
    permission_required("authorisatie.context_lijst_bekijken"), name="dispatch"
)
class ContextLijstView(ContextView, ListView):
    ...


class ContextAanmakenAanpassenView(ContextView):
    def form_valid(self, form):
        form.instance.filters = {"fields": form.cleaned_data.get("filters")}
        return super().form_valid(form)


@method_decorator(
    permission_required("authorisatie.context_aanpassen"), name="dispatch"
)
class ContextAanpassenView(ContextAanmakenAanpassenView, UpdateView):
    form_class = ContextAanpassenForm
    template_name = "context/context_aanpassen.html"

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        initial["filters"] = obj.filters.get("fields", [])
        return initial


@method_decorator(permission_required("authorisatie.context_aanmaken"), name="dispatch")
class ContextAanmakenView(ContextAanmakenAanpassenView, CreateView):
    template_name = "context/context_aanmaken.html"
    form_class = ContextAanmakenForm


@method_decorator(
    permission_required("authorisatie.taaktype_bekijken"), name="dispatch"
)
class TaaktypeView(View):
    model = Taaktype
    success_url = reverse_lazy("taaktype_lijst")


@method_decorator(
    permission_required("authorisatie.taaktype_lijst_bekijken"), name="dispatch"
)
class TaaktypeLijstView(TaaktypeView, ListView):
    ...


class TaaktypeAanmakenAanpassenView(TaaktypeView):
    def form_valid(self, form):
        return super().form_valid(form)


@method_decorator(
    permission_required("authorisatie.taaktype_aanpassen"), name="dispatch"
)
class TaaktypeAanpassenView(TaaktypeAanmakenAanpassenView, UpdateView):
    form_class = TaaktypeAanpassenForm
    template_name = "taken/taaktype_aanpassen.html"

    def get_initial(self):
        initial = self.initial.copy()
        self.get_object()
        return initial


@method_decorator(
    permission_required("authorisatie.taaktype_aanmaken"), name="dispatch"
)
class TaaktypeAanmakenView(TaaktypeAanmakenAanpassenView, CreateView):
    template_name = "taken/taaktype_aanmaken.html"
    form_class = TaaktypeAanmakenForm
