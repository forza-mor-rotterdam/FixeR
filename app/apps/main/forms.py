from django import forms

HANDLED_OPTIONS = (
    (
        "O",
        "Opgeruimd",
        "De gemeente heeft deze melding in behandeling genomen en gaat ermee aan de slag. De melding is daarom afgesloten.",
        "-1",
    ),
    (
        "N",
        "Niets aangetroffen",
        "In uw melding heeft u een locatie genoemd. Op deze locatie hebben wij echter niets aangetroffen. We sluiten daarom uw melding.",
        "3",
    ),
    (
        "N",
        "De locatie is niet bereikbaar",
        "In uw melding heeft u een locatie genoemd. We kunnen deze locatie echter niet bereiken. We sluiten daarom uw melding.",
        "4",
    ),
    (
        "N",
        "De melding is niet voor mij",
        "",
        "5",
    ),
    (
        "N",
        "De gemeente gaat hier niet over",
        "Helaas valt uw melding niet onder verantwoordelijkheid van de gemeente. We sluiten daarom uw melding.",
        "1",
    ),
)
TAAK_BEHANDEL_OPTIES = (
    (
        "ja",
        "Ja",
        "We zijn met uw melding aan de slag gegaan en hebben het probleem opgelost.",
        "voltooid",
        "opgelost",
    ),
    (
        "nee",
        "Nee",
        "We zijn met uw melding aan de slag gegaan, maar konden het probleem helaas niet oplossen. Want...",
        "voltooid",
        "niet_opgelost",
    ),
)

TAAK_BEHANDEL_STATUS = {bo[0]: bo[3] for bo in TAAK_BEHANDEL_OPTIES}
TAAK_BEHANDEL_RESOLUTIE = {bo[0]: bo[4] for bo in TAAK_BEHANDEL_OPTIES}


class RadioSelect(forms.RadioSelect):
    option_template_name = "widgets/radio_option.html"


class RadioSelectSimple(forms.RadioSelect):
    option_template_name = "widgets/radio_option_simple.html"


class TaakBehandelForm(forms.Form):
    resolutie = forms.ChoiceField(
        widget=RadioSelectSimple(
            attrs={
                "class": "list--form-radio-input",
                "data-action": "change->bijlagen#updateImageDisplay",
            }
        ),
        label="Is de taak afgehandeld?",
        choices=[[x[4], x[1]] for x in TAAK_BEHANDEL_OPTIES],
        required=True,
    )

    bijlagen = forms.FileField(
        widget=forms.widgets.FileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic",
                "data-action": "change->bijlagen#updateImageDisplay",
                "data-bijlagen-target": "bijlagenExtra",
            }
        ),
        label="Foto's",
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
            }
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        volgende_taaktypes = kwargs.pop("volgende_taaktypes", None)
        super().__init__(*args, **kwargs)

        if volgende_taaktypes:
            self.fields["nieuwe_taak"] = forms.ChoiceField(
                widget=forms.Select(),
                label="Vervolgtaak",
                choices=[
                    (taaktype.id, taaktype.omschrijving)
                    for taaktype in volgende_taaktypes
                ],
                required=False,
            )
            self.fields["nieuwe_taak_toevoegen"] = forms.BooleanField(
                widget=forms.CheckboxInput(
                    attrs={
                        "class": "form-check-input",
                        "data-action": "change->incidentHandleForm#toggleNewTask",
                    }
                ),
                label="Er moet nog iets gebeuren.",
                required=False,
            )
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
        label="Sorteer de taken",
        choices=(
            ("Datum-reverse", "Datum (nieuwste bovenaan)"),
            ("Datum", "Datum (oudste bovenaan)"),
            ("Afstand", "Afstand"),
            ("Adres", "Adres (a-z)"),
            ("Adres-reverse", "Adres (z-a)"),
            ("Postcode", "Postcode (1000-9999)"),
            ("Postcode-reverse", "Postcode (9999-1000)"),
        ),
    )


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
