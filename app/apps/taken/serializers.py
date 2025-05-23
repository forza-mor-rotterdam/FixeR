from apps.instellingen.models import Instelling
from apps.taken.models import Taak, Taakgebeurtenis, Taakstatus, Taaktype
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.reverse import reverse
from utils.exceptions import UrlFout


class TaakstatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taakstatus
        fields = (
            "naam",
            "taak",
        )
        # read_only_fields = ("naam", "taak",)


class TaakgebeurtenisStatusSerializer(WritableNestedModelSerializer):
    bijlagen = serializers.ListSerializer(
        child=serializers.URLField(), required=False, allow_null=True
    )
    taakstatus = TaakstatusSerializer(required=True)
    resolutie = serializers.CharField(required=False, allow_null=True)
    uitvoerder = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Taakgebeurtenis
        fields = (
            "bijlagen",
            "taakstatus",
            "resolutie",
            "omschrijving_intern",
            "gebruiker",
            "uitvoerder",
        )


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
            "actief",
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
    _links = TaakLinksSerializer(source="*", read_only=True)
    melding = serializers.URLField()
    taaktype = serializers.HyperlinkedRelatedField(
        view_name="taaktype-detail",
        lookup_field="uuid",
        queryset=Taaktype.objects.all(),
    )
    taakstatus = TaakstatusSerializer(read_only=True)
    gebruiker = serializers.CharField(required=False, allow_null=True)
    omschrijving_intern = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    def validate_melding(self, data):
        is_url_valide = Instelling.actieve_instelling().valideer_url(
            "mor_core_basis_url", data
        )
        if not is_url_valide:
            raise UrlFout("melding")
        return data

    def validate_taakopdracht(self, data):
        is_url_valide = Instelling.actieve_instelling().valideer_url(
            "mor_core_basis_url", data
        )
        if not is_url_valide:
            raise UrlFout("taakopdracht")
        return data

    class Meta:
        model = Taak
        fields = (
            "_links",
            "id",
            "uuid",
            "taaktype",
            "titel",
            "bericht",
            "additionele_informatie",
            "taakstatus",
            "melding",
            "gebruiker",
            "taakopdracht",
            "omschrijving_intern",
            "aangemaakt_op",
        )
        read_only_fields = (
            "_links",
            "id",
            "uuid",
            "melding",
            "aangemaakt_op",
        )
        read_only_fields = ("_links",)
