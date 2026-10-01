# 公開履歴のプライバシー対策

2026年10月2日、公開履歴7コミットの大学名・接続先ドメイン・個人用メールアドレスを置換した。作者・コミッターのメールはGitHub noreplyアドレスへ統一。既存の履歴は内容を匿名化した形で保持し、コミットIDと署名は変更されている。

調査時点の公開参照はmainのみ。タグ・PR・リリースなし、GitHubのフォーク数は0。書き換えは更新前の先端を指定したforce-with-leaseで反映する。

旧クローンからpullしてmerge/pushすると除去した履歴が復活する可能性があるため、以後は新しくcloneして使用する。過去の識別子や未加工の差分を再掲載しない。

## 残る限界

公開前に取得されたコピーやGitHubの旧コミットキャッシュは、Gitの履歴置換だけでは削除できない。GitHub Supportへのキャッシュ・参照削除依頼が必要になる場合があり、対応可否はGitHubが判断する。

[GitHub公式の機密データ削除手順](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
