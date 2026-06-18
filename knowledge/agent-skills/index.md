# Agent Skills（プラットフォーム）の仕様とベストプラクティス

Anthropic 公式の Agent Skills の仕組み。一次資料（platform docs / engineering blog）に基づく、本リポジトリのスキルが乗っているプラットフォーム側の知識。

* [Skill フォーマットと段階的開示](skill-format-and-loading.md) - SKILL.md の構造、frontmatter の必須/任意フィールドと制限値、3 層のロードモデル
* [スキル執筆のベストプラクティス](authoring-best-practices.md) - eval 駆動の開発、スケール時のファイル分割、code と reference の使い分け、description の質
* [ランタイムと配布](runtime-and-distribution.md) - Claude Code での配置パス、サーフェス間の非同期、実行環境の制約、セキュリティ
