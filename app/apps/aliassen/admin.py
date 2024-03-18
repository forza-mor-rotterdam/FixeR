from apps.aliassen.models import BijlageAlias, MeldingAlias
from apps.aliassen.tasks import task_update_melding_alias_data
from django.contrib import admin


@admin.action(description="Update melding alias data")
def action_update_melding_alias_data(self, request, queryset):
    for melding_alias in queryset:
        task_update_melding_alias_data.delay(melding_alias.id)


class MeldingAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bron_url",
        "aangepast_op",
        "geen_data",
    )
    actions = (action_update_melding_alias_data,)

    def geen_data(self, obj):
        return bool(not obj.response_json)


class BijlageAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bron_url",
    )


admin.site.register(MeldingAlias, MeldingAliasAdmin)
admin.site.register(BijlageAlias, BijlageAliasAdmin)
