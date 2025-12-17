from django.db.models import OuterRef, Q, QuerySet, Subquery


class TaakQuerySet(QuerySet):
    def taken_lijst(self):
        from apps.taken.models import Taakgebeurtenis

        taakgebeurtenissen = Taakgebeurtenis.objects.filter(
            taak=OuterRef("pk")
        ).order_by("-aangemaakt_op")
        return (
            self.filter(
                verwijderd_op__isnull=True,
            )
            .select_related(
                "melding",
                "taaktype",
                "taakstatus",
            )
            .annotate(
                laatste_taakgebeurtenis_omschrijving_intern=Subquery(
                    taakgebeurtenissen.values("omschrijving_intern")[:1]
                ),
                laatste_taakgebeurtenis_gebruiker=Subquery(
                    taakgebeurtenissen.values("gebruiker")[:1]
                ),
            )
            .only(
                "id",
                "uuid",
                "titel",
                "taakopdracht",
                "afgesloten_op",
                "taaktype__uuid",
                "taaktype__omschrijving",
                "taakstatus__id",
                "taakstatus__naam",
                "taakstatus__aangemaakt_op",
                "melding__id",
                "melding__melding_uuid",
                "melding__locatie_type",
                "melding__bron_signaal_ids",
                "melding__straatnaam",
                "melding__plaatsnaam",
                "melding__huisnummer",
                "melding__huisletter",
                "melding__toevoeging",
                "melding__postcode",
                "melding__geometrie",
                "melding__wijknaam",
                "melding__buurtnaam",
                "melding__begraafplaats",
                "melding__grafnummer",
                "melding__locatie_verbose",
                "melding__vak",
                "melding__thumbnail_afbeelding_relative_url",
                "melding__response_json",
            )
        )

    def taken_zoeken(self, q):
        if not q:
            return self
        try:
            search_terms = q.split(",")
        except Exception:
            return self

        cleaned_search_terms = [
            "".join(
                [
                    char
                    for char in term.strip()
                    if char not in ["*", "(", ")", "?", "[", "]", "{", "}", "\\"]
                ]
            )
            for term in search_terms
        ]
        cleaned_search_terms = [term for term in cleaned_search_terms if term]
        combined_q = Q()
        for term in cleaned_search_terms:
            combined_q &= Q(melding__zoek_tekst__icontains=term)
        return self.filter(combined_q).distinct()
