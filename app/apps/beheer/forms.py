from django import forms


class AchtegrondTasksAanmakenForm(forms.Form):
    taakgebeurtenis_ids = forms.CharField(widget=forms.HiddenInput())


class ModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj


class CheckboxSelectMultipleTaakgebeurtenisNotificatieIssues(
    forms.CheckboxSelectMultiple
):
    template_name = (
        "beheer/taakgebeurtenis_notificatie_issues/taakgebeurtenissen_input.html"
    )


class TaakgebeurtenisNotificatieIssuesForm(forms.Form):
    page = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )
    q = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "data-action": "selectAll#selectAll",
            }
        ),
        label="Zoek",
        required=False,
    )
    taakgebeurtenissen = ModelMultipleChoiceField(
        widget=CheckboxSelectMultipleTaakgebeurtenisNotificatieIssues(
            attrs={
                "class": "form-check-input",
                "showSelectAll": True,
            }
        ),
        queryset=None,
        label=None,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        taakgebeurtenissen_choices = kwargs.pop("taakgebeurtenissen_choices", None)
        super().__init__(*args, **kwargs)

        if taakgebeurtenissen_choices is not None:
            self.fields["taakgebeurtenissen"].queryset = taakgebeurtenissen_choices
