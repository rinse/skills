---
type: Convention
title: 外向き操作の安全則
description: 取り消しづらい外向き操作は実行前に確認し、push はまず試して失敗時にユーザーへ委譲し、既定は保守的に倒す本リポジトリ共通の安全規約。
tags: [safety, github, git, confirmation]
timestamp: 2026-06-23T00:00:00Z
---

外部に作用する操作（PR・Issue・レビュー・マージ・リリース・タグ）を扱うスキルに共通する安全側の取り決め。「うっかり外に出す」事故を防ぐための法則。

# 実行前に必ず確認を取る

外向きで取り消しづらい操作（関係者に通知される・公開される）は、**実行前にユーザーへ内容を提示して了承を取る**。`gh-pr-create` / `gh-issue-create` / `gh-review` / `gh-merge` / `gh-release` すべてに「ユーザーに内容を見せて確認を取る」ステップがある。修正指示があれば反映して再提示する。

# push はまず試し、失敗したら委譲する

push と、push を誘発する操作は、**まず一度試す**（`git push origin <branch>`）。成功すればそのまま進む。失敗した場合（認証・パスフレーズ入力が対話的に必要、権限が無い等）は、無理に繰り返さず、その時点で**ユーザーに push を依頼する**。`gh-init` / `gh-pr-create` / `gh-release` / `gh-pr-update` に共通。

依頼するときは、失敗の内容を簡潔に伝え、実行してほしいコマンド（`git push origin <branch>`）を示す。ユーザー自身のシェルなら、エージェントの実行環境では入れられない対話的入力（SSH 鍵のパスフレーズ等）もできる。

なお「必ず委譲する」「`-u` を付けない／upstream を明示する」といった運用は利用者ごとの好みであり、本スキル群には埋め込まない（利用者固有の preference は各自の Memory 等で管理する）。

# 既定は保守的に倒す

ユーザーが明示しない限り、強い副作用のあるオプションは付けない。スキルが先回りで決めない。

- `gh-review`: `event` は `COMMENT` を既定にし、`[対応必須]` があっても勝手に `REQUEST_CHANGES` に上げない。「PR をブロックするかはユーザーの判断」。
- `gh-merge`: ブランチ削除（`--delete-branch`）は希望時のみ。
- `gh-pr-create`: `--draft` は明示時のみ。
- `gh-pr-create` / `gh-issue-create`: 担当者・マイルストーンは希望時のみ。ラベルは内容（差分／課題）に合うものを既存ラベルから**自動選定**するが、付けすぎず、**存在しないラベルは勝手に作らずユーザーに確認**する（AI 作成を示すラベルのような運用ラベルも、適合すればこの選定で付く）。
- `gh-review` の severity タグも乱発しない（`[対応必須]` の多用は著者の負担）。

# git の規律

- **コミットメッセージは単一行**、conventional-commit 風 prefix（`feat:` / `fix:` / `refactor:` ...）で統一。
- **`git add -A` は禁止**。対象ファイルを明示列挙する（`git add -u` は可）。`git-commit` の規約で、`concurrent-dev` の Subagent 指示にも引き継がれる。
- default ブランチ上で作業を始めるときはブランチを切ってから。

これらは [スキル設計の思想](/this-repo/skill-design-philosophy.md) の「合成主義」「アクションスキルの共通骨格」の確認・後処理ステップに対応する。

# Citations

[1] `skills/gh-pr-create/SKILL.md`, `skills/gh-issue-create/SKILL.md`, `skills/gh-review/SKILL.md`, `skills/gh-merge/SKILL.md`, `skills/gh-release/SKILL.md`, `skills/gh-init/SKILL.md`, `skills/git-commit/SKILL.md` の本文。
