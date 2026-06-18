---
okf_version: "0.1"
---

# このリポジトリの knowledge bundle

`rinse/skills`（再利用可能な Agent 向け Skill のリポジトリ）について、**一度全体を読まないと見えてこない横断的な法則**と、**Agent Skills プラットフォームの仕様・ベストプラクティス**をまとめた knowledge です。

# このリポジトリのスキル設計の法則

リポジトリ内の全 SKILL.md を読み通して抽出した、スキル群に共通する規約・設計思想。新しいスキルを書く／既存スキルを直すときの拠り所。

* [スキル執筆の規約](this-repo/skill-authoring-conventions.md) - 言語・命名・frontmatter・ファイル構成の取り決め
* [スキル設計の思想](this-repo/skill-design-philosophy.md) - 「核」= 判断と機械作業の分離、合成主義、アクションスキルの共通骨格
* [外向き操作の安全則](this-repo/external-action-safety.md) - 取り消しづらい操作は実行前に確認、push はユーザーへ委譲、保守的な既定
* [ツール検出とフォールバック](this-repo/tool-gating-and-fallbacks.md) - 依存ツールの検出・導入提案・「未導入 ≠ 対象外」・MCP フォールバック
* [Subagent 委譲と worktree の制約](this-repo/subagent-and-worktree.md) - 高コスト/並列作業の委譲とオーケストレーターによる判断の保持

# Agent Skills（プラットフォーム）の仕様とベストプラクティス

Anthropic 公式の Agent Skills の仕組み。一次資料（platform docs / engineering blog）に基づく。

* [Skill フォーマットと段階的開示](agent-skills/skill-format-and-loading.md) - SKILL.md の構造・frontmatter の制限値・3 層のロード
* [スキル執筆のベストプラクティス](agent-skills/authoring-best-practices.md) - eval 駆動・スケール時の分割・code と reference の使い分け
* [ランタイムと配布](agent-skills/runtime-and-distribution.md) - Claude Code での配置・サーフェス間の非同期・実行環境の制約・セキュリティ
