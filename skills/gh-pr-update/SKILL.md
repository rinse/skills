---
name: gh-pr-update
description: Use this skill whenever an existing GitHub PR's title, description, or labels may have drifted out of sync with what the PR actually changes — and bring them back up to date. Triggers after you address code-review feedback, when the user gives additional instructions or new requirements on an open PR, or any time a PR is modified (code or otherwise). Also triggers on phrases like "PR を修正して", "レビュー指摘を反映して", "PR の説明を更新して", "PR のタイトル/本文/ラベルを直して", "PR を最新にして", "update the PR description", "fix up this PR", "address the review comments". Whenever you change what a PR does, use this skill to re-synthesize the title, body, and labels from the current diff so the PR never describes stale work. It edits an existing GitHub PR via `gh pr edit` — it does not create PRs (use gh-pr-create) and does not merge them. It is GitHub-PR-only — if the target is not a GitHub PR, this skill does not apply.
metadata:
  author: rinse <rinse418@gmail.com>
  license: MIT
  source: https://github.com/rinse/skills
---

# GitHub PR Update

既存の GitHub Pull Request の **title・description・labels を、現在の変更内容と一致した状態に保つ**ためのスキルです。

PR は最初に作ったときの説明のまま放置されがちです。レビュー指摘を反映してコードを直したり、追加の要望を取り込んだりすると、**実際の差分と PR の説明がずれていきます**。このスキルは、その都度 PR のメタ情報を最新の差分から組み立て直し、ずれを解消します。

このスキルの核は、**古い本文に差分を継ぎ足すのではなく、いまの差分全体を読んで title・body・labels を合成し直す**ことです（合成主義）。「何が変わったか」を追記するのではなく、「いま PR が何を・なぜ変えるのか」を改めて記述します。

> **原則: PR のコードを直したら、本文も直す。** レビュー対応・追加実装・仕様変更などで PR の中身を変更したら、コードの修正だけで終わらせず、このスキルで title・body・labels を更新するところまでをワンセットにします。「コードは直したが説明は古いまま」を作らないことが目的です。

## 全体の流れ

1. ガードと前提確認
2. 対象 PR の特定
3. コンテキスト（現在のメタ情報・最新の差分・対応した指摘/指示）の収集
4. title・body・labels の再合成
5. ユーザーに変更内容を見せて確認を取る
6. PR の更新（`gh pr edit`）
7. 後処理

## 1. ガードと前提確認

- **`gh` コマンドが無い場合**（`command -v gh` で確認）→ このスキルは `gh` に依存する。未インストールならその旨を伝え、**インストールするかどうかユーザーに尋ねる**。希望する場合は実行環境（OS / パッケージマネージャ）に合った方法でインストールして続行する（公式は https://cli.github.com ）。希望しない場合はここで終了する。「`gh` が無い」ことと「GitHub PR でない」ことは別物なので混同しない。
- **そもそも GitHub PR が対象でない場合**（`gh` がリポジトリを認識しない／別ホストのリモート等）→ このスキルの対象外。その旨を伝えて終了する。

## 2. 対象 PR の特定

更新する PR を一つに絞ります。

- まず現在のブランチに紐づく PR を確認する（`gh pr view --json number,title,url`）。
- **現在ブランチに PR がある場合** → それを対象とする。
- **現在ブランチに PR が無い／複数候補がある／別の PR を指定された場合** → どの PR か（番号・URL・ブランチ）をユーザーに確認する。状況を取り違えて別の PR を書き換えないよう、曖昧なら黙って進めず尋ねる。

以降、対象 PR の番号を `<num>`、base ブランチを `<base>`、PR の作成元ブランチを `<branch>` とします。

## 3. コンテキストの収集

PR を正しく描き直すために、現在の状態と「何が変わったか・なぜ変わったか」を集めます。

### 現在の PR メタ情報

```
gh pr view <num> --json number,title,body,labels,baseRefName,headRefName,url
```

いまの title・body・labels を把握する（差し替え前の状態。確認ステップで before として見せる）。

### 最新の差分

PR が最終的に「何を変えるのか」を、**過程ではなく現在の到達点**として読みます。

- 対象ブランチをローカルにチェックアウトしている場合: `git -P diff <base>...HEAD` と `git --no-pager log <base>..HEAD`。
- そうでない場合: `gh pr diff <num>`（GitHub 上の PR ブランチの差分）。

**注意: 差分はコミット済みの内容しか見えない。** このスキルは「レビュー指摘を受けてコードを直した」直後に呼ばれることが多いが、その修正が**まだコミットされていない作業ツリーの変更**だと、`git diff <base>...HEAD` にも `gh pr diff` にも現れず、結果として**修正前の状態から本文を組み立ててしまう**（このスキルが防ぎたいズレそのもの）。合成に入る前に `git status` で未コミットの変更が無いか確認し、あれば**先にコミットしてから**差分を取り直す（コミット規約は `git-commit` に従う）。

`gh pr diff` は **origin に push 済みの内容**しか反映しません。ローカルに未 push のコミットがある場合、GitHub 側の差分は古いままです。ローカルの差分を正とみなして本文を書きつつ、**未 push がある旨を後述の確認・後処理でユーザーに伝えます**（push はこのスキルでは行わず、ユーザーに委譲する）。

### 対応した指摘・指示

このスキルがトリガーされた理由（レビュー指摘・追加要望・修正指示）を読み、**何が・なぜ変わったか**を理解します。必要なら PR のレビューコメントも参照する（`gh pr view <num> --comments` など）。これは body の「なぜ」を正確にするためで、コメントへの逐一の返信を本文に書き写すためではありません。

### 本文テンプレート

リポジトリに PR テンプレートがあれば body の構成はそれに合わせます。検出場所は `gh-pr-create` と同じ（`.github/PULL_REQUEST_TEMPLATE.md` ほか）。既存 body が既にテンプレート構成なら、その構成を保ったまま中身を更新します。

## 4. title・body・labels の再合成

集めた差分から、メタ情報を組み立て直します。**古い body に追記して辻褄を合わせるのではなく、現在の差分を説明する文章として書き直す**のが核です。

- **title**: 変更の目的・結果を端的に伝える一行。conventional-commit 風 prefix を付ける（既存の git/PR スキルと統一）。レビュー対応で当初の主目的が変わったなら title もそれに合わせて変える。
- **body**:
  - 現在の差分全体を反映する。レビュー対応や追加実装で増えた変更も織り込む。
  - **古くなった記述は消す。** もう存在しない変更点・「予定」のまま実体と食い違う記述を残さない。
  - テンプレートがあれば各セクションを実内容で埋める（プレースホルダや `<!-- -->` を残さない）。
  - 「過程」ではなく「最終的に何を・なぜ」。中間コミットの経緯や WIP の名残を持ち込まない。
- **labels**: 現在の内容に合うよう見直す（`gh-pr-create` のラベル選定と同じ方針）。
  - 内容に新たに合致するラベルがあれば**追加**、もう当てはまらないラベルは**削除**する。
  - 既存ラベルだけを使う。リポジトリに無いラベルは勝手に作らず、必要ならユーザーに確認する。付けすぎない。
  - 変更が無ければラベルはそのままでよい。

## 5. 変更内容の確認

PR の編集は**外向きの操作**で、関係者に見える形が変わるため、適用前にユーザーへ提示して了承を取ります。

**変更前 → 変更後**が分かる形で示します:

- title（変わる場合）
- body（要点の差分。大きく変わるなら全文）
- labels（追加するもの / 削除するもの）
- 未 push のローカルコミットがある場合は、その旨と「GitHub 側の差分は push 後に最新化される」ことも併せて伝える。

ユーザーが了承したら次へ。修正指示があれば反映して再提示します。

## 6. PR の更新

body はコマンドラインに直書きすると壊れやすいので、ファイルに書き出して `--body-file` で渡します。**一時ファイルは作業ツリーを汚さない場所に作ります** ── セッションで自由に読み書きできる一時ファイル（スクラッチ領域）があればそれを、なければ標準の一時ファイル（`/tmp`）を使います。

```
gh pr edit <num> \
  --title "fix: ..." \
  --body-file /tmp/pr-body.md \
  --add-label "<label>" \
  --remove-label "<label>"
```

- 変える項目だけ指定する。title を変えないなら `--title` を付けない。body を変えないなら `--body-file` を付けない。labels に増減が無ければ `--add-label` / `--remove-label` を付けない。
- `--add-label` / `--remove-label` は確認の取れたものだけ。存在しないラベルを指定すると失敗するので、`gh label list` で実在を確認しておく。

## 7. 後処理

- 更新後の PR の URL をユーザーに伝える。何を変えたか（title/body/labels）を一言添える。
- 一時的に作った本文ファイルは片付ける。
- **未 push のローカルコミットがある場合**は、コードの変更を GitHub に反映するための push をユーザーに依頼する（push 先は常に明示し、`origin <branch>` の形で。upstream 設定 `-u` は付けない）。SSH 鍵のパスフレーズ入力が必要な場合に `! ` 実行のサブシェルでは入力できないため、push はこのスキルでは行わない。

  案内:
  1. `Ctrl+Z` で Claude Code を一時停止する
  2. 自分のシェルで `git push origin <branch>` を実行する
  3. `fg` で Claude Code に戻ってくる

## フォールバック: GitHub MCP

`gh` が使えず GitHub MCP が利用できる環境では、GitHub MCP の PR 編集ツールで同じことを行います。その場合も「現在の差分から title・body・labels を**合成し直す**」「古い記述を残さない」「編集前の確認」「push はユーザーに委譲」という方針は変わりません。現在のメタ情報・差分の取得、ラベルの増減も MCP の対応ツールで行います。
