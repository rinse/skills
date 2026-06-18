---
type: Convention
title: ツール検出とフォールバック
description: 依存ツールを検出し、未導入なら導入を提案し、「未導入」と「対象外」を区別し、GitHub MCP へフォールバックする本リポジトリ共通の前提処理。
tags: [tooling, github, mcp, guards]
timestamp: 2026-06-18T00:00:00Z
---

外部ツール（主に `gh`、`git-profile`）に依存するスキルが共通して持つ、前提確認とフォールバックの作法。

# 依存ツールはまず検出する

スキル冒頭のガードで `command -v <tool>` により存在を確認する（`gh`, `git-profile` など）。

# 未導入なら「導入するか」を尋ねる ── 黙って失敗しない

依存ツールが無い場合、エラーで止めず**インストールするかをユーザーに尋ねる**。希望すれば実行環境（OS / パッケージマネージャ）に合った方法で導入して続行、希望しなければその操作を見送る。

- `gh` 系スキル: 公式 https://cli.github.com を案内して導入を提案。
- `git-init`: `git-profile`（`rinse/git-profile-rs`）を GitHub Releases から導入。アセット名は固定で仮定せず、`gh release view` の一覧から実環境（`uname -sm`）に合うものを**自分で選ぶ**。

# 「未導入 ≠ 対象外」を混同しない

これは複数の gh スキルが**明示的に警告している**重要な区別。

- 「`gh` が無い」＝ 依存ツールが未導入 → 導入を提案する。
- 「GitHub リポジトリでない」＝ そもそもこのスキルの**適用範囲外**（別ホストのリモート、リモート未設定、ローカル変更のみ等）→ 何もせず対象外と伝えて終了する。

`gh-merge` / `gh-review` ではさらに「GitHub リポジトリだが現在ブランチに PR が無い」場合も区別し、黙って止まらず**どの PR か尋ねる**。状況の取り違えで誤動作しないよう、状態を細かく場合分けするのが法則。

# GitHub MCP へのフォールバック

`gh` が使えず GitHub MCP が利用できる環境では、MCP の対応ツールで同じことを行う。全 gh スキルの末尾に「フォールバック: GitHub MCP」節があり、**方針（合成・確認・push 委譲など）は MCP でも変えない**と明記している。Claude Code はネットワーク・コマンド実行が可能な環境であることが前提（[ランタイムと配布](/agent-skills/runtime-and-distribution.md)）。

# 壊れやすいペイロードはファイル経由で渡す

コメントや本文など複雑な文字列をコマンドラインに直書きするとシェルのエスケープで壊れる。**ファイルに書き出して渡し、後で片付ける**のが共通手法。

- `gh-issue-create` / `gh-pr-create`: `--body-file`
- `gh-review`: JSON を作って `--input`
- `gh-release`: `--notes-file`

# テンプレートは検出 → フォールバック

`gh-pr-create` / `gh-issue-create` はリポジトリの PR/Issue テンプレートを所定パスで探し、あればそれを埋め、なければ自前のフォールバックテンプレートを使う。プレースホルダ（空欄・`<!-- -->`）は残さず実内容に置換する。

# Citations

[1] `skills/gh-pr-create/SKILL.md`, `skills/gh-issue-create/SKILL.md`, `skills/gh-review/SKILL.md`, `skills/gh-merge/SKILL.md`, `skills/gh-release/SKILL.md`, `skills/gh-init/SKILL.md`, `skills/git-init/SKILL.md` の本文。
