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
                OR NOT ("aliassen_meldingalias"."response_status_code" = ANY(ARRAY[200, 404])) \
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
                AND ("django_celery_results_taskresult"."status" = ANY(ARRAY[\'FAILURE\', \'SUCCESS\'])  \
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
