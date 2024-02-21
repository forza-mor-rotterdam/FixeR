import json

from apps.aliassen.models import MeldingAlias
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
            and melding_alias.response_json.get("locaties_voor_melding")
            and melding_alias.response_json.get("locaties_voor_melding")[0].get(
                "geometrie"
            )
        ):
            melding_alias.taken_voor_meldingalias.all().update(
                geometrie=GEOSGeometry(
                    json.dumps(
                        melding_alias.response_json.get("locaties_voor_melding")[0].get(
                            "geometrie"
                        )
                    )
                )
            )

        return Response({}, status=status.HTTP_200_OK)
