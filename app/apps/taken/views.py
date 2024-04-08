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
    )

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
class TaaktypeDetailView(TaaktypeView):
    ...


class TaaktypeAanmakenAanpassenView(TaaktypeView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["voorbeeldsituatie_wel"] = TaaktypeVoorbeeldsituatieWelFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="voorbeeldsituatie_wel",
                queryset=TaaktypeVoorbeeldsituatie.objects.filter(
                    type=TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_WEL
                ),
            )
            context["voorbeeldsituatie_niet"] = TaaktypeVoorbeeldsituatieNietFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="voorbeeldsituatie_niet",
                queryset=TaaktypeVoorbeeldsituatie.objects.filter(
                    type=TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_NIET
                ),
            )
        else:
            context["voorbeeldsituatie_wel"] = TaaktypeVoorbeeldsituatieWelFormSet(
                instance=self.object,
                prefix="voorbeeldsituatie_wel",
                queryset=TaaktypeVoorbeeldsituatie.objects.filter(
                    type=TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_WEL
                ),
            )
            context["voorbeeldsituatie_niet"] = TaaktypeVoorbeeldsituatieNietFormSet(
                instance=self.object,
                prefix="voorbeeldsituatie_niet",
                queryset=TaaktypeVoorbeeldsituatie.objects.filter(
                    type=TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_NIET
                ),
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            print(self.request.POST)
            context["reden_wel"] = TaaktypeVoorbeeldsituatieWelFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="reden_wel",
                queryset=TaaktypeVoorbeeldsituatie.objects.filter(
                    type=TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_WEL
                ),
            )
            context["reden_niet"] = TaaktypeVoorbeeldsituatieNietFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="reden_niet",
                queryset=TaaktypeVoorbeeldsituatie.objects.filter(
                    type=TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_NIET
                ),
            )
        else:
            context["reden_wel"] = TaaktypeVoorbeeldsituatieWelFormSet(
                instance=self.object,
                prefix="reden_wel",
                queryset=TaaktypeVoorbeeldsituatie.objects.filter(
                    type=TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_WEL
                ),
            )
            context["reden_niet"] = TaaktypeVoorbeeldsituatieNietFormSet(
                instance=self.object,
                prefix="reden_niet",
                queryset=TaaktypeVoorbeeldsituatie.objects.filter(
                    type=TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_NIET
                ),
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        self.object = form.save()
        formsets = [context["reden_wel"], context["reden_niet"]]
        if not all([x.is_valid() for x in formsets]):
            return self.render_to_response(self.get_context_data(form=form))

        for ff in [context["reden_wel"], context["reden_niet"]]:
            redenen = ff.save(commit=False)
            for obj in ff.deleted_objects:
                obj.delete()
            for reden in redenen:
                reden.taaktype = self.object
                reden.save()

            for f in ff.forms:
                bijlagen = f.bijlage_formset.save(commit=False)

                for obj in f.bijlage_formset.deleted_objects:
                    obj.delete()
                for variant in bijlagen:
                    variant.content_object = f.instance
                    variant.save()

        return redirect(reverse("taaktype_aanpassen", args=[self.object.id]))
        # return self.render_to_response(self.get_context_data(form=form))

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
