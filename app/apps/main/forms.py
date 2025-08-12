import logging

from apps.taken.filters import FILTERS
from apps.taken.models import Taak
from django import forms

logger = logging.getLogger(__name__)


class RadioSelect(forms.RadioSelect):
    option_template_name = "widgets/radio_option.html"


class RadioSelectSimple(forms.RadioSelect):
    option_template_name = "widgets/radio_option_simple.html"


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
            result = [single_file_clean(data, initial)]
        return result


class TaakBehandelForm(forms.Form):
    resolutie = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
                "data-action": "change->incidentHandleForm#onChangeResolution",
                "hideLabel": True,
            }
        ),
        label="Is de taak afgehandeld?",
        choices=Taak.behandel_opties(),
        required=True,
    )

    bijlagen = MultipleFileField(
        widget=MultipleFileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic",
                "data-action": "change->bijlagen#updateImageDisplay",
                "data-bijlagen-target": "bijlagenExtra",
                "hideLabel": True,
                "class": "file-upload-input",
            }
        ),
        label="Foto's",
        help_text="Help je collega’s en de melder door een volledig beeld van de situatie te geven.",
        required=False,
    )

    omschrijving_intern = forms.CharField(
        label="Interne opmerking",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "data-testid": "information",
                "rows": "4",
                "data-meldingbehandelformulier-target": "internalText",
                "maxlength": "5000",
            }
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        volgende_taaktypes = kwargs.pop("volgende_taaktypes", None)
        super().__init__(*args, **kwargs)

        # Vraag Vervolgtaak? Altijd tonen bij de 3 resoluties (afgehandeld, niet afgehandeld, niets aangetroffen)
        # Alle vervolgtaken als checkboxes weergeven?
        # Bij resolutie 3 ("kan  niet") is interne opmerking VERPLICHT, met tekst "Waarom kan de taak niet worden afgerond?"
        if volgende_taaktypes:
            self.fields["nieuwe_taak"] = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                label="",
                choices=volgende_taaktypes,
                required=False,
            )
            # Omschrijving nieuwe taak nodig?
            self.fields["omschrijving_nieuwe_taak"] = forms.CharField(
                label="Toelichting",
                help_text="Deze tekst wordt niet naar de melder verstuurd.",
                widget=forms.Textarea(
                    attrs={
                        "class": "form-control",
                        "rows": "4",
                    }
                ),
                required=False,
            )


class SorteerFilterForm(forms.Form):
    sorteer_opties = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "data-action": "sorteerFilter#onChangeHandler",
                "data-sorteerFilter-target": "sorteerField",
            }
        ),
        choices=(
            ("Datum-reverse", "Datum (nieuwste bovenaan)"),
            ("Datum", "Datum (oudste bovenaan)"),
            ("Afstand", "Afstand"),
            ("Adres", "T.h.v. Adres (a-z)"),
            ("Adres-reverse", "T.h.v. Adres (z-a)"),
            ("Postcode", "Postcode (1000-9999)"),
            ("Postcode-reverse", "Postcode (9999-1000)"),
        ),
    )

    def __init__(self, *args, **kwargs):
        gebruiker = kwargs.pop("gebruiker", None)
        try:
            is_benc = gebruiker.profiel.context.template == "benc"
        except Exception:
            is_benc = False

        super().__init__(*args, **kwargs)
        benc_sorteer_opties_choices = ("Datum-reverse", "Datum")
        sorteer_opties_choices = [
            ("Datum-reverse", "Datum (nieuwste bovenaan)"),
            ("Datum", "Datum (oudste bovenaan)"),
            ("Afstand", "Afstand"),
            ("Adres", "T.h.v. Adres (a-z)"),
            ("Adres-reverse", "T.h.v. Adres (z-a)"),
            ("Postcode", "Postcode (1000-9999)"),
            ("Postcode-reverse", "Postcode (9999-1000)"),
        ]
        self.fields["sorteer_opties"].choices = [
            optie
            for optie in sorteer_opties_choices
            if (is_benc and optie[0] in benc_sorteer_opties_choices) or not is_benc
        ]


class KaartModusForm(forms.Form):
    kaart_modus = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
                "data-action": "click->kaartModus#kaartModusOptionClickHandler",
                "hideLabel": True,
            }
        ),
        choices=(
            ("volgen", "Volg mijn locatie"),
            ("toon_alles", "Toon alle taken"),
        ),
    )


class TaakFilterCheckboxSelectMultiple(forms.widgets.CheckboxSelectMultiple):
    template_name = "taken/overzicht/filter_field_widget.html"
    option_template_name = "taken/overzicht/filter_field_widget_option.html"


class TakenLijstFilterForm(forms.Form):
    filters = [
        "taken",
        "buurt",
        "begraafplaats",
        "taak_status",
    ]

    def __init__(self, *args, **kwargs):
        profiel = kwargs.pop("profiel", None)
        super().__init__(*args, **kwargs)

        filters = [
            f(profiel=profiel)
            for f in FILTERS
            if f.key() in profiel.context.filters.get("fields", [])
        ]

        for f in filters:
            self.fields[f.key()] = forms.MultipleChoiceField(
                widget=TaakFilterCheckboxSelectMultiple(
                    attrs={
                        "class": "form-check-input filter--taken",
                        "sub_label": f.sub_label(),
                    }
                ),
                template_name=f.field_template(),
                choices=f.choices(),
                required=False,
                label=f.label(),
            )
        print(self.fields.keys())
