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
