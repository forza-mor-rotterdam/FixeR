from apps.taken.models import Taak, Taaktype
from apps.taken.serializers import TaakSerializer, TaaktypeSerializer
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response


class TaaktypeViewSet(viewsets.ReadOnlyModelViewSet):

    lookup_field = "uuid"
    queryset = Taaktype.objects.all()

    permission_classes = ()

    serializer_class = TaaktypeSerializer


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
