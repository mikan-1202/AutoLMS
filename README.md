# LMS Login — メールOTP認証のログイン補助

PythonとSeleniumで対象大学のLMSログイン画面を操作し、大学で登録したメールアドレスに届くワンタイムパスワード（OTP）を取得・入力する個人用CLIツールです。特定LMSの画面構造に合わせて作成しており、任意のLMSにそのまま対応するものではありません。

元のアプリはAI生成コードを用いて制作し、その後のコードレビュー・修正・テスト・説明文の作成にもAIツールを使用しています。

## 作った目的

LMS利用時の学生番号・パスワード入力と、メールを開いてOTPを転記する操作を補助するアプリです。

## 主な機能

- ChromeでLMSを開き、学生番号・パスワードを入力
- メールOTP認証方式の選択
- 指定送信元の未読メールから8桁のOTPを抽出・入力
- OTPの待機・再送・送信再試行
- 認証送信後のエラー非検出時に余分なウィンドウを閉じ、ブラウザを残す
- 設定JSONの読込と初回入力（新規保存ではパスワードを保存しない）

## 使用技術・処理の構成

Python / Selenium / Chrome / 標準ライブラリのimaplib・email・unittest / PyInstaller / Ruff。

```text
Login.py → app.py（起動・終了処理）
              ├─ config.py（設定読込・入力・検証）
              └─ browser.py（LMS画面の操作）
                     └─ otp.py（IMAP取得・本文解析・期限付き待機）
```

## 技術的に工夫した点

- 画面操作とメール取得を組み合わせ、要素待機とOTP再試行を実装。パスワード入力に `getpass` を使用。
- 単調増加時計で待機期限を管理し、再送しても期限を延長しない。メール処理と画面操作を分離し、通信処理・時計・待機処理をテスト用に差し替えられるようにした。
- メールは新しいUIDから確認し、`BODY.PEEK[]` で取得。採用したOTPのメールだけを明示的に既読化する。
- 既存JSONとの互換性を保ち、新規設定のパスワード保存とOTPのログ出力を避ける。

接続先・待機時間・試行回数は `settings.py`、画面のセレクターと操作順序は `browser.py` にまとめています。画面仕様が変わった場合は画面操作を、メール本文の形式が変わった場合は `otp.py` の解析処理を確認・修正する構成です。

## プロジェクト構成

```text
Login.py / main.py       起動入口（main.pyは互換用）
Login.spec               コンソール付き実行ファイルのビルド設定
lms_login/
  app.py                 CLI・異常時の終了
  config.py              設定の読込・検証
  browser.py             Seleniumによる画面操作
  otp.py                 メール解析・取得・待機
  settings.py            接続先・待機時間・試行回数
tests/                   外部サービス不要のユニットテスト
docs/                    検証結果・依存ライブラリ情報・補足資料
config.example.json      個人情報を含まない設定例
requirements*.txt        実行・開発用の依存関係
pyproject.toml           Ruff設定
```

## 導入・実行

検証環境はWindows、Python 3.12.14です。実ログインにはChrome、対象LMSの利用権限、OTP通知先GmailのIMAP認証手段が必要です。ヘルプとユニットテストはアカウントなしで実行できます。

リポジトリのフォルダで、PowerShellから実行します。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe Login.py --help
$env:LMS_URL = "https://実際のLMSのホスト名/"
.\.venv\Scripts\python.exe Login.py
```

初回は学生番号・Gmailアドレス・各パスワードを入力します。新規の `config.json` には学生番号とメールアドレスのみ保存し、パスワードは `getpass` で非表示入力します。設定例は [config.example.json](config.example.json)、別の設定ファイルの指定は `--config path\to\config.json` です。

既存JSONの `password`・`email_password` と、環境変数 `LMS_PASSWORD`・`LMS_EMAIL_PASSWORD` にも対応しています。優先順位は環境変数 → 既存JSON → 対話入力です。既存JSONのパスワードは平文のため、対話入力に切り替える場合はその2項目を削除してください。

`LMS_URL` には対象LMSのHTTPS URLを指定します。未設定・不正な場合は認証情報の入力前に終了します。初回のChromeDriver準備にはダウンロードが発生する場合があります。

処理後はLMS画面でログイン状態を確認し、利用後にChromeを閉じてください。途中終了は `Ctrl+C`、失敗時は起動したブラウザの終了を試みます。

## テスト・整形・ビルド

`unittest` とモックを使い、実際のLMS・Gmailへ接続せずに次の処理を検証します。

- 設定の検証、新規保存時のパスワード除外、不正なJSONを上書きしないこと
- メールの文字コード・OTP形式の解析、使用済みコードの除外、採用したメールだけの既読化
- 再送で待機期限が延びないこと、送信回数の上限、例外時のブラウザ終了
- LMS URLの検証

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m ruff check Login.py lms_login tests
.\.venv\Scripts\python.exe -m ruff format --check Login.py lms_login tests
.\.venv\Scripts\python.exe -m PyInstaller Login.spec
```

ビルド後は `dist\Login.exe` を起動します。設定の既定位置は実行ファイルの隣です。対話入力を行うためコンソール付きです。実行用依存と開発ツールを分け、バージョン範囲を指定しています。検証履歴は [検証結果](docs/validation.md) に記載しています。ユニットテストは実サービスでのログイン確認を代替するものではありません。

## 利用時の注意

- 自分が利用権限を持つアカウントと、所属先が許可する範囲で利用してください。
- 個人設定の `config.json`、Chromeプロファイル、ビルド生成物は `.gitignore` で管理対象から除外しています。
- 認証送信後はエラー要素の不在で判定しており、ログイン成功そのものを確認する実装ではありません。
- OTPは指定送信元の未読メールのテキスト本文から8桁の形式で抽出します。
- メール認証・通信エラーは理由を一般化して表示し、処理を終了します。サービスの応答本文や秘密は出力しません。

## 権利・ライセンス

依存ライブラリのライセンスとコードの制作経緯は [権利確認記録](docs/rights-review.md) に記載しています。本プロジェクト独自の再利用ライセンスは現時点では付与していません。
