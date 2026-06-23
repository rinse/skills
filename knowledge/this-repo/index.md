# このリポジトリのスキル設計の法則

`skills/` 配下の全 SKILL.md を読み通して見えてくる、スキル群に共通する規約と設計思想。個々のスキルの説明（[README](../../README.md) にある）ではなく、**全体に通底するパターン**を扱う。

* [スキル執筆の規約](skill-authoring-conventions.md) - 言語（本文 JA / description EN）・命名・frontmatter・ファイル構成
* [スキル設計の思想](skill-design-philosophy.md) - 「核」の明示、合成主義、アクションスキルの共通骨格、スキル間の合成
* [外向き操作の安全則](external-action-safety.md) - 取り消しづらい操作は実行前に確認、push はまず試し失敗時に委譲、保守的な既定、git 規律
* [ツール検出とフォールバック](tool-gating-and-fallbacks.md) - 依存ツールの検出・導入提案・「未導入 ≠ 対象外」・GitHub MCP フォールバック・body-file 技法
* [Subagent 委譲と worktree の制約](subagent-and-worktree.md) - 高コスト/並列作業を安価なモデルへ委譲し、判断はオーケストレーターが保持
