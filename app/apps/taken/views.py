from apps.taaktype.models import TaaktypeReden
from apps.taken.forms import (
    TaaktypeAanmakenForm,
    TaaktypeAanpassenForm,
    TaaktypeRedenNietFormSet,
    TaaktypeRedenWelFormSet,
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            print(self.request.POST)
            context["reden_wel"] = TaaktypeRedenWelFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="reden_wel",
                queryset=TaaktypeReden.objects.filter(
                    type=TaaktypeReden.TypeOpties.WAAROM_WEL
                ),
            )
            context["reden_niet"] = TaaktypeRedenNietFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="reden_niet",
                queryset=TaaktypeReden.objects.filter(
                    type=TaaktypeReden.TypeOpties.WAAROM_NIET
                ),
            )
        else:
            context["reden_wel"] = TaaktypeRedenWelFormSet(
                instance=self.object,
                prefix="reden_wel",
                queryset=TaaktypeReden.objects.filter(
                    type=TaaktypeReden.TypeOpties.WAAROM_WEL
                ),
            )
            context["reden_niet"] = TaaktypeRedenNietFormSet(
                instance=self.object,
                prefix="reden_niet",
                queryset=TaaktypeReden.objects.filter(
                    type=TaaktypeReden.TypeOpties.WAAROM_NIET
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
                print("BIJLAGEN")
                # print(f.is_valid())
                if f.is_valid():
                    print(f.prefix)
                    print(f.cleaned_data.get("bijlage"))
                    # print(f.fields["bijlage"].html_name)
                    # print(f.files)
                f.bijlage_formset.save(commit=False)

                for obj in f.bijlage_formset.deleted_objects:
                    obj.delete()
                # for variant in bijlagen:
                #     variant.content_object = f.instance
                #     variant.save()

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
