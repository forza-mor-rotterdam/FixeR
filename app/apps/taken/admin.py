from apps.taken.models import Taak, Taaktype
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


admin.site.register(Taak, TaakAdmin)
admin.site.register(Taaktype, TaaktypeAdmin)
