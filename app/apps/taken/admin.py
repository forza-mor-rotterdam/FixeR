from apps.taken.models import Taak, Taakgebeurtenis, Taaktype
from django.contrib import admin


class TaakAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titel",
        "taaktype",
        "melding",
        "aangemaakt_op",
    )
    list_editable = ("melding",)


class TaaktypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "omschrijving",
        "aangemaakt_op",
    )


class TaakgebeurtenisAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "gebruiker",
    )


admin.site.register(Taak, TaakAdmin)
admin.site.register(Taaktype, TaaktypeAdmin)
admin.site.register(Taakgebeurtenis, TaakgebeurtenisAdmin)
