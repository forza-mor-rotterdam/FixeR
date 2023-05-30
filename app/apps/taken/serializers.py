from apps.taken.models import Taak, Taaktype
from rest_framework import serializers
from rest_framework.reverse import reverse


class TaaktypeLinksSerializer(serializers.Serializer):
    self = serializers.SerializerMethodField()

    def get_self(self, obj):
        return reverse(
            "v1:taaktype-detail",
            kwargs={"uuid": obj.uuid},
            request=self.context.get("request"),
        )


class TaaktypeSerializer(serializers.ModelSerializer):
    _links = TaaktypeLinksSerializer(source="*")

    class Meta:
        model = Taaktype
        fields = (
            "_links",
            "uuid",
            "omschrijving",
            "toelichting",
            "additionele_informatie",
        )
        read_only_fields = ("_links",)


class TaakLinksSerializer(serializers.Serializer):
    self = serializers.SerializerMethodField()

    def get_self(self, obj):
        return reverse(
            "v1:taak-detail",
            kwargs={"uuid": obj.uuid},
            request=self.context.get("request"),
        )


class TaakSerializer(serializers.ModelSerializer):
    _links = TaakLinksSerializer(source="*")
    melding = serializers.URLField()
    taaktype = serializers.HyperlinkedRelatedField(
        view_name="taaktype-detail",
        lookup_field="uuid",
        queryset=Taaktype.objects.all(),
    )

    class Meta:
        model = Taak
        fields = (
            "_links",
            "titel",
            "bericht",
            "additionele_informatie",
            "taaktype",
            "melding",
        )
