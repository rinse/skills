---
name: git-commit
description: Commit with explicitly listed files and a one-line conventional-commit message. Use whenever making a git commit, including as a step inside another workflow.
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

1. 現在の全内容を、作業ツリーの外の、セッションの一時領域へコピーして退避する。作業ツリーの中に置くとコピー自体がコミットに巻き込まれうる。エージェントのコンテキストに控えるだけでは、途中で失敗した場合に未コミットの変更が失われてしまう。
2. Write でファイルを**このコミットに含めるべき内容**に書き直し、`git add path/to/file` してコミットする
3. 退避したコピーからファイルを書き戻す（残りの変更が作業ツリーに復元される）

手順 2 が失敗して作業を止める場合も、止まる前に退避したコピーから書き戻し、書き戻したことと退避コピーの場所を報告する。書き直した内容のまま止まると、残りの変更が作業ツリーから消えたように見える。

最後に `git diff` で、残った変更が意図どおりであることを確認すること。確認できたら退避コピーを削除する。

## フックの失敗は直して新しくコミットする

pre-commit フックが失敗したときはコミットが作られていないので、原因を直して再度ステージし、新しくコミットする。`--amend` は直前の別のコミットを書き換えるので使わない。`--no-verify` で検査を飛ばすのはユーザーが明示したときだけにする。フックがファイルを書き換えた場合は、書き換え後の差分を確認してからステージし直す。直せない失敗は、フックの出力を示して止まる。

## コミットメッセージ

コミットメッセージは一行で簡潔にしてください。

長い説明や複数行のメッセージは避け、変更内容を端的に伝える一行メッセージを書くこと。

**conventional-commit 風の prefix を付けること。** `feat:` / `fix:` / `refactor:` / `docs:` / `chore:` 等、変更の種類を表す prefix をメッセージ先頭に付ける。これは本スキル固有の規約であり、他のスキルからも「git-commit の規約に従う」という形で参照される。

**例:**

- `fix: resolve null pointer in user authentication`
- `feat: add CSV export to dashboard`
- `refactor: simplify database connection pooling`
