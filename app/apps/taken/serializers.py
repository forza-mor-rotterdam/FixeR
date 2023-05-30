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


class TaakSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()
    melding = serializers.URLField()
    taaktype = serializers.HyperlinkedRelatedField(
        view_name="taaktype-detail",
        lookup_field="uuid",
        queryset=Taaktype.objects.all(),
    )

    def get_link(self, obj):
        return reverse(
            "v1:taak-detail",
            kwargs={"uuid": obj.uuid},
            request=self.context.get("request"),
        )

    class Meta:
        model = Taak
        fields = (
            "link",
            "titel",
            "bericht",
            "additionele_informatie",
            "taaktype",
            "melding",
        )
