import os, sys, json, time, re, imaplib, email, getpass, subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Chrome実行ファイルのパス
USER_DATA_DIR = os.path.join(os.getcwd(), "chrome_profile")  # プロファイル保存先
DEBUG_PORT = 9222
OTP_SENDER = ""
BASE_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def launch_detached_chrome():
    if not os.path.exists(USER_DATA_DIR): os.makedirs(USER_DATA_DIR)
    cmd = [CHROME_PATH, f'--remote-debugging-port={DEBUG_PORT}', f'--user-data-dir={USER_DATA_DIR}', "--no-first-run", "--no-default-browser-check"]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
def attach_to_chrome():
    options = Options()
    options.add_experimental_option("debuggerAddress", f"localhost:{DEBUG_PORT}")
    return webdriver.Chrome(options=options)
    
def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f: return json.load(f)
        except Exception as e:
            print(f"[エラー] 設定ファイルの読み込みに失敗: {e}")
    print("設定ファイルが見つかりません。以下の情報を入力してください。")
    config = {
        "student_id": input("学生番号: "),
        "password": getpass.getpass("LMSパスワード: "),
        "email": input("OTP通知用メールアドレス: "),
        "email_password": getpass.getpass("メールパスワード（アプリパスワードなど）: ")
    }
    with open(CONFIG_FILE, "w") as f: json.dump(config, f)
    return config
    
def fetch_otp(email_user, email_pass):
    try:
        with imaplib.IMAP4_SSL("imap.gmail.com") as imap:
            imap.login(email_user, email_pass)
            imap.select("INBOX")
            status, messages = imap.search(None, f'(UNSEEN FROM "{OTP_SENDER}")')
            for mail_id in messages[0].split():
                _, msg_data = imap.fetch(mail_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body += part.get_payload(decode=True).decode()
                else:
                    body = msg.get_payload(decode=True).decode()
                match = re.search(r"\b\d{8}\b", body)
                if match:
                    imap.store(mail_id, '+FLAGS', '\\Seen')
                    return match.group()
    except Exception as e:
        print(f"メール取得中にエラー: {e}")
    return None
    
def safe_find_element(driver, by, value, timeout=10):
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            return driver.find_element(by, value)
        except NoSuchElementException:
            time.sleep(0.5)
    return None
    
def login_lms(driver, config):
    driver.get("https://lms.******/")
    time.sleep(1)
    login_btn = safe_find_element(driver, By.CLASS_NAME, "buttonLabel")
    if not login_btn:
        print("ログインボタンが見つかりません。")
        return False
    login_btn.click()
    time.sleep(1)
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
    time.sleep(1)
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
    time.sleep(1)
    try:
        select = Select(driver.find_element(By.NAME, "auth"))
        select.select_by_value("motplogin")
        driver.find_element(By.ID, "choice_button").click()
    except NoSuchElementException:
        print("OTP認証方式選択が見つかりません。スキップします。")
    return True
    
def enter_otp(driver, config):
    print("OTP入力欄の待機中...")
    otp_input = safe_find_element(driver, By.ID, "password_input", timeout=30)
    if not otp_input:
        print("OTP入力欄が見つかりません。")
        return False
    otp_used = None
    for attempt in range(3):
        print(f"[セット {attempt + 1}] OTP取得中...")
        otp, waited, resend_time = None, 0, 60
        while waited < 90:
            otp = fetch_otp(config["email"], config["email_password"])
            if otp and otp != otp_used:
                otp_used = otp
                print(f"OTP取得成功: {otp}")
                break
            if waited >= resend_time:
                try:
                    driver.find_element(By.ID, "otp_resend_button").click()
                    print("再送信クリック。")
                    waited = 0
                except NoSuchElementException:
                    print("再送信ボタンなし。")
            time.sleep(1)
            waited += 1
        if not otp:
            print("OTP取得失敗。")
            return False
        for sub in range(2):
            print(f"[OTP再試行 {sub + 1}/2]")
            otp_input.clear()
            otp_input.send_keys(otp)
            time.sleep(1)
            login_btn = safe_find_element(driver, By.ID, "login_button")
            if not login_btn:
                print("ログインボタンなし。")
                return False
            login_btn.click()
            time.sleep(2)
            try:
                error = driver.find_element(By.CSS_SELECTOR, "div.message.error")
                if "IDまたはパスワード" in error.text:
                    print("OTPエラー。")
                    continue
            except NoSuchElementException:
                print("OTP成功。")
                return True
        print("OTP再送信し次を待機。")
    print("全OTP試行に失敗。")
    return False
    
def close_extra_windows(driver):
    main = driver.current_window_handle
    for handle in driver.window_handles:
        if handle != main:
            driver.switch_to.window(handle)
            driver.close()
    driver.switch_to.window(main)
if __name__ == "__main__":
    config = load_or_create_config()
    print("Chrome起動中... 2秒待機")
    launch_detached_chrome()
    time.sleep(2)
    driver = attach_to_chrome()
    if login_lms(driver, config):
        if enter_otp(driver, config):
            print("ログイン成功。ウィンドウ整理中。")
            close_extra_windows(driver)
        else:
            print("OTP認証失敗。ブラウザ終了。")
            driver.quit()
    else:
        print("ログイン失敗。ブラウザ終了。")
        driver.quit()
    print("完了。ブラウザは手動で閉じてください。")
