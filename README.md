# 📘 LMS 自動ログイン・OTP認証スクリプト

## ✅ 概要
このスクリプトは、東北工業大学のLMSに対し、以下を自動で実行します：

- Chromeをプロファイル付きで起動（デバッグモード）
- LMSにログイン
- メールによるOTPを取得
- 自動的にOTPを入力しログイン完了
- 最前面以外のウィンドウを自動で閉じる

## 💻 使用方法

### 1. 前提条件

- Google Chrome がインストールされていること（`CHROME_PATH`を確認）
- Python 3.x インストール済み
- GmailのIMAPアクセスを有効にしていること
- Gmailの「アプリパスワード」が発行済み（2段階認証ONの場合）

### 2. 最初の実行で必要な情報

初回実行時に以下の情報を入力する必要があります：

- 学生番号
- LMSパスワード
- OTP用メールアドレス（Gmail想定）
- メールパスワード（またはアプリパスワード）

これらは`config.json`に保存され、次回からは入力不要です。

---

## 📂 ファイル構成

- `main.py` ： スクリプト本体
- `config.json` ： ログイン情報（自動生成）
- `chrome_profile/` ： Chromeのユーザープロファイル（自動生成）

---

## 🧠 主な処理の流れ

1. `launch_detached_chrome()`  
　Chromeをデバッグモード＆ユーザープロファイル付きで起動

2. `attach_to_chrome()`  
　Seleniumが起動中のChromeに接続

3. `load_or_create_config()`  
　設定ファイル（学生番号、パスワード、メール等）を読み込むか新規作成

4. `login_lms(driver, config)`  
　LMSへログイン（ユーザーID、パスワード）

5. `enter_otp(driver, config)`  
　GmailからOTPメールを取得し、自動で入力・ログイン

6. `close_extra_windows(driver)`  
　ログイン後、余計なウィンドウを自動で閉じる

---

## ⚙️ カスタマイズ可能な定数

```python
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = os.path.join(os.getcwd(), "chrome_profile")
DEBUG_PORT = 9222
OTP_SENDER = "slink-info@secioss.co.jp"
```

---

## 🐞 エラーが出るとき

- GmailのIMAPが有効になっているか確認
- アプリパスワードの使用
- Chromeのパスが間違っていないか確認
- 2段階認証メールが迷惑メールに分類されていないか確認

---

## 🔒 注意

- `config.json`にはパスワードが平文で保存されます。安全な環境で使用してください。
- セキュリティ上、スクリプトの取り扱いには十分注意してください。

---

## 📌 依存ライブラリ

標準ライブラリ：
- `os`, `sys`, `json`, `time`, `re`, `imaplib`, `email`, `getpass`, `subprocess`

外部ライブラリ：
- `selenium`

インストール：
```bash
pip install selenium
```

---

## 🏁 実行

```bash
python main.py
```

---

## 🧹 後始末

- `config.json`を削除すれば、次回から再入力が可能です。
- `chrome_profile`フォルダを削除すれば、Chromeのユーザーデータも削除されます。
