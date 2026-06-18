---
type: Reference
title: ランタイムと配布
description: Agent Skills の動作環境と配布。Claude Code での配置パス、サーフェス間の非同期、API/claude.ai の実行制約、セキュリティ上の注意。
resource: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
tags: [agent-skills, runtime, claude-code, distribution, security]
timestamp: 2026-06-18T00:00:00Z
---

スキルがどこに置かれ、どんな実行環境で動くか。本リポジトリは Claude Code 向けのファイルベースのスキル集なので、特に Claude Code の項が効く。

# Claude Code での配置

- **ファイルベース**。API アップロード不要。Claude がディレクトリを自動検出して使う。
- 配置パス:
  - **個人用**: `~/.claude/skills/`
  - **プロジェクト用**: `.claude/skills/`
  - Claude Code Plugins 経由でも共有可能。
- このリポジトリは `skills/` を**オーサリング元**とし、`gh skill install` 等で上記の有効パスへ導入する運用（README 参照）。`skills/` に置いただけではセッションでアクティブにならない点に注意。

# サーフェス間で同期しない

custom skill は **claude.ai / Claude API / Claude Code の間で自動同期されない**。それぞれに別々に導入・管理する必要がある。共有スコープも異なる（claude.ai はユーザー個人、API はワークスペース全体、Claude Code は個人 or プロジェクト）。

# 実行環境の制約（サーフェス別）

| サーフェス | ネットワーク | パッケージ |
|---|---|---|
| **Claude Code** | フル（ユーザーのマシンと同等） | グローバル導入は避け、ローカルに導入 |
| **Claude API** | なし（外部 API 不可） | 実行時インストール不可。プリインストール済みのみ |
| **claude.ai** | 設定により full/partial/none | ― |

- Claude API でスキルを使うにはコード実行コンテナ + 3 つの beta ヘッダ（`code-execution-2025-08-25`, `skills-2025-10-02`, `files-api-2025-04-14`）が要る。
- このリポジトリのスキルは `gh` や `playwright-cli` などローカルツールに依存する。これらは**ネットワーク・コマンド実行が可能な Claude Code 前提**であり、ネットワーク不可の API サーフェスではそのままは動かない。本リポジトリの [ツール検出とフォールバック](/this-repo/tool-gating-and-fallbacks.md) や [worktree の許可制約](/this-repo/subagent-and-worktree.md) は、この Claude Code のランタイム特性（プロジェクトディレクトリにスコープされた許可・フルネットワーク）を踏まえている。

# セキュリティ

- **信頼できる出所のスキルだけ使う**（自作 or Anthropic 提供）。悪意あるスキルは、表向きの目的と異なる形でツールを呼び出し・コード実行させ得る。
- 同梱物（SKILL.md・スクリプト・画像・リソース）を**監査**する。特に**外部 URL を取得するスキルは要注意**（取得内容に悪意ある指示が混入し得る）。
- ソフトウェアのインストールと同等の警戒で扱う。

# Citations

[1] Agent Skills Overview（platform docs, How Skills work / Where Skills work / Security / Limitations）: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
[2] Use Skills in Claude Code: https://code.claude.com/docs/en/skills
