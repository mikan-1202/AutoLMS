# 検証結果

検証日：2026年9月30日。Windows / Python 3.12.14。

| 項目 | 結果 |
|---|---|
| 新規 `.venv` への `requirements-dev.txt` 導入 | 成功（ネットワークアクセスが必要） |
| `python -m pip check` | 依存関係の不整合なし |
| `python -m unittest discover -s tests -v` | 15件成功 |
| 個人設定・プロファイルを含まないソースコピーで同じテスト | 15件成功。依存導入済みの同じ仮想環境を使用 |
| Ruff check / format --check | 成功 |
| `python Login.py --help` | 成功。ソースコピーでも確認 |
| PyInstallerによるビルド | 成功。旧distを上書きせず `.local-review/dist/Login.exe` に出力 |
| ビルドした `Login.exe --help` | 成功 |
| Gitの公開除外ルール | ローカル監査用Gitディレクトリを使い、config・profile・build・dist・venv・作業記録の除外を確認 |
| 公開候補テキストと既存configの値の照合 | 一致なし。秘密の値は出力していない |
| 過去のGit履歴 | 元の作業フォルダに存在せず確認不可 |
| 実Chrome起動・Gmail接続・LMS認証 | 未検証 |

テストは実際のアカウントを使わず、メールサーバーとブラウザをモックに置き換えている。ビルド成功とヘルプ表示は、実ブラウザ操作の成功を保証しない。

秘密情報確認は公開候補のソース・設定例・説明資料を対象とする。公開除外したChromeプロファイルの内部や過去のexe内に情報がないことは保証しない。元データは削除していないため、フォルダ丸ごとの公開は避ける。

## ローカル比較の再確認

`docs/source-changes.diff` に、変更前の2ファイルと変更後のソース・テスト・設定の差分を保存した。差分内の `before/`・`after/` は比較用のディレクトリ名で、過去のブランチ名ではない。

```powershell
git apply --stat docs/source-changes.diff
Get-FileHash .local-review/before/Login.py -Algorithm SHA256
Get-FileHash .local-review/before/Login.spec -Algorithm SHA256
```

作業フォルダのGit初期化・コミット・GitHub公開は実施していない。除外確認用の一時的なGit管理領域は `.local-review/audit-git/` 内にのみ作成し、過去の履歴としては利用していない。

## 公開版の確認（2026年10月2日）

上記は9月30日の元版の検証記録。公開版は独立したGitリポジトリとして初期化したが、コミット・リモート設定・公開は未実施。`.local-review` は公開版に含めないため、上記の原本ハッシュ確認コマンドは元の作業フォルダでのみ実行できる。匿名化後の公開版はユニットテスト17件成功、Ruff lint、CLIヘルプ表示の成功を確認した。公開版のexe再ビルド・実認証は未検証。


## 既存公開版からの更新

公開準備時にGitHub上の2025年7月20日の履歴を確認した。比較元は `REDACTED_PRE_CLEANUP_COMMIT`。旧公開版との違いと履歴の扱いは [改善記録](improvements.md) を参照。`python main.py` も互換用の入口として利用できる。最新版の匿名化は過去のコミットに残る大学名・作者メールを削除するものではない。
