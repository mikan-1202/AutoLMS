import unittest
from unittest.mock import MagicMock, patch

from selenium.common.exceptions import NoSuchElementException, WebDriverException

from lms_login import app, browser


class BrowserTests(unittest.TestCase):
    @patch("lms_login.browser.time.sleep")
    @patch("lms_login.browser.wait_for_otp", return_value="12345678")
    @patch("lms_login.browser.safe_find_element")
    def test_submission_preserves_error_absence_check(self, find, wait, sleep):
        driver = MagicMock()
        driver.find_element.side_effect = NoSuchElementException()
        self.assertTrue(browser.enter_otp(driver, {"email": "sample", "email_password": "secret"}))
        find.return_value.send_keys.assert_called_with("12345678")

    @patch("lms_login.browser.time.sleep")
    @patch("lms_login.browser.wait_for_otp", return_value="12345678")
    @patch("lms_login.browser.safe_find_element")
    def test_persistent_error_has_bounded_submissions(self, find, wait, sleep):
        driver = MagicMock()
        self.assertFalse(browser.enter_otp(driver, {"email": "sample", "email_password": "secret"}))
        self.assertEqual(find.return_value.send_keys.call_count, 6)

    @patch.dict("os.environ", {"LMS_URL": "https://example.org/"})
    @patch("sys.argv", ["Login.py"])
    @patch("lms_login.app.load_config", return_value={})
    @patch("lms_login.browser.create_browser")
    @patch("lms_login.browser.login_lms", side_effect=WebDriverException("private"))
    def test_browser_closed_on_exception(self, login, create, config):
        self.assertEqual(app.main(), 1)
        create.return_value.quit.assert_called_once()
