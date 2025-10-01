import logging

from apps.taken.filters import FILTERS
from apps.taken.models import Taak
from deepdiff import DeepDiff
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


class TaakFilterCheckboxSelectMultiple(forms.widgets.CheckboxSelectMultiple):
    template_name = "taken/overzicht/filter_field_widget.html"
    option_template_name = "taken/overzicht/filter_field_widget_option.html"


class KaartModusRadioSelect(forms.RadioSelect):
    template_name = "taken/overzicht/kaart_modus_widget.html"


class TakenLijstFilterForm(forms.Form):
    gps = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                "data-action": "taken-overzicht#onGPSChangeHandler",
                "data-main-target": "gpsField",
                "data-taken-overzicht-target": "gpsField",
            }
        ),
        required=False,
    )
    page = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                "data-taken-overzicht-target": "pageField",
                "data-action": "taken-overzicht#onPageChangeHandler",
            }
        ),
        required=False,
    )
    q = forms.CharField(
        widget=forms.SearchInput(
            attrs={
                "class": "form-control search",
                "maxlength": 50,
                "placeholder": "Zoek op straatnaam of MeldR-nummer",
                "data-taken-overzicht-target": "zoekField",
                "data-action": "taken-overzicht#onSearchChangeHandler",
            }
        ),
        required=False,
    )
    sorteer_opties = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "data-action": "taken-overzicht#onSortingChangeHandler",
                "data-main-target": "sorteerField",
                "data-taken-overzicht-target": "sorteerField",
            }
        ),
        choices=(),
        required=False,
    )
    kaart_modus = forms.ChoiceField(
        widget=KaartModusRadioSelect(
            attrs={
                "class": "list--form-radio-input",
                "data-action": "click->taken-overzicht#kaartModusOptionClickHandler",
                "data-taken-overzicht-target": "kaartModusOption",
                "data-main-target": "kaartModusOption",
                "hideLabel": True,
            }
        ),
        choices=(
            ("volgen", "Volg mijn locatie"),
            ("toon_alles", "Toon alle taken"),
        ),
        required=False,
    )
    filters = [
        "taken",
        "buurt",
        "begraafplaats",
        "taak_status",
    ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        profiel = self.request.user.profiel
        super().__init__(*args, **kwargs)

        if self.request.session.get("q"):
            del self.request.session["q"]

        for f in profiel.taken_filters:
            self.fields[f.key()] = forms.MultipleChoiceField(
                widget=TaakFilterCheckboxSelectMultiple(
                    attrs={
                        "class": "form-check-input filter--taken",
                        "sub_label": f.sub_label(),
                        "data-action": "taken-overzicht#onChangeFilter",
                        "data-taken-overzicht-target": "filterInput",
                    }
                ),
                template_name=f.field_template(),
                choices=f.choices(),
                required=False,
                label=f.label(),
            )
        self.fields["sorteer_opties"].choices = profiel.taken_sorting_choices

    def filter_fields(self):
        profiel = self.request.user.profiel
        return [
            field
            for field in self
            if field.name in [f.key() for f in profiel.taken_filters]
        ]

    def active_filter_options(self):
        profiel = self.request.user.profiel
        active_profiel_selected_filter_opties = {
            k: v for k, v in profiel.taken_filter_data.items() if v
        }
        return [
            (
                f.key(),
                self.fields[f.key()].label,
                f(profiel=profiel).active_choices(
                    active_profiel_selected_filter_opties[f.key()]
                ),
            )
            for f in FILTERS
            if f.key() in profiel.context.filters.get("fields", [])
            and f.key() in active_profiel_selected_filter_opties.keys()
        ]

    def changed_fields(self):
        return {
            f"{field}_changed": getattr(self, f"{field}_changed")
            for field in [
                "filters",
                "sorteer_opties",
                "q",
                "page",
                "gps",
            ]
            if hasattr(self, f"{field}_changed")
        }

    def save(self):
        profiel = self.request.user.profiel
        data = self.cleaned_data
        status = "nieuw"

        actieve_filters = {f.key(): data.get(f.key()) for f in profiel.taken_filters}

        # changed fields
        self.filters_changed = bool(
            DeepDiff(
                profiel.taken_filter_validated_data,
                {k: v for k, v in actieve_filters.items() if v},
            )
        )
        self.sorteer_opties_changed = data.get(
            "sorteer_opties"
        ) != profiel.ui_instellingen.get("sortering")
        self.q_changed = data.get("q") != self.request.session.get("q")
        self.page_changed = data.get("page", "") != self.request.session.get("page", "")
        self.gps_changed = data.get("gps", "") != self.request.session.get("gps", "")

        # update profiel fields
        profiel.filters.update({status: actieve_filters})
        profiel.ui_instellingen.update(
            {
                "sortering": data.get("sorteer_opties", "Datum-reverse"),
            }
        )
        profiel.save()
        # update session fields
        self.request.session["q"] = data.get("q", "")
        self.request.session["page"] = data.get("page", "")
        self.request.session["gps"] = data.get("gps", "")
