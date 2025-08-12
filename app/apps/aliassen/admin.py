from apps.aliassen.models import BijlageAlias, MeldingAlias
from apps.aliassen.tasks import task_update_melding_alias_data_voor_reeks
from django.contrib import admin
from django.db.models import Count, Q


@admin.action(description="Update melding alias data voor reeks")
def action_update_melding_alias_data(self, request, queryset):
    task_update_melding_alias_data_voor_reeks.delay(
        meldingalias_ids=list(queryset.values_list("id", flat=True))
    )
    self.message_user(
        request,
        f"Update melding alias data voor reeks: aantal={queryset.count()}",
    )


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
        "buurtnaam",
        "begraafplaats",
        "locatie_type",
        "zoek_tekst",
        "locatie_verbose",
    )
    actions = (action_update_melding_alias_data,)
    search_fields = ("bron_url",)
    list_filter = (
        ResponseDataFilter,
        TakenAantalFilter,
        "locatie_type",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            "taken_voor_meldingalias",
        )

    def taken_aantal(self, obj):
        return str(obj.taken_voor_meldingalias.count())


class BijlageAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bron_url",
    )


admin.site.register(MeldingAlias, MeldingAliasAdmin)
admin.site.register(BijlageAlias, BijlageAliasAdmin)
