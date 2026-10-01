"""既存サービスの接続先・待機方針。画面仕様に依存する値をまとめる。"""

import os
from urllib.parse import urlsplit

from .config import ConfigError


def get_lms_url():
    url = os.environ.get("LMS_URL", "").strip()
    try:
        parsed = urlsplit(url)
        valid = (
            parsed.scheme == "https"
            and parsed.hostname
            and not parsed.username
            and not parsed.password
            and not parsed.hostname.endswith(".invalid")
        )
        _ = parsed.port
    except ValueError:
        valid = False
    if not valid:
        raise ConfigError("環境変数LMS_URLに対象LMSのHTTPS URLを設定してください。")
    return url


IMAP_HOST = "imap.gmail.com"
OTP_SENDER = "slink-info@secioss.co.jp"
IMAP_TIMEOUT = 15
ELEMENT_TIMEOUT = 10
PAGE_TRANSITION_DELAY = 1
OTP_RESULT_DELAY = 2
OTP_TIMEOUT = 90
OTP_RESEND_AFTER = 60
OTP_POLL_INTERVAL = 1
OTP_SETS = 3
OTP_SUBMISSIONS = 2
