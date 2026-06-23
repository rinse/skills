---
name: git-commit
description: Use this skill whenever performing a git commit. This includes when the user asks to commit changes, create a commit, save progress to git, or any variation of "commit this/these changes". Also triggers when using /commit or when a workflow involves creating git commits as a step.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# Git Commit

## ステージング (`git add`)

基本的に各ファイルを一つずつ指定してステージングしてください。

- `git add -A` は**禁止**です。意図しないファイルを巻き込む恐れがあるため使用しないこと。
- `git add -u` は**許可**されます（追跡中ファイルの変更・削除のみを対象とするため）。
- 通常は `git add path/to/file1 path/to/file2` のように対象ファイルを明示的に列挙すること。

### 同一ファイルの一部だけをコミットする場合

一つのファイルに今回のコミットと無関係な変更が同居している場合、ハンク選択（`git add -p` / `git apply --cached`）に頼らないこと。1 行の中に複数の関心事が同居しているとハンクでは物理的に分けられず破綻する。LLM は「適用できるパッチを切り出す」のは苦手で、「正しいファイル内容を書く」のは得意なので、**内容を直接書く**方が確実:

1. 現在の全内容を控える
2. Write でファイルを**このコミットに含めるべき内容**に書き直し、`git add path/to/file` してコミットする
3. ファイルを控えた全内容に書き戻す（残りの変更が作業ツリーに復元される）

最後に `git diff` で、残った変更が意図どおりであることを確認すること。

## コミットメッセージ

コミットメッセージは一行で簡潔にしてください。

長い説明や複数行のメッセージは避け、変更内容を端的に伝える一行メッセージを書くこと。

**例:**

- `fix: resolve null pointer in user authentication`
- `feat: add CSV export to dashboard`
- `refactor: simplify database connection pooling`
