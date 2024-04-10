from apps.release_notes.models import Bijlage
from apps.services.onderwerpen import OnderwerpenService
from apps.taaktype.models import Afdeling, TaaktypeMiddel, TaaktypeReden
from apps.taken.models import Taaktype
from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.forms import formset_factory, inlineformset_factory


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        print("MultipleFileField")
        print(single_file_clean)
        print(data)
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
                "data-bijlagen-target": "bijlagenExtra",
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
    # form=BijlageForm,
)


class TaaktypeRedenForm(forms.ModelForm):
    class Meta:
        model = TaaktypeReden
        fields = (
            "toelichting",
            "type",
            "taaktype",
        )


class TaaktypeRedenFormNiet(forms.ModelForm):
    type_value = TaaktypeReden.TypeOpties.WAAROM_NIET
    type = forms.CharField(
        widget=forms.HiddenInput(),
    )
    bijlage = MultipleFileField(
        label="Afbeelding of GIF",
        required=False,
        widget=MultipleFileInput(
            attrs={
                # "accept": ".jpg, .jpeg, .png, .heic, .gif",
                # "data-action": "change->bijlagen#updateImageDisplay",
                # "data-bijlagen-target": "bijlagenExtra",
                "multiple": "multiple",
                "hideLabel": True,
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        # print(args)
        # print("kwargs")
        # print(kwargs)

        super().__init__(*args, **kwargs)
        # print("self.data")
        # print(self.data)
        # print(self.is_bound)
        # print("dir(self)")
        # print(dir(self))
        self.fields["type"].initial = self.type_value

        # self.bijlage_formset = self.get_bijlagen_inline()(instance=self.instance)
        if self.is_bound:
            # print("file")
            # print(self.files)
            # print(self.instance.id)
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
        # print("self.bijlage_formset")
        # print(self.bijlage_formset)

    class Meta:
        model = TaaktypeReden
        fields = (
            "toelichting",
            "type",
            # "taaktype",
        )


class TaaktypeRedenFormWel(TaaktypeRedenFormNiet):
    type_value = TaaktypeReden.TypeOpties.WAAROM_WEL

    class Meta:
        model = TaaktypeReden
        fields = (
            "toelichting",
            "type",
            # "taaktype",
        )


class TaaktypeAanpassenForm(forms.ModelForm):
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
        label="Materieel",
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
            "gerelateerde_onderwerpen",
            "actief",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "omschrijving"
        ].help_text = "Omschrijf het taaktype zo concreet mogelijk. Formuleer de gewenste actie, bijvoorbeeld ‘Grofvuil ophalen’."
        self.fields[
            "volgende_taaktypes"
        ].help_text = "Dit zijn taken die mogelijk uitgevoerd moeten worden nadat de taak is afgerond."


# TaaktypeRedenNietFormSet = formset_factory(TaaktypeRedenFormNiet, extra=1)
# TaaktypeRedenWelFormSet = formset_factory(TaaktypeRedenFormWel, extra=1)
TaaktypeRedenFormSet = formset_factory(TaaktypeRedenForm, extra=1)

TaaktypeRedenNietFormSet = inlineformset_factory(
    Taaktype,
    TaaktypeReden,
    form=TaaktypeRedenFormNiet,
    extra=1,
    can_delete=True,
    can_delete_extra=False,
)
TaaktypeRedenWelFormSet = inlineformset_factory(
    Taaktype,
    TaaktypeReden,
    form=TaaktypeRedenFormWel,
    extra=1,
    can_delete=True,
    can_delete_extra=False,
)
