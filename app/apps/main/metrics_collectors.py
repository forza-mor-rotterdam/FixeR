from django.db import connections
from prometheus_client.core import CounterMetricFamily


class CustomCollector(object):
    def __init__(self):
        ...

    def dictfetchall(self, cursor):
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def collect(self):
        yield self.collect_meldingalias_data_update_issues_metrics()
        yield self.collect_taakgebeurtenis_notificatie_issues_metrics()
        yield self.collect_celery_task_results()

    def collect_meldingalias_data_update_issues_metrics(self):
        c = CounterMetricFamily(
            "fixer_meldingalias_data_update_issues_total",
            "De aantallen van MeldingAliassen met problemen met updaten van data vanuit MORCore",
            labels=[],
        )
        results = []

        sql = 'SELECT \
            COUNT(*) AS "count" \
            FROM "aliassen_meldingalias" \
            WHERE  \
                "aliassen_meldingalias"."locatie_type" IS NULL  \
                OR NOT ("aliassen_meldingalias"."response_status_code" IN (200, 404)) \
        '

        with connections["default"].cursor() as cursor:
            cursor.execute(sql)
            results = self.dictfetchall(cursor)

        c.add_metric(
            (),
            results[0].get("count") if results else 0,
        )
        return c

    def collect_taakgebeurtenis_notificatie_issues_metrics(self):
        c = CounterMetricFamily(
            "fixer_taakgebeurtenis_notificatie_issues_total",
            "De aantallen van Taakgebeurtenissen met problemen met versturen van de notificatie naar MORCore",
            labels=[],
        )
        results = []

        sql = 'SELECT \
            COUNT(*) AS "count" \
            FROM "taken_taakgebeurtenis" \
                LEFT OUTER JOIN "django_celery_results_taskresult" ON ("taken_taakgebeurtenis"."task_taakopdracht_notificatie_id" = "django_celery_results_taskresult"."id") \
                JOIN "taken_taakstatus" ON ("taken_taakgebeurtenis"."taakstatus_id" = "taken_taakstatus"."id") \
            WHERE  \
                "taken_taakgebeurtenis"."notificatie_verstuurd" IS FALSE  \
                AND "taken_taakstatus"."naam" = \'voltooid\'  \
                AND ("django_celery_results_taskresult"."status" IN (\'FAILURE\', \'SUCCESS\')  \
                OR "taken_taakgebeurtenis"."task_taakopdracht_notificatie_id" IS NULL)  \
        '

        with connections["default"].cursor() as cursor:
            cursor.execute(sql)
            results = self.dictfetchall(cursor)

        c.add_metric(
            (),
            results[0].get("count") if results else 0,
        )
        return c

    def collect_celery_task_results(self):
        c = CounterMetricFamily(
            "fixer_celery_task_results_issues_total",
            "Aantallen van Celery TaskResult instanties per task_name en status, met status FAILED of RETRY",
            labels=[
                "task_name",
                "status",
            ],
        )
        total_objects = []

        sql = '\
            SELECT \
                "django_celery_results_taskresult"."task_name", \
                "django_celery_results_taskresult"."status", \
                COUNT("django_celery_results_taskresult"."task_id") AS "count" \
            FROM "django_celery_results_taskresult" \
            WHERE \
                "django_celery_results_taskresult"."status" IN (\'FAILURE\', \'RETRY\') \
                AND "django_celery_results_taskresult"."task_name" IS NOT NULL \
            GROUP BY \
                "django_celery_results_taskresult"."status", \
                "django_celery_results_taskresult"."task_name" \
            ORDER BY \
                "django_celery_results_taskresult"."status", \
                "django_celery_results_taskresult"."task_name" ASC;\
        '

        with connections["default"].cursor() as cursor:
            cursor.execute(sql)
            total_objects = self.dictfetchall(cursor)

        for obj in total_objects:
            c.add_metric(
                (
                    obj["task_name"],
                    obj["status"],
                ),
                obj["count"],
            )

        if not total_objects:
            c.add_metric(
                (),
                0,
            )

        return c
