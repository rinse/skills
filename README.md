# Skills

## スキルの一覧

### gh-pr-create

現在のブランチから GitHub の Pull Request を作成するスキル。
差分の全体を読んでタイトルと本文を合成し、リポジトリに PR テンプレートがあればそれに従う。push はユーザーに任せ、作成前に内容を確認する。GitHub の PR 専用。

### gh-review

GitHub の Pull Request に対してコードレビューを行うスキル。
変更を確認し、該当する行に severity タグ付きのインラインコメントを投稿する。GitHub の PR 専用。

### gh-merge

GitHub の Pull Request をマージするスキル。
主に squash merge を対象とし、差分の全体を読んで短く適切な squash commit メッセージを合成し、実行前に内容を確認する。GitHub の PR 専用。

### git-commit

git のコミットを行うスキル。
変更内容を確認し、単一行のコミットメッセージでコミットする。

### commit-split

散らかった作業ツリーや WIP コミットを、レビューに耐える綺麗なコミット列へ整理するスキル。
デフォルトで `main`（明示されればそのベース）からの全変更を入力とし、関心事ごとに分割・依存順に並べ替える。同一ファイルの分割はハンク選択ではなく中間状態の内容を書き直して行い、各コミットが単独で緑（test/build/lint が通る）になることを検証する。最終的な追跡ツリーは入力とバイト単位で一致し、履歴の形だけを変える。

### git-init

git リポジトリを初期化するスキル。
`git init` を実行し、git プロファイル（ユーザー名・メールアドレス）を切り替えて、空の初期コミットを作成する。

### playwright-cli-auth

playwright-cli で認証をユーザーに行わせるスキル。
認証時だけ playwright-cli を headful で表示し、ユーザーにログイン操作を行わせた後、headless モードに戻って操作を続行する。

### quiver-diagram

[quiver](https://q.uiver.app/) 上で可換図式を作成して、そのリンクを作るスキル。
