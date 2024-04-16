import logging

from apps.authenticatie.forms import (
    GebruikerAanmakenForm,
    GebruikerAanpassenForm,
    GebruikerBulkImportForm,
    GebruikerProfielForm,
)
from apps.taaktype.forms import (
    AfdelingAanmakenForm,
    AfdelingAanpassenForm,
    TaaktypeMiddelAanmakenForm,
    TaaktypeMiddelAanpassenForm,
)
from apps.taaktype.models import Afdeling, TaaktypeMiddel
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

Gebruiker = get_user_model()
logger = logging.getLogger(__name__)


@login_required
@permission_required("authorisatie.taaktype_beheer_bekijken", raise_exception=True)
def taaktype_beheer(request):
    return render(
        request,
        "taaktype_beheer.html",
        {},
    )


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.afdeling_bekijken", raise_exception=True),
    name="dispatch",
)
class AfdelingView(View):
    model = Afdeling
    success_url = reverse_lazy("afdeling_lijst")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.afdeling_lijst_bekijken", raise_exception=True),
    name="dispatch",
)
class AfdelingLijstView(AfdelingView, ListView):
    ...


class AfdelingAanmakenAanpassenView(AfdelingView):
    ...


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.afdeling_aanpassen", raise_exception=True),
    name="dispatch",
)
class AfdelingAanpassenView(AfdelingAanmakenAanpassenView, UpdateView):
    form_class = AfdelingAanpassenForm


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.afdeling_aanmaken", raise_exception=True),
    name="dispatch",
)
class AfdelingAanmakenView(AfdelingAanmakenAanpassenView, CreateView):
    form_class = AfdelingAanmakenForm


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktypemiddel_bekijken", raise_exception=True),
    name="dispatch",
)
class TaaktypeMiddelView(View):
    model = TaaktypeMiddel
    success_url = reverse_lazy("taaktypemiddel_lijst")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required(
        "authorisatie.taaktypemiddel_lijst_bekijken", raise_exception=True
    ),
    name="dispatch",
)
class TaaktypeMiddelLijstView(TaaktypeMiddelView, ListView):
    ...


class TaaktypeMiddelAanmakenAanpassenView(TaaktypeMiddelView):
    ...


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktypemiddel_aanpassen", raise_exception=True),
    name="dispatch",
)
class TaaktypeMiddelAanpassenView(TaaktypeMiddelAanmakenAanpassenView, UpdateView):
    form_class = TaaktypeMiddelAanpassenForm


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktypemiddel_aanmaken", raise_exception=True),
    name="dispatch",
)
class TaaktypeMiddelAanmakenView(TaaktypeMiddelAanmakenAanpassenView, CreateView):
    form_class = TaaktypeMiddelAanmakenForm
