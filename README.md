# LMS Login — メールOTP認証のログイン補助

PythonとSeleniumで対象大学のLMSログイン画面を操作し、大学で登録したメールアドレスに届くワンタイムパスワード（OTP）を取得・入力する個人用CLIツールです。特定LMSの画面構造に合わせて作成しており、任意のLMSにそのまま対応するものではありません。

元のアプリはAI生成コードを用いて制作し、その後のコードレビュー・修正・テスト・説明文の作成にもAIツールを使用しています。

## 主な機能

- ChromeでLMSを開き、学生番号・パスワードを入力
- メールOTP認証方式の選択
- 指定送信元の未読メールからOTPを抽出・入力
- OTPの待機・再送・送信再試行
- 認証送信後のエラー非検出時に余分なウィンドウを閉じ、ブラウザを残す
- 設定JSONの読込・初回入力

## 使用技術・処理の構成

Python / Selenium / Chrome / 標準ライブラリのimaplib・email・unittest / PyInstaller / Ruff。

```text
Login.py → app.py（起動・終了処理）
              ├─ config.py（設定読込・入力・検証）
              └─ browser.py（LMS画面の操作）
                     └─ otp.py（IMAP取得・本文解析・期限付き待機）
```

## 技術的に工夫した点

- 画面操作とメール取得を組み合わせ、要素待機とOTP再試行を実装。
- 単調増加時計で待機期限を管理し、再送しても期限を延長しない。メール処理と画面操作を分離し、通信処理・時計・待機処理をテスト用に差し替えられるようにした。
- メールは新しいUIDから確認し、`BODY.PEEK[]` で取得。採用したOTPのメールだけを明示的に既読化する。
- 新規設定には学生番号とメールアドレスのみ保存し、パスワードは `getpass` で非表示入力する。環境変数・既存JSONからの読込にも対応するが、既存JSONのパスワードは平文で扱う。OTPや秘密をログに出さず、メール認証・通信エラーは理由を一般化して表示する。

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
docs/                    依存ライブラリ情報・補足資料
config.example.json      個人情報を含まない設定例
requirements*.txt        実行・開発用の依存関係
pyproject.toml           Ruff設定
```

## 起動・テスト

検証環境はWindows、Python 3.12.14です。ヘルプとユニットテストは、LMS・Gmailのアカウントなしで実行できます。リポジトリのフォルダでPowerShellから実行します。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe Login.py --help
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

実ログインにはChrome、対象LMSの利用権限、OTP通知先GmailのIMAP認証手段が必要です。環境変数 `LMS_URL` に対象LMSのHTTPS URLを指定し、`Login.py` を起動します。設定項目は [config.example.json](config.example.json) を参照してください。

`unittest` とモックを使い、外部サービスへ接続せずに次の処理を検証します。

- 設定の検証、新規保存時のパスワード除外、不正なJSONを上書きしないこと
- メールの文字コード・OTP形式の解析、使用済みコードの除外、採用したメールだけの既読化
- 再送で待機期限が延びないこと、送信回数の上限、例外時のブラウザ終了
- LMS URLの検証

ユニットテストの対象に、実サービスでのログイン確認は含まれません。

## 補足

- 認証送信後はエラー要素の不在で判定しており、ログイン成功そのものを確認する実装ではありません。
- OTPは指定送信元の未読メールのテキスト本文から抽出します。
- `LMS_URL` が未設定・不正な場合は、認証情報の入力前に終了します。
- 個人設定の `config.json`、Chromeプロファイル、ビルド生成物は `.gitignore` で管理対象から除外しています。

## 権利・ライセンス

使用している外部ライブラリは各ライブラリのライセンスに従います。本リポジトリの独自コードには現在ライセンスを設定していません。
