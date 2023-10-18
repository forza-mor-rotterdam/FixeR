from apps.aliassen.models import BijlageAlias, MeldingAlias
from apps.main.utils import update_meldingen
from django.contrib import admin


@admin.action(description="Update meldingen")
def action_update_meldingen(modeladmin, request, queryset):
    update_meldingen(queryset)


class MeldingAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bron_url",
        "aangepast_op",
    )
    actions = (action_update_meldingen,)


class BijlageAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bron_url",
    )


admin.site.register(MeldingAlias, MeldingAliasAdmin)
admin.site.register(BijlageAlias, BijlageAliasAdmin)
