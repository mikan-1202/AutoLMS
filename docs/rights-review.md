# 制作経緯と依存ライブラリ

## コードの制作経緯

作者の2026年10月2日の説明では、元コードは2025年頃にGPTを使って生成したものです。参考コード・教材等は入力していないとの説明を受けています。

その後のコードレビュー、修正、テスト、説明資料の作成にもAIツールを使用しています。変更内容は [改善記録](improvements.md) にまとめています。

## 主要依存のライセンス

2026年10月2日に記録した、導入済みパッケージのメタデータと公式資料に基づく一覧です。

| 対象 | 検証時バージョン | ライセンス | 用途 |
|---|---|---|---|
| Selenium | 4.49.0 | Apache-2.0 | ブラウザ操作 |
| Ruff | 0.16.9 | MIT | コード検査・整形 |
| PyInstaller | 6.22.3 | GPLv2以降＋配布に関する特別例外 | 実行ファイルのビルド |

公式参照先：

- [Selenium LICENSE](https://github.com/SeleniumHQ/selenium/blob/trunk/LICENSE)
- [Ruff LICENSE](https://github.com/astral-sh/ruff/blob/main/LICENSE)
- [PyInstaller License](https://pyinstaller.org/en/stable/license.html)

依存パッケージはrequirementsから導入します。このリポジトリにライブラリ本体、ビルド済みexe、Chromeプロファイル、認証情報ファイル、画像・ロゴ、Webページの保存データは含めていません。

## このプロジェクトのライセンス

本プロジェクト独自の再利用ライセンスは付与していません。上記のライセンスは各依存ライブラリに適用されます。
