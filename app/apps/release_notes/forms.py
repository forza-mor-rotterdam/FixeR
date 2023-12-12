import logging

from django import forms

from .models import ReleaseNote

logger = logging.getLogger(__name__)


class ReleaseNoteAanpassenForm(forms.ModelForm):
    titel = forms.CharField(
        label="Titel",
        widget=forms.TextInput(),
    )
    beschrijving = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 10,
                "cols": 38,
                "style": "resize: none;",
                "name": "beschrijving",
            }
        ),
        label="Beschrijving",
        max_length=500,
    )

    versie = forms.CharField(label="Versie", widget=forms.TextInput(), required=False)

    publicatie_datum = forms.DateTimeField(
        label="Publicatie datum",
        required=False,
    )

    afbeelding = forms.ImageField(
        label="Afbeelding of GIF",
        required=False,
        widget=forms.widgets.FileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic",
                "data-action": "change->bijlagen#updateImageDisplay",
                "data-bijlagen-target": "bijlagenNieuw",
            }
        ),
    )

    class Meta:
        model = ReleaseNote
        fields = ["titel", "beschrijving", "versie", "publicatie_datum", "afbeelding"]


class ReleaseNoteAanmakenForm(ReleaseNoteAanpassenForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields[
        #     "titel"
        # ].help_text = "Geef een titel op voor de standaard tekst."
        # self.fields[
        #     "tekst"
        # ].help_text = "Geef een standaard tekst op van maximaal 2000 tekens. Deze tekst kan bij het afhandelen van een melding aangepast worden."


class ReleaseNoteSearchForm(forms.Form):
    search = forms.CharField(
        label="Zoeken",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Zoek release note"}),
    )
