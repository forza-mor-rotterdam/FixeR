from apps.context.constanten import FILTER_NAMEN
from apps.context.models import Context
from apps.taken.models import Taaktype
from django import forms
from utils.forms import RadioSelect


class ContextAanpassenForm(forms.ModelForm):
    taaktypes = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
                "data-action": "change->incidentHandleForm#toggleNewTask",
            }
        ),
        queryset=Taaktype.objects.all(),
        label="Taaktypes",
        required=False,
    )
    template = forms.ChoiceField(
        widget=RadioSelect(
            attrs={
                "class": "list--form-radio-input",
                # "data-action": "change->bijlagen#updateImageDisplay",
            }
        ),
        label="Sjabloon",
        required=True,
        choices=Context.TemplateOpties.choices,
    )
    filters = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
                "data-action": "change->incidentHandleForm#toggleNewTask",
            }
        ),
        label="Filters",
        required=False,
        choices=[(f, f) for f in FILTER_NAMEN],
    )

    class Meta:
        model = Context
        fields = ("naam", "taaktypes", "filters", "template")


class ContextAanmakenForm(ContextAanpassenForm):
    class Meta:
        model = Context
        fields = (
            "naam",
            "taaktypes",
            "filters",
            "template",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "naam"
        ].help_text = "Omschrijf de rol zo concreet mogelijk, bijvoorbeeld ‘Teamleider Inzameling Noord’."
        self.fields[
            "taaktypes"
        ].help_text = "De taaktypes die hier worden geselecteerd worden getoond aan gebruikers met deze rol."
        self.fields[
            "filters"
        ].help_text = (
            "De hier geselecteerde opties worden getoond in het Filter-menu van FixeR."
        )
        self.fields[
            "template"
        ].help_text = "Ieder sjabloon toont andere informatie. Het ‘Standaard’ sjabloon voldoet voor de meeste afdelingen."
        self.fields["taaktypes"].label = "Met welke taaktypes werkt deze rol?"
        self.fields["filters"].label = "Welke filters zijn relevant voor deze rol?"
