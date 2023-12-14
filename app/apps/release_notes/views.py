from apps.release_notes.forms import (
    BijlageFormSet,
    ReleaseNoteAanmakenForm,
    ReleaseNoteAanpassenForm,
)
from apps.release_notes.tasks import task_aanmaken_afbeelding_versies
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from .models import Bijlage, ReleaseNote


class ReleaseNoteView(View):
    model = ReleaseNote
    success_url = reverse_lazy("release_note_lijst")


class ReleaseNoteListView(PermissionRequiredMixin, ReleaseNoteView, ListView):
    template_name = "beheer/release_note_list.html"
    context_object_name = "release_notes"
    permission_required = "authorisatie.release_note_lijst_bekijken"
    # form_class = ReleaseNoteSearchForm

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(titel__icontains=search) | Q(tekst__icontains=search)
            )
        return queryset


class ReleaseNoteDetailView(ReleaseNoteView, DetailView):
    template_name = "public/release_note_detail.html"
    context_object_name = "release_note"

    # form_class = ReleaseNoteSearchForm


class ReleaseNoteListViewPublic(ReleaseNoteView, ListView):
    template_name = "public/release_note_list.html"
    context_object_name = "release_notes"
    # form_class = ReleaseNoteSearchForm


class ReleaseNoteAanmakenView(PermissionRequiredMixin, ReleaseNoteView, CreateView):
    form_class = ReleaseNoteAanmakenForm
    template_name = "beheer/release_note_aanmaken.html"
    permission_required = "authorisatie.release_note_aanmaken"

    def form_valid(self, form):
        response = super().form_valid(form)

        bijlagen = self.request.FILES.getlist("bijlagen", [])

        for file in bijlagen:
            bijlage = Bijlage(
                content_type=ContentType.objects.get_for_model(self.object),
                object_id=self.object.id,
                bestand=file,
                mimetype=file.content_type,
                is_afbeelding=False,
            )
            bijlage.save()
            print(f"--- Bijlage: {bijlage} ---")

            task_aanmaken_afbeelding_versies.delay(bijlage.pk)
        return response


class ReleaseNoteAanpassenView(PermissionRequiredMixin, ReleaseNoteView, UpdateView):
    form_class = ReleaseNoteAanpassenForm

    template_name = "beheer/release_note_aanpassen.html"
    permission_required = "authorisatie.release_note_aanpassen"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = BijlageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix="bijlage",
            )
        else:
            context["formset"] = BijlageFormSet(instance=self.object, prefix="bijlage")
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            for bijlage_form in formset.forms:
                print(f"Bijlage form cleaned data: {bijlage_form.cleaned_data}")
                if bijlage_form.is_valid():
                    bijlage = bijlage_form.save(commit=False)
                    bijlage.content_object = self.object
                    bijlage.save()
                    task_aanmaken_afbeelding_versies.delay(bijlage.pk)
            formset.save()

            bijlagen = self.request.FILES.getlist("bijlagen", [])

            for file in bijlagen:
                bijlage = Bijlage(
                    content_type=ContentType.objects.get_for_model(self.object),
                    object_id=self.object.id,
                    bestand=file,
                    mimetype=file.content_type,
                    is_afbeelding=False,
                )
                bijlage.save()

                task_aanmaken_afbeelding_versies.delay(bijlage.pk)
            return super().form_valid(form)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, formset=formset)
            )


class ReleaseNoteVerwijderenView(PermissionRequiredMixin, ReleaseNoteView, DeleteView):
    permission_required = "authorisatie.release_note_verwijderen"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
