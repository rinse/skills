---
name: gh-pr-create
description: Use this skill whenever the user asks to create a GitHub pull request. Triggers on phrases like "PR を作って", "プルリクを作成", "create a PR", "open a pull request", "PR 出して", or any request to open a pull request from the current branch. This skill collects the full diff, synthesizes a clean title and body, selects appropriate labels from the repository's existing labels, and creates the PR after confirmation. It is GitHub-PR-only — if the target is not a GitHub repository, this skill does not apply.
metadata:
  author: rinse <rinse418@gmail.com>
  license: MIT
  source: https://github.com/rinse/skills
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
7. ラベルの選定（内容に合うラベルを既存ラベルから選定）
8. ユーザーに内容を見せて確認を取る
9. PR を作成する
10. 後処理

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

`gh pr create` は対象ブランチが origin に無いと自動で push を試みます。確実を期して、先にこちらで push 状態を整えておきます。

**まず一度 `git push origin <branch>` を試します**（push 先は明示する）。既に push 済みなら no-op で済み、未反映のコミットがあればここで反映されます。

- **成功した場合** → 次へ進む。
- **失敗した場合**（認証・パスフレーズ入力が対話的に必要、権限が無い等）→ 無理に繰り返さず、その時点でユーザーに push を依頼する。失敗の内容を簡潔に伝え、実行してほしいコマンド（`git push origin <branch>`）を示す。ユーザー自身のシェルなら対話的な入力もできる。

push が済んだことを確認してから次へ進みます。

## 7. ラベルの選定

PR の内容（差分・コミット）に合った**適切なラベルを選定**して付与します。まずリポジトリのラベル一覧を取得します（名前だけでなく description も読む。各ラベルの用途は description から判断する）。

```
gh label list
```

手順:

1. 一覧から、PR の内容に合致するものを選ぶ。観点の例:
   - **種別**: `bug` / `enhancement` / `feature` / `documentation` / `refactor` など、変更の性質に合うもの。
   - **領域・コンポーネント**: `area/*` `component/*` のように対象範囲を表すラベルがあれば、関係するものを付ける。
   - **優先度**: リポジトリが `priority/*` 等で運用していて、内容から優先度が読み取れる場合のみ。読み取れないなら付けない。
2. **既存のラベルだけを使う。** リポジトリに無いラベルは指定しない（`gh pr create` が失敗する）。明らかに必要なラベルが存在しない場合は、勝手に作らず、その旨をユーザーに伝えて作成するか確認する。
3. **付けすぎない。** 内容を正確に表す最小限に絞る。確信を持って当てはまるものだけを選び、迷うものは外す。合致するラベルが無ければ無理に付けない。

選んだラベルは、理由が自明でなければ一言添えて、step 8 でユーザーに提示します。

## 8. 投稿内容の確認

PR の作成は**外向きの操作**で、リポジトリの関係者に通知され取り消しづらいので、作成前に必ずユーザーに内容を見せて了承を取ります。

提示する内容:

- タイトル
- 本文
- base（マージ先）と head（作成元ブランチ）
- **付けるラベル**（step 7 で選定したもの。ユーザーは追加・削除を指示できる）

ユーザーが了承したら次へ進みます。修正指示があれば反映してから再提示します。

## 9. PR の作成

本文はコマンドラインで直接渡すと壊れやすいので、ファイルに書き出して `--body-file` で渡します。
セッションで自由に読み書きできる一時ファイルがあればそれを使い、なければ標準の一時ファイルを使います。

```
gh pr create --base <base> --head <branch> --title "feat: ..." --body-file /tmp/pr-body.md --label "<label1>" --label "<label2>"
```

- draft は既定では作らない。ユーザーが「draft で」と明示した場合のみ `--draft` を付ける。
- step 7 で選び、確認の取れたラベルを `--label` で付ける。存在しないラベルを指定すると失敗するので、選定時に `gh label list` で実在を確認しておく。

## 10. 後処理

作成された PR の URL をユーザーに伝えます。一時的に作った本文ファイル（`pr-body.md` 等）は片付けます。

## フォールバック: GitHub MCP

`gh` が使えず GitHub MCP が利用できる環境では、GitHub MCP の PR 作成ツールで同じことを行います。その場合も「差分から本文を合成」「テンプレートがあれば従う」「push はまず試し、失敗したらユーザーに依頼」「作成前の確認」という方針は変わりません。ラベルの選定（step 7、内容に合うラベルを既存ラベルから選定）も、MCP のラベル系・PR 作成ツールで同様に行います。
