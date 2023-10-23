from apps.taken.forms import TaaktypeAanmakenForm, TaaktypeAanpassenForm
from apps.taken.models import Taaktype
from django.contrib.auth.decorators import permission_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView


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
    ...


@method_decorator(
    permission_required("authorisatie.taaktype_aanpassen"), name="dispatch"
)
class TaaktypeAanpassenView(TaaktypeAanmakenAanpassenView, UpdateView):
    form_class = TaaktypeAanpassenForm


@method_decorator(
    permission_required("authorisatie.taaktype_aanmaken"), name="dispatch"
)
class TaaktypeAanmakenView(TaaktypeAanmakenAanpassenView, CreateView):
    form_class = TaaktypeAanmakenForm
