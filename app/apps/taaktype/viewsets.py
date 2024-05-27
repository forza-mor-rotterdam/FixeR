from apps.taaktype.models import Afdeling, TaaktypeMiddel, TaaktypeVoorbeeldsituatie
from apps.taaktype.serializers import (
    AfdelingSerializer,
    TaaktypeMiddelSerializer,
    TaaktypeVoorbeeldsituatieSerializer,
)
from rest_framework import viewsets


class AfdelingViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "uuid"
    queryset = Afdeling.objects.all().order_by("naam")
    permission_classes = ()
    serializer_class = AfdelingSerializer


class TaaktypeMiddelViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "uuid"
    queryset = TaaktypeMiddel.objects.all().order_by("naam")
    permission_classes = ()
    serializer_class = TaaktypeMiddelSerializer


class TaaktypeVoorbeeldsituatieViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "uuid"
    queryset = TaaktypeVoorbeeldsituatie.objects.all()
    permission_classes = ()
    serializer_class = TaaktypeVoorbeeldsituatieSerializer
