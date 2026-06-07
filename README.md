# Skills

## スキルの一覧

### gh-pr-create

現在のブランチから GitHub の Pull Request を作成するスキル。
差分の全体を読んでタイトルと本文を合成し、リポジトリに PR テンプレートがあればそれに従う。push はユーザーに任せ、作成前に内容を確認する。GitHub の PR 専用。

### gh-review

GitHub の Pull Request に対してコードレビューを行うスキル。
変更を確認し、該当する行に severity タグ付きのインラインコメントを投稿する。GitHub の PR 専用。

### git-commit

git のコミットを行うスキル。
変更内容を確認し、単一行のコミットメッセージでコミットする。

### git-init

git リポジトリを初期化するスキル。
`git init` を実行し、git プロファイル（ユーザー名・メールアドレス）を切り替えて、空の初期コミットを作成する。

### git-merge

`gh` コマンド・GitHub MCP ツール・`git merge` でコードをマージするスキル。
マージ戦略（squash か merge commit か）に応じたマージコミットメッセージの書き方を案内する。

### playwright-cli-auth

playwright-cli で認証をユーザーに行わせるスキル。
認証時だけ playwright-cli を headful で表示し、ユーザーにログイン操作を行わせた後、headless モードに戻って操作を続行する。

### quiver-diagram

[quiver](https://q.uiver.app/) 上で可換図式を作成して、そのリンクを作るスキル。
