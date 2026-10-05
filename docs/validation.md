# 検証結果

## 2026年9月30日

環境：Windows / Python 3.12.14。

| 項目 | 結果 |
|---|---|
| 新規 `.venv` への `requirements-dev.txt` 導入 | 成功 |
| `python -m pip check` | 依存関係の不整合なし |
| `python -m unittest discover -s tests -v` | 15件成功 |
| 個人設定・プロファイルを含まないソースコピーで同じテスト | 15件成功 |
| Ruff check / format --check | 成功 |
| `python Login.py --help` | 成功 |
| PyInstallerによるビルド | 成功 |
| ビルドした `Login.exe --help` | 成功 |
| Gitの公開除外ルール | config・profile・build・dist・venv・作業記録の除外を確認 |
| 公開候補テキストと既存configの値の照合 | 一致なし |

ユニットテストではメールサーバーとブラウザをモックに置き換え、設定、メール解析、待機・再送、例外時の終了処理を検証しています。

## 2026年10月2日

匿名化後の公開版で、ユニットテスト17件、Ruff lint、CLIヘルプ表示の成功を確認しました。

## ソースの比較

[ソース差分](source-changes.diff) に、変更前の2ファイルと変更後のソース・テスト・設定の差分を保存しています。`before/`・`after/` は比較用のディレクトリ名です。

```powershell
git apply --stat docs/source-changes.diff
```

公開版では `python main.py` も互換用の入口として利用できます。変更内容は [改善記録](improvements.md) を参照してください。
