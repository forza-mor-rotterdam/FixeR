from apps.aliassen.models import BijlageAlias, MeldingAlias
from apps.aliassen.tasks import task_update_melding_alias_data
from apps.main.utils import update_meldingen
from django.contrib import admin


@admin.action(description="Update meldingen")
def action_update_meldingen(modeladmin, request, queryset):
    update_meldingen(queryset)


@admin.action(description="Update melding alias data")
def action_update_melding_alias_data(self, request, queryset):
    task_update_melding_alias_data()


class MeldingAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bron_url",
        "aangepast_op",
        "geen_data",
    )
    actions = (action_update_meldingen, action_update_melding_alias_data)

    def geen_data(self, obj):
        return bool(not obj.response_json)


class BijlageAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bron_url",
    )


admin.site.register(MeldingAlias, MeldingAliasAdmin)
admin.site.register(BijlageAlias, BijlageAliasAdmin)
