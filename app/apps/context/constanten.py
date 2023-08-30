FILTERS = (
    (
        "begraafplaats",
        "melding__response_json__locaties_voor_melding__0__begraafplaats",
        "melding__response_json__meta_uitgebreid__begraafplaats__choices",
    ),
    (
        "taken",
        "taaktype__id",
        "taaktype__omschrijving",
    ),
)
FILTER_NAMEN = [f[0] for f in FILTERS]
