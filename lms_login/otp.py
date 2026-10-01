"""メール本文の解析、IMAP取得、期限付きポーリング。Seleniumには依存しない。"""

import email
import imaplib
import re
import time

from .settings import (
    IMAP_HOST,
    IMAP_TIMEOUT,
    OTP_POLL_INTERVAL,
    OTP_RESEND_AFTER,
    OTP_SENDER,
    OTP_TIMEOUT,
)


class MailError(RuntimeError):
    """認証・通信・メールボックス操作の失敗。"""


def extract_otp(raw_message):
    message = email.message_from_bytes(raw_message)
    for part in message.walk():
        if (
            part.get_content_type() != "text/plain"
            or part.get_content_disposition() == "attachment"
        ):
            continue
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        try:
            body = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        except LookupError:
            body = payload.decode("utf-8", errors="replace")
        match = re.search(r"\b[0-9]{8}\b", body)
        if match:
            return match.group()
    return None


def require_ok(status):
    if status != "OK":
        raise MailError("メールサーバーの操作に失敗しました。")


def fetch_otp(email_user, email_password, *, excluded=(), connection_factory=imaplib.IMAP4_SSL):
    try:
        with connection_factory(IMAP_HOST, timeout=IMAP_TIMEOUT) as mailbox:
            require_ok(mailbox.login(email_user, email_password)[0])
            require_ok(mailbox.select("INBOX")[0])
            status, messages = mailbox.uid("search", None, f'(UNSEEN FROM "{OTP_SENDER}")')
            require_ok(status)
            for mail_id in reversed((messages[0] or b"").split()):
                status, data = mailbox.uid("fetch", mail_id, "(BODY.PEEK[])")
                require_ok(status)
                raw = next(
                    (
                        item[1]
                        for item in data
                        if isinstance(item, tuple) and isinstance(item[1], bytes)
                    ),
                    None,
                )
                if raw is None:
                    raise MailError("メール本文を読み取れませんでした。")
                otp = extract_otp(raw)
                if otp and otp not in excluded:
                    require_ok(mailbox.uid("store", mail_id, "+FLAGS", "(\\Seen)")[0])
                    return otp
    except (imaplib.IMAP4.error, OSError, EOFError) as exc:
        raise MailError("メール取得に失敗しました。接続と認証設定を確認してください。") from exc
    return None


def wait_for_otp(
    fetch,
    resend,
    *,
    timeout=OTP_TIMEOUT,
    resend_after=OTP_RESEND_AFTER,
    interval=OTP_POLL_INTERVAL,
    clock=time.monotonic,
    sleep=time.sleep,
):
    """再送は1回。通信時間も期限に含め、期限を再設定しない。

    同期通信中の中断はしないため、終了時刻は通信タイムアウト分だけ超過し得る。
    """
    started = clock()
    deadline = started + timeout
    resent = False
    while clock() < deadline:
        otp = fetch()
        if clock() >= deadline:
            return None
        if otp:
            return otp
        if not resent and clock() - started >= resend_after:
            resend()
            resent = True
        remaining = deadline - clock()
        if remaining > 0:
            sleep(min(interval, remaining))
    return None
