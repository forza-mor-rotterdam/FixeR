from apps.release_notes.models import Bijlage
from apps.release_notes.tasks import task_aanmaken_afbeelding_versies
from apps.taaktype.models import Afdeling, TaaktypeVoorbeeldsituatie
from apps.taken.forms import (
    TaaktypeAanmakenForm,
    TaaktypeAanpassenForm,
    TaaktypeVoorbeeldsituatieNietFormSet,
    TaaktypeVoorbeeldsituatieWelFormSet,
)
from apps.taken.models import Taaktype
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView


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
    queryset = Taaktype.objects.prefetch_related(
        "volgende_taaktypes",
        "afdelingen",
        "taaktypemiddelen",
        "contexten_voor_taaktypes",
        "voorbeeldsituatie_voor_taaktype__bijlagen",
    ).order_by("omschrijving")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["afdeling_onderdelen"] = [
            [
                onderdeel[1],
                self.queryset.filter(afdelingen__onderdeel=onderdeel[0]).distinct(),
            ]
            for onderdeel in Afdeling.OnderdeelOpties.choices
        ]
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_bekijken", raise_exception=True),
    name="dispatch",
)
class TaaktypeDetailView(TaaktypeView, DetailView):
    ...


class TaaktypeAanmakenAanpassenView(TaaktypeView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset_wel = TaaktypeVoorbeeldsituatie.objects.filter(
            type=TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_WEL
        )
        queryset_niet = TaaktypeVoorbeeldsituatie.objects.filter(
            type=TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_NIET
        )
        TaaktypeVoorbeeldsituatieWelFormSet.extra = 5 - queryset_wel.count()
        TaaktypeVoorbeeldsituatieNietFormSet.extra = 5 - queryset_niet.count()

        if self.request.POST:
            context["voorbeeldsituatie_wel"] = TaaktypeVoorbeeldsituatieWelFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="voorbeeldsituatie_wel",
                queryset=queryset_wel,
            )
            context["voorbeeldsituatie_niet"] = TaaktypeVoorbeeldsituatieNietFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="voorbeeldsituatie_niet",
                queryset=queryset_niet,
            )
        else:
            context["voorbeeldsituatie_wel"] = TaaktypeVoorbeeldsituatieWelFormSet(
                instance=self.object,
                prefix="voorbeeldsituatie_wel",
                queryset=queryset_wel,
            )
            context["voorbeeldsituatie_niet"] = TaaktypeVoorbeeldsituatieNietFormSet(
                instance=self.object,
                prefix="voorbeeldsituatie_niet",
                queryset=queryset_niet,
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        self.object = form.save()
        formsets = [context["voorbeeldsituatie_wel"], context["voorbeeldsituatie_niet"]]
        if not all([x.is_valid() for x in formsets]):
            return self.render_to_response(self.get_context_data(form=form))

        for voorbeeldsituatie_formset in [
            context["voorbeeldsituatie_wel"],
            context["voorbeeldsituatie_niet"],
        ]:
            voorbeeldsituaties = voorbeeldsituatie_formset.save(commit=False)
            for obj in voorbeeldsituatie_formset.deleted_objects:
                obj.delete()
            for voorbeeldsituatie in voorbeeldsituaties:
                voorbeeldsituatie.taaktype = self.object
                voorbeeldsituatie.save()
            for form in voorbeeldsituatie_formset.forms:
                if hasattr(form.files, "getlist") and form.files.getlist(
                    f"{form.prefix}-bestand"
                ):
                    bijlagen = [
                        Bijlage(
                            content_object=form.instance,
                            bestand=bijlage,
                        )
                        for bijlage in form.files.getlist(f"{form.prefix}-bestand")
                    ]
                    aangemaakte_bijlages = Bijlage.objects.bulk_create(bijlagen)
                    for bijlage in aangemaakte_bijlages:
                        task_aanmaken_afbeelding_versies.delay(bijlage.pk)

                form.bijlage_formset.save(commit=False)
                for bijlage in form.bijlage_formset.deleted_objects:
                    bijlage.delete()

        return redirect(reverse("taaktype_aanpassen", args=[self.object.id]))


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_aanpassen", raise_exception=True),
    name="dispatch",
)
class TaaktypeAanpassenView(TaaktypeAanmakenAanpassenView, UpdateView):
    form_class = TaaktypeAanpassenForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        current_taaktype = self.get_object()
        kwargs["current_taaktype"] = current_taaktype
        return kwargs


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_aanmaken", raise_exception=True),
    name="dispatch",
)
class TaaktypeAanmakenView(TaaktypeAanmakenAanpassenView, CreateView):
    form_class = TaaktypeAanmakenForm
