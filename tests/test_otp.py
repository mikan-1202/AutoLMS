import imaplib
import unittest
from email.message import EmailMessage
from unittest.mock import MagicMock

from lms_login.otp import MailError, extract_otp, fetch_otp, wait_for_otp


def mail(text, charset="utf-8"):
    message = EmailMessage()
    message.set_content(text, charset=charset)
    return message.as_bytes()


class OtpTests(unittest.TestCase):
    def test_extract_with_declared_charset(self):
        self.assertEqual(extract_otp(mail("認証番号: 12345678", "iso-2022-jp")), "12345678")

    def test_reject_wrong_length_and_attachment(self):
        self.assertIsNone(extract_otp(mail("123456789 1234567")))
        message = EmailMessage()
        message.set_content("no code")
        message.add_attachment("12345678", subtype="plain", filename="code.txt")
        self.assertIsNone(extract_otp(message.as_bytes()))

    def test_fetch_newest_skip_used_and_mark_only_selected(self):
        factory = MagicMock()
        mailbox = factory.return_value.__enter__.return_value
        mailbox.login.return_value = ("OK", [])
        mailbox.select.return_value = ("OK", [])
        mailbox.uid.side_effect = [
            ("OK", [b"1 2"]),
            ("OK", [(b"2", mail("22222222"))]),
            ("OK", [(b"1", mail("11111111"))]),
            ("OK", []),
        ]
        self.assertEqual(
            fetch_otp("user", "secret", excluded={"22222222"}, connection_factory=factory),
            "11111111",
        )
        calls = mailbox.uid.call_args_list
        self.assertEqual(calls[1].args, ("fetch", b"2", "(BODY.PEEK[])"))
        self.assertEqual(calls[-1].args, ("store", b"1", "+FLAGS", "(\\Seen)"))

    def test_mail_errors_do_not_expose_server_message(self):
        factory = MagicMock(side_effect=imaplib.IMAP4.error("private server detail"))
        with self.assertRaises(MailError) as result:
            fetch_otp("user", "secret", connection_factory=factory)
        self.assertNotIn("private", str(result.exception))

    def test_non_ok_response_is_error(self):
        factory = MagicMock()
        factory.return_value.__enter__.return_value.login.return_value = ("NO", [])
        with self.assertRaises(MailError):
            fetch_otp("user", "secret", connection_factory=factory)

    def test_resend_does_not_extend_deadline(self):
        now = [0]

        def sleep(seconds):
            now[0] += seconds

        resend = MagicMock()
        result = wait_for_otp(
            lambda: None, resend, timeout=90, resend_after=60, clock=lambda: now[0], sleep=sleep
        )
        self.assertIsNone(result)
        self.assertEqual(now[0], 90)
        resend.assert_called_once()

    def test_fetch_time_counts_toward_deadline(self):
        now = [0]

        def fetch():
            now[0] += 100
            return "12345678"

        self.assertIsNone(wait_for_otp(fetch, MagicMock(), clock=lambda: now[0]))

    def test_received_code_returns_without_resend(self):
        resend = MagicMock()
        self.assertEqual(wait_for_otp(lambda: "12345678", resend), "12345678")
        resend.assert_not_called()
