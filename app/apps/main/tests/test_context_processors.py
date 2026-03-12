from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-wijken-cache",
    }
}


@override_settings(CACHES=TEST_CACHES)
class TestWijkenCaching(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()

    @patch("config.context_processors.LocatieService")
    def test_eerste_aanroep_roept_service_aan(self, MockLocatieService):
        """Bij een lege cache moet de service worden aangeroepen."""
        mock_service = MagicMock()
        mock_service.wijken.return_value = {
            "results": [{"naam": "Centrum", "code": "01"}]
        }
        MockLocatieService.return_value = mock_service

        from config.context_processors import _get_wijken_response

        instelling = MagicMock()
        result = _get_wijken_response(instelling)

        mock_service.wijken.assert_called_once()
        self.assertEqual(result["results"][0]["naam"], "Centrum")

    @patch("config.context_processors.LocatieService")
    def test_tweede_aanroep_gebruikt_cache(self, MockLocatieService):
        """Bij een gevulde cache moet de service NIET opnieuw worden aangeroepen."""
        mock_service = MagicMock()
        mock_service.wijken.return_value = {
            "results": [{"naam": "Centrum", "code": "01"}]
        }
        MockLocatieService.return_value = mock_service

        from config.context_processors import _get_wijken_response

        instelling = MagicMock()
        _get_wijken_response(instelling)
        _get_wijken_response(instelling)

        mock_service.wijken.assert_called_once()

    @patch("config.context_processors.LocatieService")
    def test_error_response_wordt_niet_gecached(self, MockLocatieService):
        """Bij een error-response moet de volgende aanroep de service opnieuw aanroepen."""
        mock_service = MagicMock()
        mock_service.wijken.side_effect = [
            {"error": "Service unavailable"},
            {"results": [{"naam": "Centrum", "code": "01"}]},
        ]
        MockLocatieService.return_value = mock_service

        from config.context_processors import _get_wijken_response

        instelling = MagicMock()
        result1 = _get_wijken_response(instelling)
        result2 = _get_wijken_response(instelling)

        self.assertEqual(mock_service.wijken.call_count, 2)
        self.assertIn("error", result1)
        self.assertEqual(result2["results"][0]["naam"], "Centrum")
