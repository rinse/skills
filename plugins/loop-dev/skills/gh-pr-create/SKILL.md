---
name: gh-pr-create
description: Create a GitHub pull request from the current branch, synthesizing the title and body from the full diff. Use when asked to create or open a PR (PR を作って, create a PR). GitHub only.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# GitHub PR Create

現在のブランチから GitHub の Pull Request を作成するスキルです。`gh pr create --fill` のように中間コミットのメッセージを流用せず、差分全体を読んでタイトルと本文を合成するのが核です。

## 前提

- `gh` が必要（無ければ導入を提案する。GitHub MCP があればそれで代替してよい）。GitHub リポジトリでなければ対象外。
- 現在ブランチがデフォルトブランチなら PR は作れない。ブランチを切るよう促す。
- 未コミットの変更は PR に含まれない。先にコミットするか（git-commit の規約で）、そのまま進めるかを確認する。

## 差分の収集

base はリポジトリのデフォルトブランチ（`gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`）。ローカルの base は origin より遅れていることがあるので、origin 側を基準にする。

```
git fetch origin <base>
git -P diff origin/<base>...HEAD
git --no-pager log origin/<base>..HEAD
```

## タイトル・本文・ラベルの合成

- タイトルは変更の目的を一行で。conventional-commit 風 prefix（`feat:` / `fix:` / `refactor:` 等）を付ける。
- PR テンプレート（`.github/PULL_REQUEST_TEMPLATE.md`、`PULL_REQUEST_TEMPLATE.md`、`docs/PULL_REQUEST_TEMPLATE.md`、`.github/PULL_REQUEST_TEMPLATE/`）があれば各セクションを実内容で埋める。プレースホルダやコメントを残さない。複数あれば内容に最も合うものを選ぶ。
- 無ければ「## 概要（なぜ何を変えるか）」「## 変更点（箇条書き）」の 2 節で書く。
- ラベルは `gh label list` の既存ラベル（description も読む）から、内容に確信を持てるものだけを選ぶ。無いラベルは作らない。付けすぎない。

## push

`git push origin <branch>` を一度試す。認証などで失敗したら繰り返さず、そのコマンドを示してユーザーに push を依頼する。

## 確認と作成

PR 作成は関係者に通知される取り消しづらい操作なので、タイトル・本文・base/head・ラベルを提示して了承を得てから作成する。本文はファイルに書いて `--body-file` で渡す。draft はユーザーが明示したときだけ。

```
gh pr create --base <base> --head <branch> --title "feat: ..." --body-file <path> --label "<label>"
```

作成した PR の URL を報告する。
