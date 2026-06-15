# Skills

## スキルの一覧

### gh-pr-create

現在のブランチから GitHub の Pull Request を作成するスキル。
差分の全体を読んでタイトルと本文を合成し、リポジトリに PR テンプレートがあればそれに従う。push はユーザーに任せ、作成前に内容を確認する。GitHub の PR 専用。

### gh-issue-create

雑な記述から GitHub の Issue を起票するスキル。
やりたいことを構造化された本文に合成し、リポジトリに ISSUE_TEMPLATE があればそれに従い、なければ概要・目的・制約・受け入れ条件のテンプレートを使う。作成前に内容を確認する。GitHub 専用。

### gh-review

GitHub の Pull Request に対してコードレビューを行うスキル。
変更を確認し、該当する行に severity タグ付きのインラインコメントを投稿する。GitHub の PR 専用。

### gh-merge

GitHub の Pull Request をマージするスキル。
主に squash merge を対象とし、差分の全体を読んで短く適切な squash commit メッセージを合成し、実行前に内容を確認する。GitHub の PR 専用。

### gh-release

最後のリリース以降の差分を読み、新しいセマンティックバージョンを切るスキル。
トークンを食う差分の読解は Haiku の Subagent に委譲し、オーケストレーターがログと報告を突き合わせて bump 種別（major/minor/patch）を判断して次バージョンを算出する。リリースノートを合成して注釈付きタグを作成、任意で GitHub Release も作る。0.x の特例（破壊的変更でも minor）に対応し、push はユーザーに任せ、作成前に内容を確認する。

### gh-init

ローカルの git リポジトリに対して GitHub 上のリモートリポジトリを作成するスキル。
`gh`（なければ GitHub MCP）でリポジトリを作成して `origin` として登録する。push はユーザーに任せる。

### git-commit

git のコミットを行うスキル。
変更内容を確認し、単一行のコミットメッセージでコミットする。

### concurrent-dev

複数の開発タスクを並列に進めるスキル。
オーケストレーター（Fable 5 / Opus 級）が依存関係・優先順位・競合を判断して実行計画を立て、プロジェクトルート下 `.wt/` の worktree を準備し、開発作業だけを想定難易度に応じた Sonnet / Opus の Subagent に委譲してコストを削減する。レビュー・マージ・後片付けはオーケストレーター自身が行い、一貫性を保つ。依存で一本鎖になるタスクは無理に並列化せず直列で進める。

### git-init

git リポジトリを初期化するスキル。
`git init` を実行し、git プロファイル（ユーザー名・メールアドレス）を切り替えて、空の初期コミットを作成する。

### tdd

Kent Beck の "Canon TDD" の定義に基づいてテスト駆動開発を進めるスキル。
テストリスト → Red → Green → Optionally Refactor のサイクルを1テストずつ回し、インターフェイス設計と実装設計を分けて「動かす」と「きれいにする」を同時にやらない規律を提供する。各ステップで陥りがちな間違いも示す。

### playwright-cli-auth

playwright-cli で認証をユーザーに行わせるスキル。
認証時だけ playwright-cli を headful で表示し、ユーザーにログイン操作を行わせた後、headless モードに戻って操作を続行する。

### quiver-diagram

[quiver](https://q.uiver.app/) 上で可換図式を作成して、そのリンクを作るスキル。
