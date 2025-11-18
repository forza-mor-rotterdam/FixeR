import logging

from apps.aliassen.models import MeldingAlias
from apps.instellingen.models import Instelling
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.exceptions import UrlFout

logger = logging.getLogger(__name__)


class MeldingNotificatieAPIView(APIView):
    def get(self, request):
        melding_url = request.GET.get("melding_url")
        is_url_valide = Instelling.actieve_instelling().valideer_url(
            "mor_core_basis_url", melding_url
        )
        if not is_url_valide:
            raise UrlFout("melding")

        melding_alias, aangemaakt = MeldingAlias.objects.get_or_create(
            bron_url=melding_url
        )
        melding_alias.start_task_update_melding_alias_data()

        return Response({}, status=status.HTTP_200_OK)
