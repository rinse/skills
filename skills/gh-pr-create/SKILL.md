---
name: gh-pr-create
description: Use this skill whenever the user asks to create a GitHub pull request. Triggers on phrases like "PR を作って", "プルリクを作成", "create a PR", "open a pull request", "PR 出して", or any request to open a pull request from the current branch. This skill collects the full diff, synthesizes a clean title and body, and creates the PR after confirmation. It is GitHub-PR-only — if the target is not a GitHub repository, this skill does not apply.
---

# GitHub PR Create

現在のブランチから GitHub の Pull Request を作成するためのスキルです。差分の全体を読み、きれいなタイトルと本文を**合成**してから、確認を取って PR を作成します。

**このスキルは GitHub の PR 作成専用です。** GitHub リポジトリでない場合（別ホストのリモート、リモート未設定等）は、このスキルの対象外なので何もしません。

`gh pr create --fill` とは違い、中間コミットの雑なメッセージを流用しません。差分全体を読んでタイトル・本文を組み立てるのが、このスキルの核です。

## 全体の流れ

1. ガードと前提確認
2. base ブランチの特定
3. コンテキスト（差分・ログ）の収集
4. 本文テンプレートの判定
5. タイトル・本文の生成
6. ブランチが origin に push 済みか確認（未 push ならユーザーに push を依頼）
7. ユーザーに内容を見せて確認を取る
8. PR を作成する
9. 後処理

## 1. ガードと前提確認

- **`gh` コマンドが無い場合**（`command -v gh` で確認）→ このスキルは `gh` に依存する。未インストールならその旨を伝え、**インストールするかどうかユーザーに尋ねる**。希望する場合は実行環境（OS / パッケージマネージャ）に合った方法でインストールして続行する（方法は環境に応じて判断。公式は https://cli.github.com ）。希望しない場合はここで終了する。「`gh` が無い」ことと「GitHub リポジトリでない」ことは別物なので混同しない。
- **そもそも GitHub リポジトリでない場合**（`gh` がリポジトリを認識しない／別ホストのリモート等）→ このスキルの対象外。その旨を伝えて終了する。
- **現在ブランチがデフォルトブランチそのものの場合**（後述の base と同じ）→ PR は作成できない。ブランチを切るよう促して停止する。

## 2. base ブランチの特定

base（マージ先）はリポジトリのデフォルトブランチを既定とします。

```
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
```

通常は `main`。以降この値を `<base>`、現在のブランチを `<branch>` とします。

## 3. コンテキストの収集

PR の中身を理解するため、変更の全体を読みます。

```
git -P diff <base>...HEAD
git --no-pager log <base>..HEAD
```

`git -P diff <base>...HEAD`（3点）は、`<base>` から分岐したあとの差分を見せます。これとコミットログの両方から、PR が「なぜ・何を」変えるのかを把握します。

## 4. 本文テンプレートの判定

リポジトリに PR テンプレートがあれば、それに沿って本文を書きます。次の場所を確認します（大文字小文字の違いも含む）。

- `.github/PULL_REQUEST_TEMPLATE.md`
- リポジトリ直下の `PULL_REQUEST_TEMPLATE.md`
- `docs/PULL_REQUEST_TEMPLATE.md`
- `.github/PULL_REQUEST_TEMPLATE/`（複数テンプレートのディレクトリ）

- **テンプレートがある場合** → その各セクションを、収集した差分の内容で埋める。空欄やコメント（`<!-- -->`）のプレースホルダはそのまま残さず、実際の内容に置き換える。複数テンプレートのディレクトリがある場合は、変更内容に最も合うものを選ぶ（迷えばユーザーに尋ねる）。
- **テンプレートがない場合** → 次のフォールバック構成で書く。

```markdown
## 概要

〜の理由で〜を行う変更です。

## 変更点

- A を追加
- B を修正
```

## 5. タイトルの生成

タイトルは、変更の目的・結果を端的に伝える一行にします。conventional-commit 風の prefix を付けます（既存の git スキルと統一）。

- 例: `feat: add CSV export to dashboard`
- 例: `fix: resolve null pointer in user authentication`
- 例: `refactor: simplify database connection pooling`

## 6. push の確認

`gh pr create` は対象ブランチが origin に無いと push を試みますが、SSH 鍵のパスフレーズ入力が必要な場合、`! ` で実行するサブシェルではパスフレーズを入力できず失敗します。**このスキルは push しません。**

まず origin に push 済みかを確認します。

```
git rev-parse --abbrev-ref --symbolic-full-name @{u}
```

- **upstream があり、ローカルと差分がない場合** → push 済み。次へ進む。
- **未 push、または origin に未反映のコミットがある場合** → ユーザー自身に push を依頼する（push 先は常に明示する）。

ユーザーへの案内:

1. `Ctrl+Z` で Claude Code を一時停止する
2. 自分のシェルで `git push origin <branch>` を実行する（ここでパスフレーズを入力できる）
3. `fg` で Claude Code に戻ってくる

push が済んだことを確認してから次へ進みます。

## 7. 投稿内容の確認

PR の作成は**外向きの操作**で、リポジトリの関係者に通知され取り消しづらいので、作成前に必ずユーザーに内容を見せて了承を取ります。

提示する内容:

- タイトル
- 本文
- base（マージ先）と head（作成元ブランチ）

ユーザーが了承したら次へ進みます。修正指示があれば反映してから再提示します。

## 8. PR の作成

本文はコマンドラインで直接渡すと壊れやすいので、ファイルに書き出して `--body-file` で渡します。

```
gh pr create --base <base> --head <branch> --title "feat: ..." --body-file pr-body.md
```

- draft は既定では作らない。ユーザーが「draft で」と明示した場合のみ `--draft` を付ける。

## 9. 後処理

作成された PR の URL をユーザーに伝えます。一時的に作った本文ファイル（`pr-body.md` 等）は片付けます。

## フォールバック: GitHub MCP

`gh` が使えず GitHub MCP が利用できる環境では、GitHub MCP の PR 作成ツールで同じことを行います。その場合も「差分から本文を合成」「テンプレートがあれば従う」「push はユーザーに任せる」「作成前の確認」という方針は変わりません。
