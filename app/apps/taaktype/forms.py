from apps.taaktype.models import Afdeling, TaaktypeMiddel
from django import forms


class AfdelingAanpassenForm(forms.ModelForm):
    class Meta:
        model = Afdeling
        fields = ("naam", "onderdeel")


class AfdelingAanmakenForm(AfdelingAanpassenForm):
    class Meta:
        model = Afdeling
        fields = ("naam", "onderdeel")


class TaaktypeMiddelAanpassenForm(forms.ModelForm):
    class Meta:
        model = TaaktypeMiddel
        fields = ("naam",)


class TaaktypeMiddelAanmakenForm(TaaktypeMiddelAanpassenForm):
    class Meta:
        model = TaaktypeMiddel
        fields = ("naam",)
