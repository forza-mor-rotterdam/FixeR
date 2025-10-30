from apps.taken.models import Taak
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class TaakopdrachtStatusFilter(admin.SimpleListFilter):
    title = _("TaakopdrachtStatus")
    parameter_name = "taakopdrachtStatus"

    def lookups(self, request, model_admin):
        return (
            ("nieuw", "Nieuw"),
            ("voltooid", "Voltooid"),
            ("voltooid_met_feedback", "Voltooid met feedback"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                additionele_informatie__taakopdracht__isnull=False,
                additionele_informatie__taakopdracht__status__naam=self.value(),
            )
        return queryset


class TaakopdrachtStatusCodeFilter(admin.SimpleListFilter):
    title = _("Taakopdracht status code ")
    parameter_name = "taakopdracht_status_code"

    def lookups(self, request, model_admin):
        return (
            ("geen", "Geen data"),
            ("200", "Valide data"),
            ("404", "Niet gevonden"),
            ("500", "Fout"),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() in ("geen",):
                return queryset.filter(
                    additionele_informatie__taakopdracht_status_code__isnull=True,
                )
            if self.value() in ("200", "404", "500"):
                return queryset.filter(
                    additionele_informatie__taakopdracht_status_code=str(self.value()),
                )
        return queryset


class ResolutieFilter(admin.SimpleListFilter):
    title = _("Resolutie")
    parameter_name = "resolutie"

    def lookups(self, request, model_admin):
        return Taak.ResolutieOpties.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(resolutie=self.value())
        else:
            return queryset


class TitelFilter(admin.SimpleListFilter):
    title = _("Titel")
    parameter_name = "titel"

    def lookups(self, request, model_admin):
        titles = Taak.objects.values_list("titel", flat=True).distinct()
        return ((title, title) for title in sorted(set(titles)))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(titel=self.value())
        return queryset


class AfgeslotenOpFilter(admin.SimpleListFilter):
    title = _("Afgesloten")
    parameter_name = "afgesloten"

    def lookups(self, request, model_admin):
        return (
            ("ja", _("Ja")),
            ("nee", _("Nee")),
        )

    def queryset(self, request, queryset):
        if self.value() == "ja":
            return queryset.exclude(afgesloten_op__isnull=True)
        elif self.value() == "nee":
            return queryset.filter(afgesloten_op__isnull=True)
        else:
            return queryset


class ZoekDataFilter(admin.SimpleListFilter):
    title = "heeft response data"
    parameter_name = "response_json"

    def lookups(self, request, model_admin):
        return (
            ("has_not", "Geen response data"),
            ("has", "Wel response data"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(response_json__isnull=(value == "has_not"))
