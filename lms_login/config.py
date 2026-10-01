"""既存JSONと互換性を保ち、新規保存時にはパスワードを含めない。"""

import getpass
import json
import os
import sys
from pathlib import Path


class ConfigError(ValueError):
    """設定を読み込めない、または必須項目が不正。"""


def default_config_path():
    base = (
        Path(sys.executable).parent
        if getattr(sys, "frozen", False)
        else Path(__file__).resolve().parent.parent
    )
    return base / "config.json"


def validate_config(config):
    if not isinstance(config, dict):
        raise ConfigError("設定はJSONオブジェクトにしてください。")
    for key in ("student_id", "password", "email", "email_password"):
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise ConfigError(f"設定項目 {key} に空でない文字列が必要です。")
    return config


def load_config(path=None, *, prompt=input, secret_prompt=getpass.getpass, environ=None):
    path = Path(path) if path is not None else default_config_path()
    environ = os.environ if environ is None else environ
    exists = path.exists()
    try:
        config = json.loads(path.read_text(encoding="utf-8-sig")) if exists else {}
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ConfigError(
            "設定ファイルを読み込めません。内容を確認してください（上書きしません）。"
        ) from exc
    if not isinstance(config, dict):
        raise ConfigError("設定はJSONオブジェクトにしてください。")
    for key in ("student_id", "password", "email", "email_password"):
        if key in config and not isinstance(config[key], str):
            raise ConfigError(f"設定項目 {key} は文字列にしてください。")
    for key, label in (("student_id", "学生番号: "), ("email", "OTP通知用Gmailアドレス: ")):
        if not config.get(key, "").strip():
            config[key] = prompt(label).strip()
    for key, variable, label in (
        ("password", "LMS_PASSWORD", "LMSパスワード: "),
        ("email_password", "LMS_EMAIL_PASSWORD", "メールのアプリパスワード: "),
    ):
        config[key] = environ.get(variable) or config.get(key) or secret_prompt(label)
    validate_config(config)
    if not exists:
        try:
            with path.open("x", encoding="utf-8") as stream:
                json.dump(
                    {key: config[key] for key in ("student_id", "email")},
                    stream,
                    ensure_ascii=False,
                    indent=2,
                )
        except OSError as exc:
            raise ConfigError("設定を保存できません。保存先の権限を確認してください。") from exc
    return config
