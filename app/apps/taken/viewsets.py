from apps.taken.models import Taak, Taaktype
from apps.taken.serializers import TaakSerializer, TaaktypeSerializer
from rest_framework import mixins, viewsets


class TaaktypeViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Taaktype.objects.all()

    permission_classes = ()

    serializer_class = TaaktypeSerializer


class TaakViewSet(
    mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):

    queryset = Taak.objects.all()

    permission_classes = ()

    serializer_class = TaakSerializer
