"""CLIの入口とリソースの終了処理。"""

import argparse

from .config import ConfigError, load_config
from .otp import MailError
from .settings import get_lms_url


def main():
    parser = argparse.ArgumentParser(description="LMSへのログインとメールOTP入力を補助します。")
    parser.add_argument("--config", help="設定JSONのパス（既定: アプリと同じ場所）")
    args = parser.parse_args()
    try:
        from selenium.common.exceptions import WebDriverException
        from .browser import close_extra_windows, create_browser, enter_otp, login_lms
    except ImportError:
        print("依存関係が不足しています。pip install -r requirements.txt を実行してください。")
        return 1
    driver = None
    keep_browser = False
    try:
        get_lms_url()
        config = load_config(args.config)
        print("Chrome起動中...")
        driver = create_browser()
        if not login_lms(driver, config) or not enter_otp(driver, config):
            print("認証処理を完了できませんでした。")
            return 1
        close_extra_windows(driver)
        keep_browser = True
        print(
            "認証送信後にエラー表示は検出されませんでした。LMS画面を確認し、終了後は手動で閉じてください。"
        )
        return 0
    except (ConfigError, MailError) as exc:
        print(str(exc))
        return 1
    except WebDriverException:
        print("ブラウザ操作に失敗しました。Chrome・通信状態・画面の変更を確認してください。")
        return 1
    except (KeyboardInterrupt, EOFError):
        print("入力または処理を中断しました。")
        return 130
    finally:
        if driver is not None and not keep_browser:
            try:
                driver.quit()
            except WebDriverException:
                print("ブラウザの終了を確認できませんでした。必要に応じて手動で閉じてください。")
