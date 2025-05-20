from apps.aliassen.models import BijlageAlias, MeldingAlias
from apps.aliassen.tasks import task_update_melding_alias_data
from django.contrib import admin
from django.db.models import Count, Q


@admin.action(description="Update melding alias data")
def action_update_melding_alias_data(self, request, queryset):
    for melding_alias in queryset:
        task_update_melding_alias_data.delay(melding_alias.id)


class TakenAantalFilter(admin.SimpleListFilter):
    title = "taken aantal"
    parameter_name = "taken_voor_meldingalias"

    def lookups(self, request, model_admin):
        return (
            ("taken_aantal__lte", "Geen taken"),
            ("taken_aantal__gt", "1 of meer taken"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            value = "taken_aantal__gte"
        return (
            queryset.annotate(taken_aantal=Count("taken_voor_meldingalias"))
            .order_by()
            .filter(**{value: 0})
        )


class ZoekDataAantalFilter(admin.SimpleListFilter):
    title = "zoek data aantal"
    parameter_name = "taak_zoek_data"

    def lookups(self, request, model_admin):
        return (
            ("zoek_data_aantal__lte", "Geen zoek data"),
            ("zoek_data_aantal__gt", "1 of meer zoek data"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            value = "zoek_data_aantal__gte"
        return (
            queryset.annotate(zoek_data_aantal=Count("taken_voor_meldingalias"))
            .order_by()
            .filter(**{value: 0})
        )


class GeenTaakZoekDataFilter(admin.SimpleListFilter):
    title = "Geen taak zoek data"
    parameter_name = "geen_taak_zoek_data"

    def lookups(self, request, model_admin):
        return (("geen_taak_zoek_data", "Geen taak zoek data"),)

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(
                taak_zoek_data__straatnaam__isnull=True,
                taak_zoek_data__begraafplaats__isnull=True,
            )
        return queryset


class ResponseDataFilter(admin.SimpleListFilter):
    title = "heeft response data"
    parameter_name = "response_json"

    def lookups(self, request, model_admin):
        return (("has_not", "Geen response data"),)

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(
            Q(response_json__isnull=(value == "has_not")) | Q(response_json={})
        )


class MeldingAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bron_url",
        "aangepast_op",
        "taken_aantal",
        "taak_zoek_data_aantal",
        "onderwerp_urls",
    )
    actions = (action_update_melding_alias_data,)
    search_fields = ("bron_url",)
    list_filter = (
        ResponseDataFilter,
        TakenAantalFilter,
        ZoekDataAantalFilter,
        GeenTaakZoekDataFilter,
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            "taak_zoek_data",
            "taken_voor_meldingalias",
        )

    def taken_aantal(self, obj):
        return str(obj.taken_voor_meldingalias.count())

    def onderwerp_urls(self, obj):
        return obj.response_json.get("onderwerpen")

    def taak_zoek_data_aantal(self, obj):
        return str(obj.taak_zoek_data.count())

    def heeft_response_data(self, obj):
        return bool(obj.response_json)


class BijlageAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bron_url",
    )


admin.site.register(MeldingAlias, MeldingAliasAdmin)
admin.site.register(BijlageAlias, BijlageAliasAdmin)
