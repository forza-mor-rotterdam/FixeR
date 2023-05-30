from apps.taken.models import Taak, Taaktype
from apps.taken.serializers import TaakSerializer, TaaktypeSerializer
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class TaaktypeViewSet(viewsets.ReadOnlyModelViewSet):

    lookup_field = "uuid"
    queryset = Taaktype.objects.all()

    permission_classes = ()

    serializer_class = TaaktypeSerializer

    @extend_schema(
        description="Taaktypes voor melding",
        responses={status.HTTP_200_OK: TaaktypeSerializer},
        parameters=None,
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="voor_melding",
        serializer_class=TaaktypeSerializer,
    )
    def voor_melding(self, request, melding_url):
        """
        minimale implementatie: geef alleen taaktypes terug voor deze melding, waar nog geen openstaande taken voor zijn.
        """
        taaktypes = (
            Taak.objects.filter(melding=melding_url)
            .values_list("taaktype", flat=True)
            .distinct()
        )
        serializer = TaaktypeSerializer(taaktypes)
        return Response(serializer.data)


class TaakViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = Taak.objects.all()

    permission_classes = ()

    serializer_class = TaakSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        taak = Taak.acties.aanmaken(serializer)

        serializer = self.get_serializer(taak, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
