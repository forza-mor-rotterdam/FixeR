from apps.release_notes.forms import ReleaseNoteAanmakenForm, ReleaseNoteAanpassenForm
from django.contrib.auth.mixins import PermissionRequiredMixin
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

from .models import ReleaseNote


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
    # fields = ['versie', 'titel', 'beschrijving', 'publicatie_datum', 'afbeelding_of_gif']
    permission_required = "authorisatie.release_note_aanmaken"


class ReleaseNoteAanpassenView(PermissionRequiredMixin, ReleaseNoteView, UpdateView):
    form_class = ReleaseNoteAanpassenForm

    template_name = "beheer/release_note_aanpassen.html"
    # fields = ['versie', 'titel', 'beschrijving', 'publicatie_datum', 'afbeelding_of_gif']
    permission_required = "authorisatie.release_note_aanpassen"


class ReleaseNoteVerwijderenView(PermissionRequiredMixin, ReleaseNoteView, DeleteView):
    permission_required = "authorisatie.release_note_verwijderen"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
