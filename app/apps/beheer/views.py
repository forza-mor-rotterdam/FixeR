import json
import logging
import uuid
from collections import Counter
from functools import reduce
from operator import or_

from apps.beheer.forms import (
    AchtegrondTasksAanmakenForm,
    TaakgebeurtenisNotificatieIssuesForm,
)
from apps.taken.models import Taak, Taakgebeurtenis
from apps.taken.tasks import (
    TASK_LOCK_KEY_NOTFICATIES_VOOR_TAKEN,
    task_taakopdracht_notificatie_voor_taakgebeurtenissen,
)
from celery import states
from config.celery import app
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView

logger = logging.getLogger(__name__)


@login_required
@permission_required("authorisatie.beheer_bekijken", raise_exception=True)
def beheer(request):
    return render(
        request,
        "beheer/beheer.html",
        {},
    )


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.beheer_bekijken", raise_exception=True),
    name="dispatch",
)
class MORCoreNotificatieStatusOverzicht(FormView):
    template_name = "beheer/mor_core_notificatie_status_overzicht.html"
    form_class = AchtegrondTasksAanmakenForm

    def get_taken(self):
        taken = Taak.objects.all()
        taken = taken.annotate(
            taakgebeurtenis_aantal_notificatie_niet_vertuurd=Count(
                "taakgebeurtenissen_voor_taak",
                filter=Q(taakgebeurtenissen_voor_taak__notificatie_verstuurd=False),
            ),
            taakgebeurtenis_aantal=Count("taakgebeurtenissen_voor_taak"),
            taakgebeurtenis_ids=ArrayAgg(
                "taakgebeurtenissen_voor_taak__id",
                filter=Q(taakgebeurtenissen_voor_taak__notificatie_verstuurd=False),
            ),
        )
        taken = taken.filter(taakgebeurtenis_aantal_notificatie_niet_vertuurd__gt=0)
        celery_inspect = app.control.inspect()

        tasks_states = {
            "active": "Bezig: met verwerken",
            "reserved": "Bezig: in wachtrij",
            "scheduled": "Bezig: retry",
        }
        taakgebeurtenis_tasks = {
            task.get("args", task.get("request", {}).get("args"))[0]: task
            | {
                "state": tasks_states[state],
            }
            for state in tasks_states.keys()
            for _, tasks in getattr(celery_inspect, state)().items()
            for task in tasks
            if task.get("name", task.get("request", {}).get("name"))
            == "apps.taken.tasks.task_taakopdracht_notificatie"
        }
        logger.info("Celery statussen")
        logger.info(json.dumps(taakgebeurtenis_tasks, indent=4))
        taken = [
            taak.__dict__
            | {
                "taakgebeurtenissen": dict(
                    Counter(
                        [
                            taakgebeurtenis_tasks.get(
                                taakgebeurtenis_id, {"state": "Niet bezig"}
                            )["state"]
                            for taakgebeurtenis_id in taak.taakgebeurtenis_ids
                        ]
                    )
                )
            }
            | {
                "taakgebeurtenissen_niet_bezig": [
                    taakgebeurtenis_id
                    for taakgebeurtenis_id in taak.taakgebeurtenis_ids
                    if not taakgebeurtenis_tasks.get(taakgebeurtenis_id)
                ]
            }
            for taak in taken
        ]
        return {
            "taken": taken,
            "taakgebeurtenissen_niet_bezig": [
                str(taakgebeurtenis_id)
                for taak in taken
                for taakgebeurtenis_id in taak["taakgebeurtenissen_niet_bezig"]
            ],
        }

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {
                "taakgebeurtenis_ids": ",".join(
                    self.get_taken()["taakgebeurtenissen_niet_bezig"]
                ),
            }
        )
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bezig_versturen_van_notificaties = cache.get(
            TASK_LOCK_KEY_NOTFICATIES_VOOR_TAKEN
        )
        context.update(
            {
                "bezig_versturen_van_notificaties": bezig_versturen_van_notificaties,
            }
        )
        context.update(self.get_taken())
        return context

    def form_valid(self, form):
        # app.control.purge()
        task_taakopdracht_notificatie_voor_taakgebeurtenissen.delay(
            form.cleaned_data["taakgebeurtenis_ids"].split(",")
        )
        import time

        time.sleep(2)
        return super().form_invalid(form)


class TaakgebeurtenisNotificatieIssuesView(PermissionRequiredMixin, FormView):
    permission_required = "authorisatie.taakgebeurtenis_notificatie_issues_aanpassen"
    template_name = "beheer/taakgebeurtenis_notificatie_issues/lijst.html"
    form_class = TaakgebeurtenisNotificatieIssuesForm
    success_url = reverse_lazy("taakgebeurtenis_notificatie_issues")
    taakopdracht_choices = []
    page_size = 100

    def dispatch(self, request, *args, **kwargs):
        self.taakgebeurtenissen = (
            Taakgebeurtenis.objects.select_related(
                "taak__melding", "task_taakopdracht_notificatie"
            )
            .filter(
                Q(notificatie_verstuurd=False)
                & (
                    Q(task_taakopdracht_notificatie__isnull=True)
                    | Q(
                        task_taakopdracht_notificatie__status__in=[
                            states.FAILURE,
                            states.SUCCESS,
                        ]
                    )
                )
            )
            .only(
                "taak__melding__melding_uuid",
                "taak__uuid",
                "taak__titel",
                "uuid",
                "notificatie_error",
                "task_taakopdracht_notificatie__status",
            )
        )

        if self.request.session.get("taakgebeurtenis_notificatie_issues__q"):
            q = str(self.request.session.get("taakgebeurtenis_notificatie_issues__q"))
            filters = {
                "taak__titel__icontains": q,
                "notificatie_error__icontains": q,
            }
            try:
                q_uuid = uuid.UUID(q)
                filters.update(
                    {
                        "uuid": q_uuid,
                        "taak__uuid": q_uuid,
                        "taak__melding__melding_uuid": q_uuid,
                    }
                )
            except Exception:
                ...

            q_objects = (Q(**{k: v}) for k, v in filters.items())
            query = reduce(or_, q_objects)
            self.taakgebeurtenissen = self.taakgebeurtenissen.filter(query)

        self.initial.update(
            {"q": self.request.session.get("taakgebeurtenis_notificatie_issues__q")}
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "taakgebeurtenissen_choices": self.taakgebeurtenissen,
            }
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "count": self.taakgebeurtenissen.count(),
            }
        )
        return context

    def form_valid(self, form):
        q = form.cleaned_data["q"]
        taakgebeurtenissen = form.cleaned_data["taakgebeurtenissen"]
        if taakgebeurtenissen:
            start_task_taakopdracht_notificaties_mislukt = [
                result
                for result in [
                    taakgebeurtenis.start_task_taakopdracht_notificatie()
                    for taakgebeurtenis in taakgebeurtenissen
                ]
                if result
            ]
            getattr(
                messages,
                "warning" if start_task_taakopdracht_notificaties_mislukt else "info",
            )(
                self.request,
                f"{len(taakgebeurtenissen) - len(start_task_taakopdracht_notificaties_mislukt)} van de {len(taakgebeurtenissen)} notificaties zijn verstuurd",
            )

        if q:
            self.request.session["taakgebeurtenis_notificatie_issues__q"] = q
        elif self.request.session.get("taakgebeurtenis_notificatie_issues__q"):
            del self.request.session["taakgebeurtenis_notificatie_issues__q"]

        return super().form_valid(form)
