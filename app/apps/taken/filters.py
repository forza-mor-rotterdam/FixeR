from apps.main.services import PDOKService


class StandaardFilter:
    _key = None
    _filter_lookup = None
    _choices = ()
    _label = "Default label"
    _sub_label = None
    _field_template = "taken/overzicht/filter_field.html"
    _profiel = None

    def __init__(self, *args, **kwargs):
        self._profiel = kwargs.pop("profiel", None)

    def flat_choices(self):
        return [choice[0] for choice in self._choices]

    def choices(self):
        return self._choices

    def active_choices(self, values):
        choices = [
            (
                v[0],
                v[1]
                if not isinstance(v[1], (list, tuple))
                else [vv for vv in v[1] if vv[0] in values],
            )
            for v in self.choices()
            if v[0] in values
            or (
                isinstance(v[1], (list, tuple))
                and [vv for vv in v[1] if vv[0] in values]
            )
        ]
        return choices

    @classmethod
    def filter_lookup(cls):
        return cls._filter_lookup

    @classmethod
    def key(cls):
        return cls._key

    @classmethod
    def label(cls):
        return cls._label

    @classmethod
    def sub_label(cls):
        return cls._sub_label

    @classmethod
    def field_template(cls):
        return cls._field_template


class BegraafplaatsFilter(StandaardFilter):
    _key = "begraafplaats"
    _filter_lookup = "melding__begraafplaats__in"
    _label = "Begraafplaats"
    _choices = (
        ("1", "Begraafplaats Crooswijk"),
        ("2", "Begraafplaats Hoek van Holland"),
        ("3", "Begraafplaats en crematorium Hofwijk"),
        ("4", "Begraafplaats Oudeland, Hoogvliet"),
        ("5", "Begraafplaats Oud-Hoogvliet"),
        ("6", "Begraafplaats Oud-Overschie"),
        ("7", "Begraafplaats Oud-Pernis"),
        ("8", "Begraafplaats Oud-Schiebroek"),
        ("9", "Begraafplaats Pernis"),
        ("10", "Begraafplaats Rozenburg"),
        ("11", "Zuiderbegraafplaats"),
    )


class TaaktypeFilter(StandaardFilter):
    _key = "taken"
    _filter_lookup = "taaktype__id__in"
    _label = "Taak"

    def flat_choices(self):
        return [
            f"{taaktype['id']}"
            for taaktype in self._profiel.get_taaktypes().values("id", "omschrijving")
        ]

    def choices(self):
        return [
            (f"{taaktype['id']}", taaktype["omschrijving"])
            for taaktype in self._profiel.get_taaktypes().values("id", "omschrijving")
        ]


class TaakStatusFilter(StandaardFilter):
    _key = "taak_status"
    _filter_lookup = "taakstatus__naam__in"
    _label = "Taakstatus"
    _choices = (
        ("nieuw", "Nieuw"),
        ("voltooid", "Voltooid"),
    )


class WijkBuurtFilter(StandaardFilter):
    _key = "buurt"
    _filter_lookup = "melding__buurtnaam__in"
    _label = "Wijken & buurten"
    _sub_label = "Buurten"
    _field_template = "taken/overzicht/filter_field_grouped.html"

    def flat_choices(self):
        pdok_service = PDOKService()
        all_data = pdok_service.get_buurten_middels_gemeentecode()
        return [
            buurt["buurtnaam"]
            for wijk in all_data.get("wijken", [])
            for buurt in wijk.get("buurten", [])
            if wijk["wijkcode"] in self._profiel.wijken
        ]

    def choices(self):
        pdok_service = PDOKService()
        all_data = pdok_service.get_buurten_middels_gemeentecode()
        return [
            [
                wijk["wijknaam"],
                sorted(
                    [
                        [buurt["buurtnaam"], buurt["buurtnaam"]]
                        for buurt in wijk.get("buurten", [])
                    ],
                    key=lambda x: x[0],
                ),
            ]
            for wijk in all_data.get("wijken", [])
            if wijk["wijkcode"] in self._profiel.wijken
        ]


FILTERS = [
    TaaktypeFilter,
    TaakStatusFilter,
    BegraafplaatsFilter,
    WijkBuurtFilter,
]

FILTERS_BY_KEY = {f.key(): f for f in FILTERS}
