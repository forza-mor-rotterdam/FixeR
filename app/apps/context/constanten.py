from django.db.models import Count
from django.template.defaultfilters import slugify


class StandaardFilter:
    _key = None
    _option_key_lookup = None
    _option_value_lookup = None
    _option_group_lookup = None
    _filter_lookup = None
    _options = {}
    _taken = None
    _taken_filtered = None
    _options = None
    _grouped_options = None
    _filter_manager = None
    _selected_options = None

    def __init__(self, filter_manager, selected_options):
        self._selected_options = selected_options
        self._filter_manager = filter_manager
        self._set_options(selected_options)

    @classmethod
    def key(cls):
        return cls._key

    def get_option_key_lookup(self):
        return self._option_key_lookup

    def get_option_value_lookup(self):
        return (
            self._option_value_lookup
            if self._option_value_lookup
            else self._option_key_lookup
        )

    def get_option_group_lookup(self):
        return (
            self._option_group_lookup
            if self._option_group_lookup
            else self.get_option_value_lookup()
        )

    @classmethod
    def get_filter_lookup(cls):
        return cls._filter_lookup

    @classmethod
    def name(cls):
        return cls._label

    @classmethod
    def group_label(cls):
        return cls._group_label

    def _value_lookup(self, obj, key):
        if isinstance(obj, dict):
            return obj.get(key, key)
        if isinstance(obj, (str, int)):
            return obj
        return key

    def _set_options(self, selected_options):
        option_key = self.get_option_key_lookup()
        option_value = self.get_option_value_lookup()
        option_group = self.get_option_group_lookup()
        f_dict = {
            ll[0]: (self._value_lookup(ll[1], ll[0]), ll[2], 0)
            for ll in self._filter_manager.taken.order_by(option_key)
            .values_list(option_key, option_value, option_group)
            .distinct(option_key)
        }
        ff_dict = {
            fl[0]: (self._value_lookup(fl[1], fl[0]), fl[2], fl[3])
            for fl in self._filter_manager.taken_filtered.order_by(option_key)
            .values_list(option_key, option_value, option_group)
            .annotate(count=Count(option_key))
        }
        f_dict.update(ff_dict)
        f_dict = {str(k): v for k, v in f_dict.items() if k}
        print(f_dict)

        def create_option(k, v):
            return {
                "id": k,
                "label": v[0],
                "checked": str(k) in selected_options,
            }

        self._options = {
            "label": self._label,
            "name": self._label,
            "key": slugify(self._label),
            "options": [create_option(k, v) for k, v in f_dict.items()],
        }
        if self._option_group_lookup:
            self._grouped_options = {
                "label": self._group_label,
                "key": slugify(self._group_label),
                "groups": [
                    {
                        "name": g,
                        "key": slugify(g),
                        "label": self._label,
                        "options": [
                            create_option(kk, vv)
                            for kk, vv in f_dict.items()
                            if g == vv[1]
                        ],
                    }
                    for g in list(set([v[1] for k, v in f_dict.items()]))
                ],
            }

    def options(self):
        return self._options

    def active(self):
        return self._selected_options

    def grouped_options(self):
        return self._grouped_options


class BegraafplaatsFilter(StandaardFilter):
    _key = "begraafplaats"
    _option_key_lookup = (
        "melding__response_json__locaties_voor_melding__0__begraafplaats"
    )
    _option_value_lookup = (
        "melding__response_json__meta_uitgebreid__begraafplaats__choices"
    )
    _filter_lookup = (
        "melding__response_json__locaties_voor_melding__0__begraafplaats__in"
    )
    _label = "Begraafplaats"


class TaaktypeFilter(StandaardFilter):
    _key = "taken"
    _option_key_lookup = "taaktype__id"
    _option_value_lookup = "taaktype__omschrijving"
    _filter_lookup = "taaktype__id__in"
    _label = "Taak"


class WijkFilter(StandaardFilter):
    _key = "wijk"
    _option_key_lookup = "melding__response_json__locaties_voor_melding__0__wijknaam"
    _filter_lookup = "melding__response_json__locaties_voor_melding__0__wijknaam__in"
    _label = "Wijk"


class BuurtFilter(StandaardFilter):
    _key = "buurt"
    _option_key_lookup = "melding__response_json__locaties_voor_melding__0__buurtnaam"
    _filter_lookup = "melding__response_json__locaties_voor_melding__0__buurtnaam__in"
    _label = "Buurt"


class WijkBuurtFilter(StandaardFilter):
    _key = "wijk_buurt"
    _option_key_lookup = "melding__response_json__locaties_voor_melding__0__buurtnaam"
    _option_group_lookup = "melding__response_json__locaties_voor_melding__0__wijknaam"
    _filter_lookup = "melding__response_json__locaties_voor_melding__0__buurtnaam__in"
    _label = "Buurten"
    _group_label = "Wijken"


class FilterManager:
    _taken = None
    _taken_filtered = None
    _available_filter_classes = (
        BegraafplaatsFilter,
        TaaktypeFilter,
        WijkFilter,
        BuurtFilter,
        WijkBuurtFilter,
    )

    def __init__(self, taken, active_filters):
        self._taken = taken
        self._active_filters = {
            k: v
            for k, v in active_filters.items()
            if isinstance(v, (list, tuple)) and self._get_filter_class(k)
        }

    @property
    def taken(self):
        return self._taken

    @property
    def taken_filtered(self):
        return self._taken_filtered

    def _get_filter_class(self, filter_key):
        return {cls.key(): cls for cls in self._available_filter_classes}.get(
            filter_key
        )

    def filter(self):
        queryset_filter = {
            self._get_filter_class(k).get_filter_lookup(): v
            for k, v in self._active_filters.items()
            if v
        }
        self._taken_filtered = self._taken.filter(**queryset_filter)
        self._set_filter_options()
        return self._taken_filtered

    def _set_filter_options(self):
        self._filter_options = [
            self._get_filter_class(k)(self, v) for k, v in self._active_filters.items()
        ]

    def _set_available_active_filter_classes(self):
        if not self._active_filters or not isinstance(self._active_filters, dict):
            raise Exception("You have to filter taken first!")
        self._available_active_filter_classes = [
            f
            for f in self._available_filter_classes
            if f.key() in [k for k, v in self._active_filters.items()]
        ]
        return self._available_active_filter_classes

    def _validate_selected_options(self):
        self._validated_selected_options = {
            k: [
                af
                for af in v
                if af in [fok for fok, fov in self._filter_options.get(k, {}).items()]
            ]
            for k, v in self._validated_active_filters.items()
        }

    def filter_options(self, foldout_states=[]):
        # print([f for f in self._filter_options])
        return self._filter_options
        self._set_available_active_filter_classes()
        self._filter_options = [
            filter_class(
                self, self._validated_active_filters.get(filter_class.key())
            ).options()
            for filter_class in self._available_active_filter_classes
        ]
        # self._validate_selected_options()

        # print("__init__")
        # print(self._validated_selected_options)
        return []

    #     return [
    #         {
    #             "key": k,
    #             "naam": self._get_filter_class(k).label(),
    #             "opties": self._filter_options.get(k),
    #             "actief": self._validated_selected_options.get(k),
    #             "folded": f"foldout_{k}" not in foldout_states,
    #         }
    #         for k, v in self._validated_active_filters.items()
    #     ]

    # def validated_selected_options(self):
    #     return self._validated_selected_options


FILTERS = (
    (
        "begraafplaats",
        "melding__response_json__locaties_voor_melding__0__begraafplaats",
        "melding__response_json__meta_uitgebreid__begraafplaats__choices",
        "melding__response_json__meta_uitgebreid__begraafplaats__choices",
        "melding__response_json__locaties_voor_melding__0__begraafplaats__in",
    ),
    (
        "taken",
        "taaktype__id",
        "taaktype__omschrijving",
        "taaktype__omschrijving",
        "taaktype__id__in",
    ),
    (
        "wijk",
        "melding__response_json__locaties_voor_melding__0__wijknaam",
        "melding__response_json__locaties_voor_melding__0__wijknaam",
        "melding__response_json__locaties_voor_melding__0__wijknaam",
        "melding__response_json__locaties_voor_melding__0__wijknaam__in",
    ),
    (
        "buurt",
        "melding__response_json__locaties_voor_melding__0__buurtnaam",
        "melding__response_json__locaties_voor_melding__0__buurtnaam",
        "melding__response_json__locaties_voor_melding__0__buurtnaam",
        "melding__response_json__locaties_voor_melding__0__buurtnaam__in",
    ),
)

FILTERS = (
    BegraafplaatsFilter,
    TaaktypeFilter,
    WijkFilter,
    BuurtFilter,
    WijkBuurtFilter,
)

FILTER_NAMEN = [f.key() for f in FILTERS]
FILTERS_LOOKUP = {f.key(): f for f in FILTERS}
