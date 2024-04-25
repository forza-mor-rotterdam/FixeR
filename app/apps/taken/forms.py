from apps.release_notes.models import Bijlage
from apps.services.onderwerpen import OnderwerpenService
from apps.taaktype.models import Afdeling, TaaktypeMiddel, TaaktypeVoorbeeldsituatie
from apps.taken.models import Taaktype
from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.forms import inlineformset_factory


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class BijlageForm(forms.ModelForm):
    bestand = forms.FileField(
        label="Afbeelding of GIF",
        required=False,
        widget=forms.widgets.FileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic, .gif",
                "data-action": "change->bijlagen#updateImageDisplay",
                "multiple": "multiple",
                "hideLabel": True,
            }
        ),
    )

    class Meta:
        model = Bijlage
        fields = (
            "id",
            "bestand",
        )


BijlageFormSet = generic_inlineformset_factory(
    Bijlage,
    fields=["bestand"],
    extra=0,
    can_delete=True,
    can_delete_extra=True,
)


class TaaktypeVoorbeeldsituatieFormNiet(forms.ModelForm):
    type_value = TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_NIET
    type = forms.CharField(
        widget=forms.HiddenInput(),
    )
    bestand = forms.FileField(
        label="Afbeelding of GIF",
        required=False,
        widget=forms.widgets.FileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic, .gif",
                "data-action": "change->bijlagen#updateImageDisplay",
                "multiple": "multiple",
                "hideLabel": True,
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"].initial = self.type_value
        if self.is_bound:
            self.bijlage_formset = BijlageFormSet(
                self.data,
                self.files,
                instance=self.instance,
                prefix=f"{self.prefix}_bijlage",
            )
        else:
            self.bijlage_formset = BijlageFormSet(
                instance=self.instance, prefix=f"{self.prefix}_bijlage"
            )

    class Meta:
        model = TaaktypeVoorbeeldsituatie
        fields = (
            "toelichting",
            "type",
        )


class TaaktypeVoorbeeldsituatieFormWel(TaaktypeVoorbeeldsituatieFormNiet):
    type_value = TaaktypeVoorbeeldsituatie.TypeOpties.WAAROM_WEL

    class Meta:
        model = TaaktypeVoorbeeldsituatie
        fields = (
            "toelichting",
            "type",
        )


class TaaktypeAanpassenForm(forms.ModelForm):
    toelichting = forms.CharField(
        label="Omschrijving",
        widget=forms.Textarea(
            attrs={
                "data-testid": "toelichting",
                "rows": "4",
            }
        ),
        required=True,
    )
    volgende_taaktypes = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        queryset=Taaktype.objects.filter(actief=True),
        label="Volgende taaktypes",
        required=False,
    )
    afdelingen = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        queryset=Afdeling.objects.all(),
        label="Afdelingen",
        required=False,
    )
    taaktypemiddelen = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        queryset=TaaktypeMiddel.objects.all(),
        label="Welk materieel is nodig om de taak af te handelen?",
        required=False,
    )
    gerelateerde_onderwerpen = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(),
        label="Gerelateerde onderwerpen",
        required=False,
    )
    actief = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Actief",
        required=False,
    )

    def __init__(self, *args, current_taaktype=None, **kwargs):
        super().__init__(*args, **kwargs)
        if current_taaktype:
            self.fields["volgende_taaktypes"].queryset = Taaktype.objects.filter(
                actief=True
            ).exclude(id=current_taaktype.id)

        # START gerelateerde_onderwerpen
        onderwerpen = OnderwerpenService().get_onderwerpen()
        onderwerpen_all = [
            [
                onderwerp.get("group_uuid"),
                onderwerp.get("_links", {}).get("self"),
                onderwerp.get("name", ""),
            ]
            for onderwerp in onderwerpen.get("results", [])
        ]
        groep_uuids = {
            onderwerp[0]: OnderwerpenService().get_groep(onderwerp[0]).get("name")
            for onderwerp in onderwerpen_all
        }
        onderwerpen_gegroepeerd = [
            [
                groep_naam,
                [
                    [onderwerp[1], onderwerp[2]]
                    for onderwerp in onderwerpen_all
                    if onderwerp[0] == groep_uuid
                ],
            ]
            for groep_uuid, groep_naam in groep_uuids.items()
        ]
        self.fields["gerelateerde_onderwerpen"].choices = onderwerpen_gegroepeerd
        # END gerelateerde_onderwerpen

    class Meta:
        model = Taaktype
        fields = (
            "omschrijving",
            "toelichting",
            "volgende_taaktypes",
            "afdelingen",
            "taaktypemiddelen",
            "gerelateerde_onderwerpen",
            "actief",
        )


class TaaktypeAanmakenForm(TaaktypeAanpassenForm):
    class Meta:
        model = Taaktype
        fields = (
            "omschrijving",
            "volgende_taaktypes",
            "afdelingen",
            "taaktypemiddelen",
            "gerelateerde_onderwerpen",
            "actief",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "omschrijving"
        ].help_text = "Omschrijf het taaktype zo concreet mogelijk. Formuleer de gewenste actie, bijvoorbeeld 'Grofvuil ophalen'."
        self.fields[
            "volgende_taaktypes"
        ].help_text = "Dit zijn taken die mogelijk uitgevoerd moeten worden nadat de taak is afgerond."


TaaktypeVoorbeeldsituatieNietFormSet = inlineformset_factory(
    Taaktype,
    TaaktypeVoorbeeldsituatie,
    form=TaaktypeVoorbeeldsituatieFormNiet,
    extra=1,
    can_delete=True,
    can_delete_extra=False,
)
TaaktypeVoorbeeldsituatieWelFormSet = inlineformset_factory(
    Taaktype,
    TaaktypeVoorbeeldsituatie,
    form=TaaktypeVoorbeeldsituatieFormWel,
    extra=1,
    can_delete=True,
    can_delete_extra=False,
)
