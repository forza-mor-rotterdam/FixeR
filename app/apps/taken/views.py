from apps.taken.forms import TaaktypeAanmakenForm, TaaktypeAanpassenForm
from apps.taken.models import Taaktype
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from rest_framework.reverse import reverse as drf_reverse


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
    ...


class TaaktypeAanmakenAanpassenView(TaaktypeView):
    ...


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_aanpassen", raise_exception=True),
    name="dispatch",
)
class TaaktypeAanpassenView(TaaktypeAanmakenAanpassenView, UpdateView):
    form_class = TaaktypeAanpassenForm

    def get_initial(self):
        initial = self.initial.copy()
        initial["redirect_field"] = (
            self.request.GET.get("redirect_url", "")
            if self.request.GET.get("redirect_url", "").startswith(settings.TAAKR_URL)
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
        response = super().form_valid(form)
        if form.cleaned_data.get("redirect_field", "").startswith(settings.TAAKR_URL):
            taaktype_url = drf_reverse(
                "v1:taaktype-detail",
                kwargs={"uuid": self.object.uuid},
                request=self.request,
            )
            return redirect(f"{form.cleaned_data.get('redirect_field')}{taaktype_url}")
        return response


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_aanmaken", raise_exception=True),
    name="dispatch",
)
class TaaktypeAanmakenView(TaaktypeAanmakenAanpassenView, CreateView):
    form_class = TaaktypeAanmakenForm

    def get_initial(self):
        initial = self.initial.copy()
        initial["redirect_field"] = (
            self.request.GET.get("redirect_url", "")
            if self.request.GET.get("redirect_url", "").startswith(settings.TAAKR_URL)
            else None
        )
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get("redirect_field", "").startswith(settings.TAAKR_URL):
            taaktype_url = drf_reverse(
                "v1:taaktype-detail",
                kwargs={"uuid": self.object.uuid},
                request=self.request,
            )
            return redirect(f"{form.cleaned_data.get('redirect_field')}{taaktype_url}")
        return response
