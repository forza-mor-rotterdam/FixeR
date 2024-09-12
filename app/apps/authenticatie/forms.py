import csv
import json
from io import StringIO

import chardet
from apps.authenticatie.models import Profiel
from apps.context.models import Context
from apps.main.utils import get_wijknaam_by_wijkcode
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models.query import QuerySet
from utils.constanten import PDOK_WIJKEN

Gebruiker = get_user_model()


class GebruikerAanpassenForm(forms.ModelForm):
    context = forms.ModelChoiceField(
        queryset=Context.objects.all(),
        label="Rol",
        required=True,
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Rechtengroep",
        required=False,
    )

    class Meta:
        model = Gebruiker
        fields = ("telefoonnummer", "first_name", "last_name", "group", "context")


class GebruikerAanmakenForm(GebruikerAanpassenForm):
    class Meta:
        model = Gebruiker
        fields = (
            "email",
            "telefoonnummer",
            "first_name",
            "last_name",
            "group",
            "context",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "email"
        ].help_text = "Gebruik altijd het e-mailadres van de gemeente."
        self.fields[
            "context"
        ].help_text = (
            "Bestaat de juiste rol voor deze gebruiker niet, maak deze eerst aan."
        )
        self.fields[
            "group"
        ].help_text = "Bestaat de juiste rechtengroep voor deze gebruiker niet, maak deze eerst aan."


class GebruikerBulkImportForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "data-action": "change->bijlagen#updateImageDisplay",
                "accept": ".csv",
                "required_css_class": "required",
                "button_text": "CSV bestand",
            }
        ),
        label="CSV upload",
    )
    context = forms.ModelChoiceField(
        widget=forms.Select(attrs={"class": "form-control"}),
        queryset=Context.objects.all(),
        label="Rol",
        required=True,
    )
    group = forms.ModelChoiceField(
        widget=forms.Select(attrs={"class": "form-control"}),
        queryset=Group.objects.all(),
        label="Rechtengroep",
        required=True,
    )

    def clean_csv_file(self):
        try:
            csv_file = self.cleaned_data["csv_file"]
            file_read = csv_file.read()

            encoding = "utf-8"
            auto_detect_encoding = chardet.detect(file_read)
            if auto_detect_encoding.get("confidence") > 0.5:
                encoding = auto_detect_encoding.get("encoding")
        except Exception:
            return {}
        return self._get_rows(file_read.decode(encoding, "ignore"))

    def _get_rows(self, str_data):
        all_rows = []
        valid_rows = []
        csv_fo = StringIO(str_data)

        csvreader = csv.reader(csv_fo, delimiter=";", quotechar="|")
        valid_checked_rows_email = []
        for row in csvreader:
            if len(row) and not row[0] or len(row) == 0:
                continue
            default_row = [row[r] if r < len(row) else None for r in range(0, 4)]
            try:
                validate_email(default_row[0])
            except ValidationError:
                continue
            default_row[0] = default_row[0].lower()
            errors = []
            if default_row[0] in valid_checked_rows_email:
                errors.append(
                    "Er is al een gebruiker met dit e-mailadres in deze lijst aanwezig"
                )
            row_is_not_valid = self.validate_row(default_row, errors)
            default_row.append(row_is_not_valid)
            default_row.append("")
            if not row_is_not_valid:
                if Gebruiker.objects.all().filter(email__iexact=default_row[0].lower()):
                    default_row[5] = "aanpassen"
                valid_rows.append(default_row)

                valid_checked_rows_email.append(default_row[0])
            all_rows.append(default_row)
        return {
            "all_rows": all_rows,
            "valid_rows": valid_rows,
        }

    def validate_row(self, row, errors=[]):
        email = row[0]
        first_name = row[1]
        last_name = row[2]
        telefoonnummer = row[3]
        try:
            validate_email(email.strip())
        except ValidationError:
            errors.append(f"{email} is geen e-mailadres")
        if first_name and len(first_name) > 150:
            errors.append("voornaam mag niet langer zijn dan 150 karakters")
        if last_name and len(last_name) > 150:
            errors.append("achternaam mag niet langer zijn dan 150 karakters")
        if telefoonnummer and len(telefoonnummer) > 17:
            errors.append("telefoonnummer mag niet langer zijn dan 17 karakters")
        return ", ".join(errors)

    def submit(self, valid_rows):
        gebruiker_fieldnames = [
            "email",
            "first_name",
            "last_name",
            "telefoonnummer",
        ]
        aangemaakte_gebruikers = Gebruiker.objects.bulk_create(
            [
                Gebruiker(**{f: row[i] for i, f in enumerate(gebruiker_fieldnames)})
                for row in valid_rows
            ],
            ignore_conflicts=False,
            update_conflicts=True,
            unique_fields=["email"],
            update_fields=["first_name", "last_name", "telefoonnummer"],
        )

        aangemaakte_aangepaste_gebruikers = []
        for gebruiker in aangemaakte_gebruikers:
            if not gebruiker.id:
                gebruiker = Gebruiker.objects.get(email=gebruiker.email)
            gebruiker.groups.clear()
            gebruiker.groups.add(self.cleaned_data.get("group"))
            if not hasattr(gebruiker, "profiel"):
                Profiel.objects.create(
                    gebruiker=gebruiker,
                    context=self.cleaned_data.get("context"),
                )
            else:
                gebruiker.profiel.context = self.cleaned_data.get("context")
                gebruiker.profiel.save()
            aangemaakte_aangepaste_gebruikers.append(gebruiker)
        return aangemaakte_aangepaste_gebruikers


class GebruikerProfielForm(forms.ModelForm):
    telefoonnummer = forms.CharField(
        label="Telefoonnummer",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    first_name = forms.CharField(
        label="Voornaam",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    last_name = forms.CharField(
        label="Achternaam",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = Gebruiker
        fields = ("telefoonnummer", "first_name", "last_name")


class WelkomForm(forms.Form):
    pass


class ProfielfotoForm(forms.ModelForm):
    class Meta:
        model = Profiel
        fields = ["profielfoto"]


class AfdelingForm(forms.Form):
    afdelingen = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "hasIcon": True,
                "classList": "list--form-check-input--tile-image",
            }
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        afdelingen_data = kwargs.pop("afdelingen_data", [])
        super().__init__(*args, **kwargs)
        afdelingen = [
            (
                afdeling["uuid"],
                {"naam": afdeling["naam"], "icon": afdeling.get("icoon", None)},
            )
            for afdeling in afdelingen_data
        ]
        self.fields["afdelingen"].choices = afdelingen


class WerklocatieForm(forms.ModelForm):
    wijken = forms.MultipleChoiceField(
        label="Wijken",
        choices=[],
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "showSelectAll": True,
                "data-action": "change->onboarding#updateCounters",
                "showCount": True,
            }
        ),
        required=True,
    )

    stadsdeel = forms.ChoiceField(
        label="Gebied",
        choices=Profiel.StadsdeelOpties.choices,
        widget=forms.RadioSelect(
            attrs={
                "data-action": "change->onboarding#updateWijken",
                "data-onboarding-wijken-param": json.dumps(PDOK_WIJKEN),
                "classList": "list--form-radio-input background--white",
            }
        ),
        required=True,
        initial=None,
    )

    class Meta:
        model = Profiel
        fields = ["stadsdeel"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_wijken_choices(stadsdeel=self.fields["stadsdeel"].initial)

    def update_wijken_choices(self, stadsdeel=None):
        sorted_pdok_wijken = sorted(PDOK_WIJKEN, key=lambda wijk: wijk["wijknaam"])
        wijken_choices = [
            (wijk["wijkcode"], wijk["wijknaam"]) for wijk in sorted_pdok_wijken
        ]
        self.fields["wijken"].choices = wijken_choices


class BevestigenForm(forms.Form):
    def __init__(self, *args, **kwargs):
        afdelingen_data = kwargs.pop("afdelingen_data", {})
        previous_steps_data = kwargs.pop("previous_steps_data", {})
        super(BevestigenForm, self).__init__(*args, **kwargs)

        # Dynamically add fields from previous steps as read-only fields
        for field_name, field_value in previous_steps_data.items():
            if field_value:
                # print(
                #     f"Field name: {field_name}, value: {field_value}, type: {type(field_value)}"
                # )
                if field_name == "afdelingen" and isinstance(field_value, list):
                    self.fields[field_name] = forms.MultipleChoiceField(
                        choices=[
                            (
                                val,
                                next(
                                    (
                                        {
                                            "naam": afdeling["naam"],
                                            "icon": afdeling.get("icoon", None),
                                        }
                                        for afdeling in afdelingen_data
                                        if afdeling["uuid"] == val
                                    ),
                                    val,
                                ),
                            )
                            for val in field_value
                        ],
                        widget=forms.CheckboxSelectMultiple(
                            attrs={
                                "readonly": "readonly",
                                "disabled": "disabled",
                                "hideLabel": True,
                                "hasIcon": True,
                                "classList": "list--form-check-input--tile-image",
                            }
                        ),
                        required=False,
                    )
                elif field_name.startswith("taaktypes_") and isinstance(
                    field_value, QuerySet
                ):
                    self.fields[field_name] = forms.ModelMultipleChoiceField(
                        queryset=field_value,
                        widget=forms.CheckboxSelectMultiple(
                            attrs={
                                "readonly": "readonly",
                                "disabled": "disabled",
                                "hideLabel": True,
                            }
                        ),
                        required=False,
                    )
                elif isinstance(field_value, QuerySet):
                    self.fields[field_name] = forms.ModelMultipleChoiceField(
                        queryset=field_value,
                        widget=forms.CheckboxSelectMultiple(
                            attrs={
                                "readonly": "readonly",
                                "disabled": "disabled",
                                "hideLabel": True,
                            }
                        ),
                        required=False,
                    )
                elif isinstance(field_value, str):
                    self.fields[field_name] = forms.CharField(
                        initial=field_value.title(),
                        widget=forms.TextInput(
                            attrs={
                                "readonly": "readonly",
                                "disabled": "disabled",
                                "hideLabel": True,
                            }
                        ),
                        required=False,
                    )
                elif isinstance(field_value, list):
                    self.fields[field_name] = forms.MultipleChoiceField(
                        choices=[
                            (
                                val,
                                (
                                    get_wijknaam_by_wijkcode(val)
                                    if field_name == "wijken"
                                    else val
                                ),
                            )
                            for val in field_value
                        ],
                        initial=field_value,
                        widget=forms.CheckboxSelectMultiple(
                            attrs={
                                "readonly": "readonly",
                                "disabled": "disabled",
                                "hideLabel": True,
                            }
                        ),
                        required=False,
                    )

    class Meta:
        fields = []
