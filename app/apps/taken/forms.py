from apps.taken.models import Taaktype
from django import forms


class TaaktypeAanpassenForm(forms.ModelForm):
    omschrijving = forms.CharField(
        label="Titel",
        widget=forms.TextInput(
            attrs={
                "data-testid": "titel",
            }
        ),
        required=True,
    )
    toelichting = forms.CharField(
        label="Omschrijving",
        widget=forms.Textarea(
            attrs={
                "data-testid": "omschrijving",
                "rows": "8",
            }
        ),
        required=False,
    )
    actief = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Actief",
        required=False,
    )
    redirect_field = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = Taaktype
        fields = (
            "omschrijving",
            "toelichting",
            "actief",
        )


class TaaktypeAanmakenForm(TaaktypeAanpassenForm):
    class Meta:
        model = Taaktype
        fields = (
            "omschrijving",
            "toelichting",
            "actief",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "omschrijving"
        ].help_text = "Omschrijf het taaktype zo concreet mogelijk. Formuleer de gewenste actie, bijvoorbeeld ‘Grofvuil ophalen’."
