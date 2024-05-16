import copy
import logging
import math

from apps.services.basis import BasisService
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PDOKService(BasisService):
    _basis_url = "https://api.pdok.nl/bzk/locatieserver/search/v3_1"

    def get_buurten_middels_gemeentecode(self, gemeentecode) -> dict:
        url = f"{self._basis_url}/free"
        results = []
        start = 0
        rows = 10
        params = {
            "start": start,
            "rows": rows,
            "fq": [
                f"gemeentecode:{gemeentecode}",
                "bron:CBS",
                "type:buurt",
            ],
            "wt": "json",
            "fl": [
                "woonplaatscode",
                "wijkcode",
                "wijknaam",
                "buurtcode",
                "buurtnaam",
            ],
        }
        response = self.do_request(url, params=params, raw_response=False).get(
            "response", {}
        )
        result_count = response.get("numFound", 0)
        results.extend(response.get("docs", []))
        loop_range = range(
            (start + 1) * rows, math.ceil(result_count / rows) * rows, rows
        )
        for i in loop_range:
            params_clone = copy.deepcopy(params)
            params_clone.update(
                {
                    "start": i,
                }
            )
            r = self.do_request(url, params=params_clone, raw_response=False).get(
                "response", {}
            )
            results.extend(r.get("docs", []))

        wijken = {r.get("wijkcode"): r for r in results}
        results_grouped = {
            "wijken": [
                {
                    "wijkcode": wijkcode,
                    "wijknaam": w.get("wijknaam"),
                    "buurten": [
                        {
                            "buurtnaam": b.get("buurtnaam"),
                            "buurtcode": b.get("buurtcode"),
                        }
                        for b in results
                        if b.get("wijkcode") == wijkcode
                    ],
                }
                for wijkcode, w in wijken.items()
            ]
        }
        cache.set(
            settings.WIJKEN_EN_BUURTEN_CACHE_KEY,
            results_grouped,
            settings.MELDINGEN_TOKEN_TIMEOUT,
        )
        return results_grouped
