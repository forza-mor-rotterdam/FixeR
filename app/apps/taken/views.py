from apps.instellingen.models import Instelling
from apps.main.services import TaakRService
from apps.taken.forms import TaaktypeAanmakenForm, TaaktypeAanpassenForm
from apps.taken.models import Taaktype
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from rest_framework.reverse import reverse as drf_reverse
from utils.diversen import absolute


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_bekijken", raise_exception=True),
    name="dispatch",
)
class TaaktypeView(View):
    model = Taaktype
    success_url = reverse_lazy("taaktype_lijst")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_lijst_bekijken", raise_exception=True),
    name="dispatch",
)
class TaaktypeLijstView(TaaktypeView, ListView):
    queryset = Taaktype.objects.order_by("omschrijving")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context.update(
            {
                "active": queryset.filter(actief=True),
                "inactief": queryset.filter(actief=False),
            }
        )
        return context


class TaaktypeAanmakenAanpassenView(TaaktypeView):
    def get_success_url(self):
        return reverse("taaktype_aanpassen", kwargs={"pk": self.object.id})


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_aanpassen", raise_exception=True),
    name="dispatch",
)
class TaaktypeAanpassenView(
    SuccessMessageMixin, TaaktypeAanmakenAanpassenView, UpdateView
):
    form_class = TaaktypeAanpassenForm
    success_message = "Het taaktype '%(omschrijving)s' is aangepast"

    def get_initial(self):
        instelling = Instelling.actieve_instelling()
        if not instelling:
            raise Exception(
                "De TaakR url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
            )

        initial = self.initial.copy()
        initial["redirect_field"] = (
            self.request.GET.get("redirect_url", "")
            if self.request.GET.get("redirect_url", "").startswith(
                instelling.taakr_basis_url
            )
            else None
        )
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["taaktype_url"] = drf_reverse(
            "v1:taaktype-detail",
            kwargs={"uuid": self.object.uuid},
            request=self.request,
        )
        return context

    def form_valid(self, form):
        instelling = Instelling.actieve_instelling()
        if not instelling:
            raise Exception(
                "De TaakR url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
            )
        response = super().form_valid(form)

        taaktype_url = drf_reverse(
            "v1:taaktype-detail",
            kwargs={"uuid": self.object.uuid},
            request=self.request,
        )

        TaakRService().vernieuw_taaktypes(taaktype_url)
        if form.cleaned_data.get("redirect_field", "").startswith(
            instelling.taakr_basis_url
        ):
            return redirect(f"{form.cleaned_data.get('redirect_field')}{taaktype_url}")
        return response


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_aanmaken", raise_exception=True),
    name="dispatch",
)
class TaaktypeAanmakenView(
    SuccessMessageMixin, TaaktypeAanmakenAanpassenView, CreateView
):
    form_class = TaaktypeAanmakenForm
    success_message = "Het taaktype '%(omschrijving)s' is aangemaakt"

    def get(self, request, *args, **kwargs):
        taaktype_url = request.GET.get("taaktype_url", "")
        if taaktype_url.startswith(absolute(request).get("ABSOLUTE_ROOT")):
            taaktype_uuid = taaktype_url.split("/")[-2]
            taaktype = Taaktype.objects.filter(uuid=taaktype_uuid).first()
            if taaktype:
                return redirect(reverse("taaktype_aanpassen", args=[taaktype.id]))
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        instelling = Instelling.actieve_instelling()
        if not instelling:
            raise Exception(
                "De TaakR url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
            )
        initial = self.initial.copy()
        initial["redirect_field"] = (
            self.request.GET.get("redirect_url", "")
            if self.request.GET.get("redirect_url", "").startswith(
                instelling.taakr_basis_url
            )
            else None
        )
        return initial

    def form_valid(self, form):
        instelling = Instelling.actieve_instelling()
        if not instelling:
            raise Exception(
                "De TaakR url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
            )
        response = super().form_valid(form)
        taaktype_url = drf_reverse(
            "v1:taaktype-detail",
            kwargs={"uuid": self.object.uuid},
            request=self.request,
        )
        TaakRService().vernieuw_taaktypes(taaktype_url)
        if form.cleaned_data.get("redirect_field", "").startswith(
            instelling.taakr_basis_url
        ):
            return redirect(f"{form.cleaned_data.get('redirect_field')}{taaktype_url}")
        return response
