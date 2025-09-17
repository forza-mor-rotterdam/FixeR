from apps.frontend.widgets import CheckboxInput
from django.forms.fields import BooleanField as DjangoBooleanField


class FieldInitMixin:
    default_template_name = "django/forms/field.html"

    def __init__(
        self,
        *,
        required=True,
        widget=None,
        label=None,
        initial=None,
        help_text="",
        error_messages=None,
        show_hidden_initial=False,
        validators=(),
        localize=False,
        disabled=False,
        label_suffix=None,
        template_name=None,
        bound_field_class=None,
    ):
        super().__init__(
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            error_messages=error_messages,
            show_hidden_initial=show_hidden_initial,
            validators=validators,
            localize=localize,
            disabled=disabled,
            label_suffix=label_suffix,
            template_name=template_name
            if template_name
            else self.default_template_name,
            bound_field_class=bound_field_class,
        )


class BooleanField(FieldInitMixin, DjangoBooleanField):
    default_template_name = "fields/boolean.html"
    widget = CheckboxInput
