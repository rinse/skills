---
name: gh-review
description: Use this skill whenever the user asks for a code review of a GitHub pull request. Triggers on phrases like "コードレビューをして", "レビューして", "code review", "review this PR", "PR をレビュー", or any request to review changes on a GitHub PR. This skill posts inline comments to specific lines of a GitHub PR with severity tags. It is GitHub-PR-only — if the target is not a GitHub PR, this skill does not apply.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# GitHub PR Code Review

GitHub の PR に対して、コードの特定箇所へ **inline comment** を付けてレビューするためのスキルです。指摘には深刻さを表すタグを付けます。

**このスキルは GitHub の PR 専用です。** GitHub の PR でない場合（GitHub リポジトリでない、GitLab 等の別ホスト、ローカル変更のみ等）は、このスキルの対象外なので何もしません。

## 全体の流れ

1. 対象 PR を特定する
2. 差分を取得してレビューする
3. 指摘を inline comment として組み立てる（severity タグ付き）
4. ユーザーに内容を見せて確認を取る
5. レビューを投稿する

## 1. 対象 PR の特定

まず前提として、**`gh` コマンドが無い場合**（`command -v gh` で確認）→ このスキルは `gh` に依存する。未インストールならその旨を伝え、**インストールするかどうかユーザーに尋ねる**。希望する場合は実行環境（OS / パッケージマネージャ）に合った方法でインストールして続行する（方法は環境に応じて判断。公式は https://cli.github.com ）。希望しない場合はここで終了する。「`gh` が無い」ことと「GitHub リポジトリでない」ことは別物なので混同しない。

レビュー対象の PR を確定させます。

- **PR 番号や URL が指定されている場合** → それを使う。
- **指定がない場合** → 現在のブランチに紐づく PR を `gh pr view` で探す。

```
gh pr view --json number,title,headRefName,url
```

結果によって分岐します。

- **PR が見つかった場合** → その PR を対象にする。番号を控えておく（以降 `<PR番号>`）。
- **GitHub リポジトリだが現在のブランチに PR がない場合** → 黙って止まらず、どの PR をレビューするかユーザーに尋ねる（番号 / URL）。「PR が見つからない」ことと「GitHub でない」ことは別物。
- **そもそも GitHub リポジトリでない場合**（`gh` がリポジトリを認識しない／別ホストのリモート等） → このスキルの対象外。その旨を伝えて終了する。

## 2. 差分の取得とレビュー

PR の差分を取得します。

```
gh pr diff <PR番号>
```

差分を読み、コードレビューを行います。レビューの観点はコードの性質に応じて判断してください（バグ・正しさ、セキュリティ、設計、可読性、テスト漏れ、命名など）。指摘ごとに「どのファイルの何行目か」を必ず押さえます。

**重要 — コメントを付けられる行:** inline comment は **diff のハンク内に現れる行**にしか付けられません（変更行および前後のコンテキスト行）。差分に含まれない行を指定すると API が 422 で失敗します。`gh pr diff` の出力を見て、コメント対象の行が差分内にあることを確認してください。

行番号の数え方:
- **追加行・コンテキスト行**（新しい側）→ 新ファイル側の行番号を使い、`side` は `RIGHT`。
- **削除行**（古い側）→ 旧ファイル側の行番号を使い、`side` は `LEFT`。
- **複数行にまたがる指摘** → 開始行を `start_line`、終了行を `line` で指定する。

## 3. severity タグ

各指摘の本文 (`body`) の先頭にタグを付け、対応の必要度を伝えます。

- `[対応必須]` — 必ず直してほしい点（バグ、セキュリティ問題、明確な不具合、壊れる変更など）
- `[対応任意]` — 対応の判断を著者に任せる点（改善提案、より良い書き方の提示など）
- **(タグなし)** — その他（軽微な指摘、nit、疑問、質問、補足、良い点への言及など）

**例:**

- `[対応必須] この分岐では null チェックが抜けており、空入力で例外になります。`
- `[対応任意] ここはマップで書くと分岐が減って読みやすくなります。`
- `commit_id を毎回取得していますが、ループ外に出せそうです。`（タグなし = nit）

タグはエージェントの判断で付けず、深刻さを実際に見極めて選んでください。`[対応必須]` を乱発すると著者の負担になります。

## 4. 投稿内容の確認

レビューの投稿は**外向きの操作**で、PR の関係者に通知され取り消しづらいので、投稿前に必ずユーザーに内容を見せて了承を取ります。

提示する内容:
- 全体サマリー（任意、レビュー全体の所見）
- 各 inline comment の「ファイル:行」「タグ」「本文」の一覧

ユーザーが了承したら次へ進みます。修正指示があれば反映してから再提示します。

## 5. レビューの投稿

inline comment は1件ずつ投稿するのではなく、**1つのレビューにまとめて**投稿します（通知が1回で済み、レビューとして筋が通るため）。`POST /repos/{owner}/{repo}/pulls/<PR番号>/reviews` を使います。`{owner}` と `{repo}` は `gh` がカレントリポジトリから自動補完します。

コメントの多い JSON はコマンドラインで組むと壊れやすいので、JSON ファイルを作って `--input` で渡します。

`review.json` の例:

```json
{
  "event": "COMMENT",
  "body": "全体としては良い変更です。いくつか指摘します。",
  "comments": [
    {
      "path": "src/auth.py",
      "line": 42,
      "side": "RIGHT",
      "body": "[対応必須] この分岐では null チェックが抜けており、空入力で例外になります。"
    },
    {
      "path": "src/util.py",
      "start_line": 10,
      "line": 15,
      "side": "RIGHT",
      "body": "[対応任意] この範囲はヘルパー関数に切り出すと読みやすくなります。"
    }
  ]
}
```

投稿コマンド:

```
gh api --method POST /repos/{owner}/{repo}/pulls/<PR番号>/reviews --input review.json
```

### event は COMMENT を既定にする

`event` は `COMMENT` を既定とします。`[対応必須]` の指摘があっても、勝手に `REQUEST_CHANGES` に上げないこと。**PR をブロックするかどうかはユーザーの判断**であり、スキルが先回りして決めるべきではありません。明示的に「変更を要求して」「approve して」と言われた場合のみ `REQUEST_CHANGES` / `APPROVE` を使います。

### 投稿後

レビューの URL（`gh api` の応答に含まれる `html_url`）をユーザーに伝えます。一時的に作った `review.json` は片付けます。

## フォールバック: GitHub MCP

`gh` が使えず GitHub MCP が利用できる環境では、GitHub MCP の PR レビュー作成ツール（保留レビューの作成 → inline コメントの追加 → レビューの送信、もしくはレビューの一括作成）で同じことを行います。その場合も「line/side に基づく inline コメント」「severity タグ」「投稿前の確認」「event は COMMENT 既定」という方針は変わりません。
