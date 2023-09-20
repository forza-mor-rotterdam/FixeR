FILTERS = (
    (
        "begraafplaats",
        "melding__response_json__locaties_voor_melding__0__begraafplaats",
        "melding__response_json__meta_uitgebreid__begraafplaats__choices",
        "melding__response_json__locaties_voor_melding__0__begraafplaats__in",
    ),
    (
        "taken",
        "taaktype__id",
        "taaktype__omschrijving",
        "taaktype__id__in",
    ),
    (
        "wijk",
        "melding__response_json__locaties_voor_melding__0__wijknaam",
        "melding__response_json__locaties_voor_melding__0__wijknaam",
        "melding__response_json__locaties_voor_melding__0__wijknaam__in",
    ),
    (
        "buurt",
        "melding__response_json__locaties_voor_melding__0__buurtnaam",
        "melding__response_json__locaties_voor_melding__0__buurtnaam",
        "melding__response_json__locaties_voor_melding__0__buurtnaam__in",
    ),
)
FILTER_NAMEN = [f[0] for f in FILTERS]
FILTERS_LOOKUP = {f[0]: f for f in FILTERS}
