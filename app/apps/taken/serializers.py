from apps.taken.models import Taak, Taaktype
from rest_framework import serializers
from rest_framework.reverse import reverse


class TaaktypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taaktype
        fields = (
            "omschrijving",
            "toelichting",
            "additionele_informatie",
        )


class TaakSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()
    taaktype = serializers.HyperlinkedRelatedField(
        view_name="taaktype-detail",
        queryset=Taaktype.objects.all(),
    )

    def get_link(self, obj):
        return reverse(
            "v1:taak-detail", kwargs={"pk": obj.id}, request=self.context.get("request")
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
