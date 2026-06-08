---
name: gh-merge
description: Use this skill whenever the user asks to merge a GitHub pull request. Triggers on phrases like "PR をマージ", "squash merge", "squash and merge", "マージして", "merge this PR", "merge the branch", or any request to merge a GitHub PR. This skill is primarily for squash-merging a PR with a clean, concise commit message synthesized from the diff. It is GitHub-PR-only — if the target is not a GitHub PR, this skill does not apply.
---

# GitHub PR Merge

GitHub の Pull Request をマージするためのスキルです。主なユースケースは **squash merge** で、差分の全体を読んで**短く適切な squash commit メッセージを合成**し、確認を取ってからマージします。

**このスキルは GitHub の PR マージ専用です。** GitHub の PR でない場合（GitHub リポジトリでない、GitLab 等の別ホスト、ローカルブランチの `git merge` のみ等）は、このスキルの対象外なので何もしません。

`gh pr merge` をそのまま使うと、リポジトリの設定によっては中間コミットの雑なメッセージが連結されてしまいます。差分全体を読んで `--subject` を組み立てるのが、このスキルの核です。

## 全体の流れ

1. ガードと前提確認
2. 対象 PR を特定する
3. マージ方式の判定（squash を既定とする）
4. コンテキスト（差分・ログ）の収集
5. squash commit メッセージの生成
6. ユーザーに内容を見せて確認を取る
7. マージを実行する
8. 後処理

## 1. ガードと前提確認

- **そもそも GitHub リポジトリでない場合**（`gh` がリポジトリを認識しない／別ホストのリモート等）→ このスキルの対象外。その旨を伝えて終了する。

## 2. 対象 PR の特定

マージ対象の PR を確定させます。

- **PR 番号や URL が指定されている場合** → それを使う。
- **指定がない場合** → 現在のブランチに紐づく PR を `gh pr view` で探す。

```
gh pr view --json number,title,headRefName,baseRefName,url,mergeable,mergeStateStatus
```

結果によって分岐します。

- **PR が見つかった場合** → その PR を対象にする。番号を控えておく（以降 `<PR番号>`）。
- **GitHub リポジトリだが現在のブランチに PR がない場合** → 黙って止まらず、どの PR をマージするかユーザーに尋ねる（番号 / URL）。「PR が見つからない」ことと「GitHub でない」ことは別物。
- **そもそも GitHub リポジトリでない場合** → このスキルの対象外。その旨を伝えて終了する。

マージ可能な状態か（`mergeable` / `mergeStateStatus`）も確認します。コンフリクトやチェック未通過でマージできない場合は、その旨をユーザーに伝えます。

## 3. マージ方式の判定

既定は **squash merge** です。ユーザーが merge commit / rebase を明示した場合のみそれに従います。

- **squash（既定）** → 4〜5 でメッセージを合成し、`--squash --subject ... --body ""` でマージする。
- **merge commit** → メッセージは GitHub のデフォルトのまま。`--merge` でマージする（メッセージを合成しない）。
- **rebase** → コミットメッセージの合成は不要。`--rebase` でマージする。

以降は主目的である squash の手順を説明します。

## 4. コンテキストの収集

squash commit メッセージを「最終的な変更内容」から組み立てるため、変更の全体を読みます。

```
gh pr diff <PR番号>
gh pr view <PR番号> --json title,body,commits
```

差分とコミットログの両方から、PR が「なぜ・何を」変えるのかを把握します。

## 5. squash commit メッセージの生成

squash merge では複数のコミットが一つにまとまるため、メッセージは**最終的な変更内容のみ**を反映したものにします。修正やレビューの過程（"fix typo", "address review comments", "WIP" など）は含めません。

- 変更の目的・結果を端的に伝える一行の `--subject`
- conventional-commit 風の prefix を付ける（既存の git スキルと統一）
- `--body` は既定で空にし、不要な過程のコミットメッセージが混ざらないようにする

**例:**

- `feat: add CSV export to dashboard`
- `fix: resolve null pointer in user authentication`
- `refactor: simplify database connection pooling`

本文を残したい明確な理由がある場合（破壊的変更の注意書き等）のみ `--body` に内容を入れます。

## 6. マージ内容の確認

マージは**外向きで取り消しづらい操作**（ブランチが取り込まれ、PR がクローズされ、関係者に通知される）なので、実行前に必ずユーザーに内容を見せて了承を取ります。

提示する内容:

- 対象 PR（番号・タイトル）
- マージ方式（squash / merge / rebase）
- squash の場合: 生成した `--subject`（と、あれば `--body`）

ユーザーが了承したら次へ進みます。修正指示があれば反映してから再提示します。

## 7. マージの実行

squash の場合、`--subject` (`-t`) と `--body` (`-b`) で明示的に上書きします。これによりリポジトリ設定に依存せず、確実にクリーンなメッセージになります。

```
gh pr merge <PR番号> --squash --subject "feat: add CSV export to dashboard" --body ""
```

- `--subject`: squash commit のタイトル（一行）
- `--body ""`: 不要な過程のコミットメッセージを含めないよう空にする

merge commit / rebase の場合はメッセージを上書きしません。

```
gh pr merge <PR番号> --merge
gh pr merge <PR番号> --rebase
```

ブランチの削除（`--delete-branch`）はユーザーが希望した場合のみ付けます。既定では付けません。

## 8. 後処理

マージ後、結果（マージされたこと、必要なら最終的なコミットメッセージ）をユーザーに伝えます。

## フォールバック: GitHub MCP

`gh` が使えず GitHub MCP が利用できる環境では、GitHub MCP の PR マージツールで同じことを行います。その場合も「差分から squash メッセージを合成」「過程のコミットメッセージを含めない」「実行前の確認」という方針は変わりません。
