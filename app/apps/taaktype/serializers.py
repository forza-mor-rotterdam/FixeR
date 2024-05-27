from apps.release_notes.models import Bijlage
from apps.taaktype.models import Afdeling, TaaktypeMiddel, TaaktypeVoorbeeldsituatie
from rest_framework import serializers
from rest_framework.reverse import reverse


class AfdelingLinksSerializer(serializers.Serializer):
    self = serializers.SerializerMethodField()

    def get_self(self, obj):
        return reverse(
            "v1:afdeling-detail",
            kwargs={"uuid": obj.uuid},
            request=self.context.get("request"),
        )


class AfdelingSerializer(serializers.ModelSerializer):
    _links = AfdelingLinksSerializer(source="*")

    class Meta:
        model = Afdeling
        fields = (
            "_links",
            "naam",
            "onderdeel",
        )


class TaaktypeMiddelLinksSerializer(serializers.Serializer):
    self = serializers.SerializerMethodField()

    def get_self(self, obj):
        return reverse(
            "v1:taaktype_middel-detail",
            kwargs={"uuid": obj.uuid},
            request=self.context.get("request"),
        )


class TaaktypeMiddelSerializer(serializers.ModelSerializer):
    _links = TaaktypeMiddelLinksSerializer(source="*")

    class Meta:
        model = TaaktypeMiddel
        fields = (
            "_links",
            "naam",
        )


class TaaktypeVoorbeeldsituatieLinksSerializer(serializers.Serializer):
    self = serializers.SerializerMethodField()
    taaktype = serializers.SerializerMethodField()

    def get_self(self, obj):
        return reverse(
            "v1:taaktype_voorbeeldsituatie-detail",
            kwargs={"uuid": obj.uuid},
            request=self.context.get("request"),
        )

    def get_taaktype(self, obj):
        return reverse(
            "v1:taaktype-detail",
            kwargs={"uuid": obj.taaktype.uuid},
            request=self.context.get("request"),
        )


class BijlagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bijlage
        fields = (
            "afbeelding",
            "afbeelding_verkleind",
        )


class TaaktypeVoorbeeldsituatieSerializer(serializers.ModelSerializer):
    _links = TaaktypeVoorbeeldsituatieLinksSerializer(source="*")
    bijlagen = BijlagenSerializer(many=True)

    class Meta:
        model = TaaktypeVoorbeeldsituatie
        fields = (
            "_links",
            "toelichting",
            "type",
            "bijlagen",
        )
