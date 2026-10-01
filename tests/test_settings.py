import unittest
from unittest.mock import patch

from lms_login.config import ConfigError
from lms_login.settings import get_lms_url


class SettingsTests(unittest.TestCase):
    def test_reject_missing_placeholder_and_non_https(self):
        for url in (
            "",
            "https://lms.example.invalid/",
            "http://example.org",
            "https://user:pass@example.org",
            "https://[broken",
        ):
            with self.subTest(url=url), patch.dict("os.environ", {"LMS_URL": url}):
                with self.assertRaises(ConfigError):
                    get_lms_url()

    @patch.dict("os.environ", {"LMS_URL": "https://example.org/lms"})
    def test_accept_https(self):
        self.assertEqual(get_lms_url(), "https://example.org/lms")
