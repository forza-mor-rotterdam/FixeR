from apps.aliassen.models import MeldingAlias
from apps.aliassen.tasks import task_update_melding_alias_data
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class MeldingNotificatieAPIView(APIView):
    def get(self, request):
        melding_alias = MeldingAlias.objects.filter(
            bron_url=request.GET.get("melding_url")
        ).first()
        if melding_alias:
            task_update_melding_alias_data.delay(melding_alias.id)

        return Response({}, status=status.HTTP_200_OK)
