from apps.taken.models import Taaktype
from django import forms


class TaaktypeAanpassenForm(forms.ModelForm):
    volgende_taaktypes = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
            }
        ),
        queryset=Taaktype.objects.filter(actief=True),
        label="Volgende taaktypes",
        required=False,
    )
    actief = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
        label="Actief",
        required=False,
    )

    class Meta:
        model = Taaktype
        fields = (
            "omschrijving",
            "volgende_taaktypes",
            "actief",
        )


class TaaktypeAanmakenForm(TaaktypeAanpassenForm):
    class Meta:
        model = Taaktype
        fields = (
            "omschrijving",
            "volgende_taaktypes",
            "actief",
        )
