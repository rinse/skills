---
name: git-commit
description: Use this skill whenever performing a git commit. This includes when the user asks to commit changes, create a commit, save progress to git, or any variation of "commit this/these changes". Also triggers when using /commit or when a workflow involves creating git commits as a step.
---

# Git Commit

## ステージング (`git add`)

基本的に各ファイルを一つずつ指定してステージングしてください。

- `git add -A` は**禁止**です。意図しないファイルを巻き込む恐れがあるため使用しないこと。
- `git add -u` は**許可**されます（追跡中ファイルの変更・削除のみを対象とするため）。
- 通常は `git add path/to/file1 path/to/file2` のように対象ファイルを明示的に列挙すること。

## コミットメッセージ

コミットメッセージは一行で簡潔にしてください。

長い説明や複数行のメッセージは避け、変更内容を端的に伝える一行メッセージを書くこと。

**例:**

- `fix: resolve null pointer in user authentication`
- `feat: add CSV export to dashboard`
- `refactor: simplify database connection pooling`
