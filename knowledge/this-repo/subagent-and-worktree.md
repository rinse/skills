---
type: Design Principle
title: Subagent 委譲と worktree の制約
description: トークン高コスト/並列の作業を安価なモデルの Subagent へ委譲しつつ判断はオーケストレーターが保持する設計と、worktree をプロジェクト直下に置く許可上の制約。
tags: [subagent, worktree, cost, orchestration]
timestamp: 2026-06-18T00:00:00Z
---

`concurrent-dev` と `gh-release` に共通する、Subagent の使い方と、その前提になるファイルアクセス許可の制約。

# 委譲するのは「機械作業」、判断は手元に残す

コストを食う／並列化できる作業だけを安価なモデルの Subagent に委譲し、**一貫性と最終判断はオーケストレーターが握り続ける**。これは [スキル設計の思想](/this-repo/skill-design-philosophy.md) の「核（判断）と機械作業の分離」を、モデル選択の次元で実装したもの。

- `gh-release`: トークンを食う**差分の読解だけ**を Haiku の Subagent に委譲し、**事実抽出に徹させる**（bump 種別やバージョンは決めさせない）。最終的なバージョン判断・ノート合成・タグ作成はオーケストレーターが、自分が読んだログと Subagent の報告を突き合わせて行う。
- `concurrent-dev`: **開発作業だけ**を難易度に応じて Sonnet / Opus の Subagent に委譲。準備（ブランチ・worktree 作成）・レビュー・マージ・後片付けはオーケストレーターが行う。「全タスクの差分を一人が読む」ことが並列開発で崩れがちな一貫性（重複実装・命名のずれ）を守る唯一の方法、と明言。

# モデルは難易度で割り当てる

`concurrent-dev` の指針: 仕様が明確で局所的な変更・既存パターン踏襲・定型作業は **Sonnet**、設計判断・複数モジュール横断・曖昧さの残るもの・厄介なデバッグは **Opus**。迷ったら Opus に倒す前に「Sonnet + 具体的な指示」を検討する。Subagent への指示は変更対象ファイル・倣うべき既存コード・受け入れ条件まで具体化する。

# worktree はプロジェクトルート直下（`.wt/`）に作る

これは見落としやすい**許可上の制約**。`concurrent-dev` は worktree を必ずプロジェクトルート直下の `.wt/` に作る。

- 理由: Claude Code のファイルアクセス・コマンド実行の許可は**プロジェクトディレクトリに対して**与えられている。その配下に worktree を置くことで Subagent が許可を引き継げる。
- やってはいけない: `/tmp` や Agent ツールの `isolation: "worktree"` が作るプロジェクト外の場所に作ること（許可が及ばず Subagent が作業できない）。
- 補足: `.wt/` は `.gitignore` ではなく `.git/info/exclude` に入れてリポジトリを汚さない。

この「プロジェクト外は許可が及ばない」という性質は Claude Code のランタイム特性に由来する（[ランタイムと配布](/agent-skills/runtime-and-distribution.md)）。

# Citations

[1] `skills/concurrent-dev/SKILL.md`, `skills/gh-release/SKILL.md` の本文。
