from apps.context.filters import FilterManager
from apps.context.models import Context
from apps.services.taakr import TaakRService
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
        choices=[(f, f) for f in FilterManager.available_filter_names()],
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


class TaaktypesForm(forms.ModelForm):
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

    class Meta:
        model = Context
        fields = ("taaktypes",)


class TaaktypesFilteredForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        afdelingen_selected = kwargs.pop("afdelingen_selected", None)
        super().__init__(*args, **kwargs)

        if afdelingen_selected:
            for afdeling_url in afdelingen_selected:
                print(f"Afdeling: {afdeling_url}")
                afdeling_response = TaakRService().get_afdeling_by_url(afdeling_url)
                print(f"Afdeling response: {afdeling_response}")

                # Extract the UUIDs of the taaktypes for the current afdeling
                taaktype_omschrijvingen = [
                    taaktype["omschrijving"]
                    for taaktype in afdeling_response.get(
                        "taaktypes_voor_afdelingen", []
                    )
                ]
                print(f"taaktype omschrijvingen: {taaktype_omschrijvingen}")

                # Fetch the queryset for the corresponding taaktypes
                taaktypes_queryset = Taaktype.objects.filter(
                    omschrijving__in=taaktype_omschrijvingen
                ).distinct()

                if taaktypes_queryset.exists():
                    field_name = f"taaktypes_{afdeling_response['naam']}"
                    self.fields[field_name] = forms.ModelMultipleChoiceField(
                        widget=forms.CheckboxSelectMultiple(
                            attrs={
                                "class": "form-check-input",
                                "data-action": "change->incidentHandleForm#toggleNewTask",
                                "showSelectAll": True,
                            }
                        ),
                        queryset=taaktypes_queryset,
                        label=f"Taken van {afdeling_response['naam']} ({taaktypes_queryset.count()})",
                        required=False,
                    )

    class Meta:
        model = Context
        fields = ()
