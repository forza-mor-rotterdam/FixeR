from apps.taaktype.models import Afdeling, TaaktypeMiddel, TaaktypeReden
from django.contrib import admin


class AfdelingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "naam",
        "onderdeel",
    )
    list_editable = ("naam", "onderdeel")


class TaaktypeMiddelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "naam",
    )
    list_editable = ("naam",)


class TaaktypeRedenAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "toelichting",
    )


admin.site.register(Afdeling, AfdelingAdmin)
admin.site.register(TaaktypeMiddel, TaaktypeMiddelAdmin)
admin.site.register(TaaktypeReden, TaaktypeRedenAdmin)
