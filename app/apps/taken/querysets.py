from django.db.models import Case, CharField, F, Q, QuerySet, Value, When
from django.db.models.functions import Cast, Concat


class TaakQuerySet(QuerySet):
    def get_taken_recent(self, user):
        return self.filter(
            verwijderd_op__isnull=True,
        ).order_by("-aangemaakt_op")

    def annotate_adres(self):
        return self.annotate(
            huisnr_huisltr_toev=Concat(
                Cast(F("taak_zoek_data__huisnummer"), output_field=CharField()),
                F("taak_zoek_data__huisletter"),
                Case(
                    When(
                        Q(taak_zoek_data__toevoeging__isnull=False)
                        & ~Q(taak_zoek_data__toevoeging=""),
                        then=Concat(Value("-"), F("taak_zoek_data__toevoeging")),
                    ),
                    default=Value(""),
                ),
                output_field=CharField(),
            ),
            adres=Concat(
                F("taak_zoek_data__straatnaam"),
                Value(" "),
                F("huisnr_huisltr_toev"),
                output_field=CharField(),
            ),
        )
