from django.forms.widgets import CheckboxInput as DjangoCheckboxInput


class CheckboxInput(DjangoCheckboxInput):
    template_name = "widgets/checkbox.html"

    def __init__(self, attrs=None):
        attrs = {} if attrs is None else attrs.copy()
        attrs.update(
            {
                "class": "form-check-input",
            }
        )
        super().__init__(attrs=attrs)
