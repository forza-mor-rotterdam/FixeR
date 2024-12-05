from apps.context.forms import ContextAanmakenForm, ContextAanpassenForm
from apps.context.models import Context
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_bekijken", raise_exception=True),
    name="dispatch",
)
class ContextView(View):
    model = Context
    success_url = reverse_lazy("context_lijst")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_lijst_bekijken", raise_exception=True),
    name="dispatch",
)
class ContextLijstView(ContextView, ListView):
    ...


class ContextAanmakenAanpassenView(ContextView):
    def form_valid(self, form):
        form.instance.filters = {"fields": form.cleaned_data.get("filters")}
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_aanpassen", raise_exception=True),
    name="dispatch",
)
class ContextAanpassenView(
    SuccessMessageMixin, ContextAanmakenAanpassenView, UpdateView
):
    form_class = ContextAanpassenForm
    success_message = "De rol '%(name)s' is aangepast"

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        initial["filters"] = obj.filters.get("fields", [])
        return initial


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_aanmaken", raise_exception=True),
    name="dispatch",
)
class ContextAanmakenView(
    SuccessMessageMixin, ContextAanmakenAanpassenView, CreateView
):
    form_class = ContextAanmakenForm
    success_message = "De rol '%(name)s' is aangemaakt"


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_verwijderen", raise_exception=True),
    name="dispatch",
)
class ContextVerwijderenView(ContextView, DeleteView):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        if not object.profielen_voor_context.all():
            response = self.delete(request, *args, **kwargs)
            messages.success(self.request, f"De rol '{object.naam}' is verwijderd")
            return response
        return HttpResponse("Verwijderen is niet mogelijk")
