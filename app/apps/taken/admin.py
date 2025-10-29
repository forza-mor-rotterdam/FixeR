from apps.taken.admin_filters import (
    AfgeslotenOpFilter,
    ResolutieFilter,
    TaakopdrachtStatusCodeFilter,
    TaakopdrachtStatusFilter,
    TaakstatusFilter,
    TitelFilter,
)
from apps.taken.models import Taak, TaakDeellink, Taakgebeurtenis, Taakstatus, Taaktype
from apps.taken.tasks import (
    start_update_taakopdracht_data_for_taak_ids,
    task_taakopdracht_notificatie_voor_taak,
    task_verwijderd_op_voor_afgeronde_taken_voor_taak_ids,
    update_taak_status_met_taakopdracht_status,
)
from django.contrib import admin, messages
from django.contrib.admin import DateFieldListFilter
from django.db.models import Count
from django.utils.safestring import mark_safe
from django_celery_beat.admin import PeriodicTaskAdmin
from django_celery_beat.models import PeriodicTask
from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import TaskResult
from utils.django_celery_results import restart_task


def retry_celery_task_admin_action(modeladmin, request, queryset):
    msg = ""
    for task_res in queryset:
        msg += f"{restart_task(task_res)}<br>"
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
    )
    list_editable = ("verwijderd_op",)
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
        ("afgesloten_op", DateFieldListFilter),
        ("verwijderd_op", DateFieldListFilter),
        ("aangemaakt_op", DateFieldListFilter),
    )
    raw_id_fields = (
        "melding",
        "taaktype",
        "taakstatus",
    )
    actions = [
        "update_taakopdracht_data",
        "update_taak_status_met_taakopdracht_status",
        "taakopdracht_notificatie",
        "verwijderd_op_voor_afgeronde_taken_voor_taak_ids",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "melding",
            "taaktype",
            "taakstatus",
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

    def verwijderd_op_voor_afgeronde_taken_voor_taak_ids(self, request, queryset):
        task_verwijderd_op_voor_afgeronde_taken_voor_taak_ids.delay(
            list(queryset.values_list("id", flat=True))
        )
        self.message_user(
            request,
            f"verwijderd_op_voor_afgeronde_taken_voor_taak_ids: aantal={queryset.count()}",
        )


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
    list_display = (
        "id",
        "task_id",
        "task_name",
        "status",
        "result",
        "date_created",
        "date_done",
        "date_started",
        "task_args",
        "task_kwargs",
    )
    list_filter = (
        "status",
        "date_created",
        "date_done",
        # "periodic_task_name",
        "task_name",
    )
    actions = [
        retry_celery_task_admin_action,
    ]


class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
    raw_id_fields = ("clocked",)


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, CustomTaskResultAdmin)

admin.site.unregister(PeriodicTask)
admin.site.register(PeriodicTask, CustomPeriodicTaskAdmin)

admin.site.register(Taak, TaakAdmin)
admin.site.register(Taaktype, TaaktypeAdmin)
admin.site.register(Taakgebeurtenis, TaakgebeurtenisAdmin)
admin.site.register(TaakDeellink, TaakDeellinkAdmin)
admin.site.register(Taakstatus, TaakstatusAdmin)
