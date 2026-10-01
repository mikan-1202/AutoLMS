import json
import tempfile
import unittest
from pathlib import Path

from lms_login.config import ConfigError, load_config


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "config.json"

    def test_new_config_does_not_store_secrets(self):
        answers = iter(["sample-student", "sample@example.invalid"])
        result = load_config(
            self.path, prompt=lambda _: next(answers), secret_prompt=lambda _: "secret", environ={}
        )
        self.assertEqual(result["password"], "secret")
        saved = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(set(saved), {"student_id", "email"})
        self.assertNotIn("secret", self.path.read_text())

    def test_invalid_json_is_not_overwritten(self):
        self.path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(ConfigError):
            load_config(self.path, environ={})
        self.assertEqual(self.path.read_text(), "{broken")

    def test_legacy_config_and_environment_override(self):
        original = {
            "student_id": "sample",
            "email": "sample@example.invalid",
            "password": "old",
            "email_password": "mail",
        }
        self.path.write_text(json.dumps(original), encoding="utf-8")
        result = load_config(self.path, environ={"LMS_PASSWORD": "new"})
        self.assertEqual(result["password"], "new")
        self.assertEqual(result["email_password"], "mail")
        self.assertEqual(json.loads(self.path.read_text()), original)

    def test_invalid_shape_or_field(self):
        for value in ([], {"student_id": 42}):
            with self.subTest(value=value):
                self.path.write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaises(ConfigError):
                    load_config(self.path, environ={})
