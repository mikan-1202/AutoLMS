"""既存の画面操作順序とセレクターを保持したSelenium操作。"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

from .otp import fetch_otp, wait_for_otp
from .settings import (
    ELEMENT_TIMEOUT,
    get_lms_url,
    PAGE_TRANSITION_DELAY,
    OTP_RESULT_DELAY,
    OTP_SETS,
    OTP_SUBMISSIONS,
)


def create_browser():
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=options)


def safe_find_element(driver, by, value, timeout=ELEMENT_TIMEOUT):
    end_time = time.monotonic() + timeout
    while time.monotonic() < end_time:
        try:
            return driver.find_element(by, value)
        except NoSuchElementException:
            time.sleep(0.5)
    return None


# ▼ 共通クリック関数（背面でも動作可能）
def safe_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    driver.execute_script("arguments[0].click();", element)


def login_lms(driver, config):
    driver.get(get_lms_url())
    time.sleep(PAGE_TRANSITION_DELAY)
    login_btn = safe_find_element(driver, By.CLASS_NAME, "buttonLabel")
    if not login_btn:
        print("ログインボタンが見つかりません。")
        return False
    safe_click(driver, login_btn)
    time.sleep(PAGE_TRANSITION_DELAY)
    driver.switch_to.window(driver.window_handles[-1])
    user_input = safe_find_element(driver, By.ID, "username_input")
    if not user_input:
        print("ユーザー名入力欄が見つかりません。")
        return False
    user_input.send_keys(config["student_id"])
    login_btn = safe_find_element(driver, By.ID, "login_button")
    if not login_btn:
        print("次へボタンが見つかりません。")
        return False
    login_btn.click()
    time.sleep(PAGE_TRANSITION_DELAY)
    pwd_input = safe_find_element(driver, By.ID, "password_input")
    if not pwd_input:
        print("パスワード入力欄が見つかりません。")
        return False
    pwd_input.send_keys(config["password"])
    login_btn = safe_find_element(driver, By.ID, "login_button")
    if not login_btn:
        print("ログインボタンが見つかりません。")
        return False
    login_btn.click()
    time.sleep(PAGE_TRANSITION_DELAY)
    try:
        select = Select(driver.find_element(By.NAME, "auth"))
        select.select_by_value("motplogin")
        choice_btn = driver.find_element(By.ID, "choice_button")
        safe_click(driver, choice_btn)
    except NoSuchElementException:
        print("OTP認証方式選択が見つかりません。スキップします。")
    return True


def resend_otp(driver):
    try:
        safe_click(driver, driver.find_element(By.ID, "otp_resend_button"))
        print("OTPの再送を要求しました。")
    except NoSuchElementException:
        print("再送信ボタンが見つかりません。")


def enter_otp(driver, config):
    used_codes = set()
    for attempt in range(OTP_SETS):
        if not safe_find_element(driver, By.ID, "password_input", timeout=30):
            print("OTP入力欄が見つかりません。")
            return False
        print(f"[セット {attempt + 1}/{OTP_SETS}] OTP取得中...")
        otp = wait_for_otp(
            lambda: fetch_otp(config["email"], config["email_password"], excluded=used_codes),
            lambda: resend_otp(driver),
        )
        if otp is None:
            print("制限時間内にOTPを取得できませんでした。")
            return False
        used_codes.add(otp)
        print("OTPを取得しました。")
        for submission in range(OTP_SUBMISSIONS):
            # 再描画後に古いWebElementを使わない。
            otp_input = safe_find_element(driver, By.ID, "password_input")
            login_button = safe_find_element(driver, By.ID, "login_button")
            if otp_input is None or login_button is None:
                return False
            print(f"[OTP送信 {submission + 1}/{OTP_SUBMISSIONS}]")
            otp_input.clear()
            otp_input.send_keys(otp)
            time.sleep(PAGE_TRANSITION_DELAY)
            safe_click(driver, login_button)
            time.sleep(OTP_RESULT_DELAY)
            try:
                driver.find_element(By.CSS_SELECTOR, "div.message.error")
            except NoSuchElementException:
                return True
            print("認証画面でエラーが検出されました。")
        if attempt + 1 < OTP_SETS:
            resend_otp(driver)
    return False


def close_extra_windows(driver):
    main = driver.current_window_handle
    for handle in driver.window_handles:
        if handle != main:
            driver.switch_to.window(handle)
            driver.close()
    driver.switch_to.window(main)
