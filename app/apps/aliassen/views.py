import json

from apps.aliassen.models import MeldingAlias
from apps.taken.models import TaakZoekData
from django.contrib.gis.geos import GEOSGeometry
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class MeldingNotificatieAPIView(APIView):
    def get(self, request):
        melding_alias = MeldingAlias.objects.filter(
            bron_url=request.GET.get("melding_url")
        ).first()
        if melding_alias:
            melding_alias.save()
        if (
            request.GET.get("notificatie_type") == "gebeurtenis_toegevoegd"
            and melding_alias
        ):
            location_data = melding_alias.response_json.get("locaties_voor_melding")[0]
            signalen = melding_alias.response_json.get("signalen_voor_melding", [])
            signaal_ids = [signaal.get("bron_signaal_id") for signaal in signalen]

            # Retrieve or create TaakZoekData instance based on the unique identifier
            taak_zoek_data_instance, _ = TaakZoekData.objects.update_or_create(
                melding_alias=melding_alias,
                defaults={
                    "geometrie": GEOSGeometry(
                        json.dumps(location_data.get("geometrie"))
                    )
                    if location_data.get("geometrie")
                    else None,
                    "locatie_type": location_data.get("locatie_type"),
                    "plaatsnaam": location_data.get("plaatsnaam"),
                    "straatnaam": location_data.get("straatnaam"),
                    "huisnummer": location_data.get("huisnummer"),
                    "huisletter": location_data.get("huisletter"),
                    "toevoeging": location_data.get("toevoeging"),
                    "postcode": location_data.get("postcode"),
                    "wijknaam": location_data.get("wijknaam"),
                    "buurtnaam": location_data.get("buurtnaam"),
                    "begraafplaats": location_data.get("begraafplaats"),
                    "grafnummer": location_data.get("grafnummer"),
                    "vak": location_data.get("vak"),
                    "lichtmast_id": location_data.get("lichtmast_id"),
                    "bron_signaal_ids": signaal_ids,
                },
            )
            # Associate the retrieved TaakZoekData instance with all Taak instances associated with the melding_alias
            for taak in melding_alias.taken_voor_meldingalias.all():
                taak.taak_zoek_data = taak_zoek_data_instance
                taak.save()

        return Response({}, status=status.HTTP_200_OK)
