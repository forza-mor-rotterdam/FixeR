from apps.context.models import Context
from apps.taken.filters import FILTERS_BY_KEY
from apps.taken.models import Taaktype
from django import forms


class ContextAanpassenForm(forms.ModelForm):
    taaktypes = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
            }
        ),
        queryset=Taaktype.objects.all(),
        label="Taaktypes",
        required=False,
    )
    template = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
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
            }
        ),
        label="Filters",
        required=False,
        choices=[(f, f) for f in FILTERS_BY_KEY.keys()],
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
            }
        ),
        queryset=Taaktype.objects.all(),
        label="Taaktypes",
        required=False,
    )

    class Meta:
        model = Context
        fields = ("taaktypes",)


class TaaktypeCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    option_template_name = "onboarding/checkbox_option_taaktype.html"


class TaaktypesFilteredForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        afdelingen_data = kwargs.pop("afdelingen_data", [])
        afdelingen_selected = kwargs.pop("afdelingen_selected", [])
        super().__init__(*args, **kwargs)

        for afdeling_uuid in afdelingen_selected:
            afdeling_detail = next(
                (
                    afdeling
                    for afdeling in afdelingen_data
                    if afdeling["uuid"] == afdeling_uuid
                ),
                None,
            )
            if afdeling_detail:
                taaktype_omschrijvingen = [
                    taaktype["omschrijving"]
                    for taaktype in afdeling_detail.get("taaktypes_voor_afdelingen", [])
                ]

                taaktypes_queryset = Taaktype.objects.filter(
                    omschrijving__in=taaktype_omschrijvingen
                ).distinct()

                if taaktypes_queryset.exists():
                    field_name = f"taaktypes_{afdeling_detail['naam']}"
                    self.fields[field_name] = forms.ModelMultipleChoiceField(
                        widget=TaaktypeCheckboxSelectMultiple(
                            attrs={
                                "class": "form-check-input",
                                # "data-onboarding-target": "taaktypeInput",
                                "data-action": "change->onboarding#updateCounters",
                                "showSelectAll": True,
                                "showCount": True,
                            }
                        ),
                        queryset=taaktypes_queryset,
                        label=f"Taken van {afdeling_detail['naam']}",
                        required=True,
                    )

    class Meta:
        model = Context
        fields = ()
