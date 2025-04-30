import ast
import importlib
import json

from apps.taken.admin_filters import (
    AfgeslotenOpFilter,
    ResolutieFilter,
    TaakopdrachtStatusCodeFilter,
    TaakopdrachtStatusFilter,
    TaakstatusFilter,
    TitelFilter,
)
from apps.taken.models import (
    Taak,
    TaakDeellink,
    Taakgebeurtenis,
    Taakstatus,
    Taaktype,
    TaakZoekData,
)
from apps.taken.tasks import (
    start_update_taakopdracht_data_for_taak_ids,
    task_taakopdracht_notificatie_voor_taak,
    update_taak_status_met_taakopdracht_status,
)
from django.contrib import admin, messages
from django.db.models import Count
from django.utils.safestring import mark_safe
from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import TaskResult


def retry_celery_task_admin_action(modeladmin, request, queryset):
    msg = ""
    for task_res in queryset:
        if task_res.status != "FAILURE":
            msg += f'{task_res.task_id} => Skipped. Not in "FAILURE" State<br>'
            continue
        try:
            task_actual_name = task_res.task_name.split(".")[-1]
            module_name = ".".join(task_res.task_name.split(".")[:-1])
            kwargs = json.loads(task_res.task_kwargs)
            if isinstance(kwargs, str):
                kwargs = kwargs.replace("'", '"')
                kwargs = json.loads(kwargs)
                if kwargs:
                    getattr(
                        importlib.import_module(module_name), task_actual_name
                    ).apply_async(kwargs=kwargs, task_id=task_res.task_id)
            if not kwargs:
                args = ast.literal_eval(ast.literal_eval(task_res.task_args))
                getattr(
                    importlib.import_module(module_name), task_actual_name
                ).apply_async(args, task_id=task_res.task_id)
            msg += f"{task_res.task_id} => Successfully sent to queue for retry.<br>"
        except Exception as ex:
            msg += f"{task_res.task_id} => Unable to process. Error: {ex}<br>"
    messages.info(request, mark_safe(msg))


retry_celery_task_admin_action.short_description = "Retry Task"


class TaakAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "titel",
        "taaktype",
        "taakstatus",
        "taakopdracht_status",
        "taakopdracht_status_code",
        "melding",
        "resolutie",
        "aangemaakt_op",
        "aangepast_op",
        "verwijderd_op",
        "taakopdracht",
        "taak_zoek_data",
    )
    readonly_fields = (
        "uuid",
        "verwijderd_op",
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
                    "taak_zoek_data",
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
                    "verwijderd_op",
                )
            },
        ),
    )
    search_fields = [
        "id",
        "uuid",
        "taakopdracht",
        "melding__bron_url",
    ]
    list_filter = (
        TaakstatusFilter,
        TaakopdrachtStatusFilter,
        TaakopdrachtStatusCodeFilter,
        ResolutieFilter,
        AfgeslotenOpFilter,
        TitelFilter,
    )
    raw_id_fields = (
        "melding",
        "taaktype",
        "taakstatus",
        "taak_zoek_data",
    )
    actions = [
        "update_taakopdracht_data",
        "update_taak_status_met_taakopdracht_status",
        "taakopdracht_notificatie",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "melding",
            "taaktype",
            "taakstatus",
            "taak_zoek_data",
        )

    def taakopdracht_status(self, obj):
        try:
            return obj.additionele_informatie["taakopdracht"]["status"]["naam"]
        except Exception:
            return "-"

    def taakopdracht_status_code(self, obj):
        try:
            return obj.additionele_informatie["taakopdracht_status_code"]
        except Exception:
            return "-"

    def update_taakopdracht_data(self, request, queryset):
        start_update_taakopdracht_data_for_taak_ids.delay(
            list(queryset.values_list(flat=True))
        )
        self.message_user(
            request, f"Updating taakopdracht for {queryset.count()} taken!"
        )

    def update_taak_status_met_taakopdracht_status(self, request, queryset):
        for taak in queryset:
            update_taak_status_met_taakopdracht_status.delay(taak.id)
        self.message_user(
            request,
            f"Updating taak status met taakopdracht status for {queryset.count()} taken!",
        )

    def taakopdracht_notificatie(self, request, queryset):
        for taak in queryset:
            task_taakopdracht_notificatie_voor_taak.delay(taak.id)
        self.message_user(
            request,
            f"Taakopdracht notificaties voor {queryset.count()} taken!",
        )

    update_taakopdracht_data.short_description = "update_taakopdracht_data"


class TaaktypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "omschrijving",
        "aangemaakt_op",
    )


class TakenAantalFilter(admin.SimpleListFilter):
    title = "taken_aantal"
    parameter_name = "taak"

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
            queryset.annotate(taken_aantal=Count("taak"))
            .order_by()
            .filter(**{value: 0})
        )


class TaakZoekDataAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "aangemaakt_op",
        "display_geometrie",
        "melding_alias",
        "taken_aantal",
    )
    readonly_fields = ("display_geometrie",)
    raw_id_fields = ("melding_alias",)
    list_filter = (TakenAantalFilter,)
    search_fields = [
        "melding_alias__bron_url",
    ]

    def taken_aantal(self, obj):
        return str(obj.taak.count())

    def display_geometrie(self, obj):
        # Convert GEOSGeometry to JSON string representation
        return str(obj.geometrie.geojson) if obj.geometrie else None

    display_geometrie.short_description = "Geometrie (JSON)"  # Customize column header

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "melding_alias",
        ).prefetch_related(
            "taak",
        )


class TaakgebeurtenisAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "aangemaakt_op",
        "gebruiker",
        "taakstatus",
        "resolutie",
        "taak",
        "omschrijving_intern",
        "notificatie_verstuurd",
    )
    raw_id_fields = (
        "taak",
        "taakstatus",
    )
    search_fields = [
        "taak__uuid",
    ]
    list_filter = ("notificatie_verstuurd",)


class TaakDeellinkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "gedeeld_door",
        "bezoekers",
        "signed_data",
        "taak",
    )


class TaakstatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "naam",
        "taak",
        "aangemaakt_op",
        "aangepast_op",
    )
    raw_id_fields = ("taak",)


class CustomTaskResultAdmin(TaskResultAdmin):
    list_filter = (
        "status",
        "date_created",
        "date_done",
        "periodic_task_name",
        "task_name",
    )
    actions = [
        retry_celery_task_admin_action,
    ]


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, CustomTaskResultAdmin)

admin.site.register(TaakZoekData, TaakZoekDataAdmin)
admin.site.register(Taak, TaakAdmin)
admin.site.register(Taaktype, TaaktypeAdmin)
admin.site.register(Taakgebeurtenis, TaakgebeurtenisAdmin)
admin.site.register(TaakDeellink, TaakDeellinkAdmin)
admin.site.register(Taakstatus, TaakstatusAdmin)
