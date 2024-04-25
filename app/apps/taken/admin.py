from apps.taken.admin_filters import (
    AfgeslotenOpFilter,
    ResolutieFilter,
    TaakstatusFilter,
    TitelFilter,
)
from apps.taken.models import (
    Taak,
    TaakDeellink,
    Taakgebeurtenis,
    Taaktype,
    TaakZoekData,
)
from apps.taken.tasks import compare_and_update_status
from django.contrib import admin


class TaakAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "titel",
        "taaktype",
        "melding",
        "taakstatus",
        "resolutie",
        "aangemaakt_op",
        "aangepast_op",
        # "geometrie",
        # "taak_zoek_data",
    )
    readonly_fields = (
        "uuid",
        "aangemaakt_op",
        "aangepast_op",
        "afgesloten_op",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "titel",
                    "melding",
                    "taaktype",
                    "taakstatus",
                    "resolutie",
                    "bericht",
                    "additionele_informatie",
                    "taakopdracht",
                )
            },
        ),
        (
            "Tijden",
            {
                "fields": (
                    "aangemaakt_op",
                    "aangepast_op",
                    "afgesloten_op",
                )
            },
        ),
    )
    list_filter = (
        TaakstatusFilter,
        ResolutieFilter,
        AfgeslotenOpFilter,
        TitelFilter,
    )
    # list_editable = ("melding",)
    actions = ["compare_taakopdracht_status"]

    def compare_taakopdracht_status(self, request, queryset):
        voltooid_taak_ids = queryset.filter(taakstatus__naam="voltooid").values_list(
            "id", flat=True
        )
        for taak_id in voltooid_taak_ids:
            compare_and_update_status.delay(taak_id)
        self.message_user(
            request, f"Updating taakopdracht for {len(voltooid_taak_ids)} taken!"
        )

    compare_taakopdracht_status.short_description = (
        "Compare taak and taakopdracht status"
    )


class TaaktypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "omschrijving",
        "aangemaakt_op",
    )


class TaakZoekDataAdmin(admin.ModelAdmin):
    list_display = ("id", "aangemaakt_op", "display_geometrie")
    readonly_fields = ("display_geometrie",)

    def display_geometrie(self, obj):
        # Convert GEOSGeometry to JSON string representation
        return str(obj.geometrie.geojson) if obj.geometrie else None

    display_geometrie.short_description = "Geometrie (JSON)"  # Customize column header


class TaakgebeurtenisAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "gebruiker",
    )


class TaakDeellinkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "gedeeld_door",
        "bezoekers",
        "signed_data",
        "taak",
    )


admin.site.register(TaakZoekData, TaakZoekDataAdmin)
admin.site.register(Taak, TaakAdmin)
admin.site.register(Taaktype, TaaktypeAdmin)
admin.site.register(Taakgebeurtenis, TaakgebeurtenisAdmin)
admin.site.register(TaakDeellink, TaakDeellinkAdmin)
