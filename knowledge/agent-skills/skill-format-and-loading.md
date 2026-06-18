---
type: Specification
title: Skill フォーマットと段階的開示
description: SKILL.md の構造、frontmatter の必須/任意フィールドと制限値、そして metadata/instructions/resources の3層からなる段階的開示（progressive disclosure）モデル。
resource: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
tags: [agent-skills, spec, frontmatter, progressive-disclosure]
timestamp: 2026-06-18T00:00:00Z
---

Agent Skills の最小仕様と、コンテキストを節約する核心の仕組み「段階的開示」。本リポジトリの執筆規約（[スキル執筆の規約](/this-repo/skill-authoring-conventions.md)）はこの仕様の上に乗っている。

# 構造

Skill = **ディレクトリ + その中の `SKILL.md`**。SKILL.md は YAML frontmatter で始まり、本文に手順を書く。補助ファイル（追加 markdown・スクリプト・参照資料）を同梱できる。

# frontmatter のフィールドと制限値

必須は **`name` と `description` の 2 つ**。

| フィールド | 必須 | 制限 |
|---|---|---|
| `name` | ✓ | 最大 64 文字。小文字・数字・ハイフンのみ。XML タグ不可。予約語 `anthropic` / `claude` を含めない |
| `description` | ✓ | 非空。最大 1024 文字。XML タグ不可。**「何をするか」と「いつ使うか」の両方**を含める |

`description` の質がトリガー精度を左右する（[ベストプラクティス](/agent-skills/authoring-best-practices.md)）。

# 段階的開示（progressive disclosure）── 3 層

Skill の内容は 3 種類あり、それぞれ**異なるタイミングでロード**される。これがコンテキストを食わずに多数のスキルを入れておける理由。

| Level | いつロードされるか | トークンコスト | 内容 |
|---|---|---|---|
| **1: メタデータ** | 常時（起動時、system prompt に注入） | 約 100 トークン/スキル | frontmatter の `name` と `description` |
| **2: 本文** | スキルがトリガーされたとき | 5k トークン未満が目安 | SKILL.md 本文の手順・指針 |
| **3: リソース** | 必要になったとき | 実質無制限 | 同梱ファイル。bash で読む／スクリプトは実行され**出力のみ**がコンテキストに入る |

要点:

- Level 1 が「第 1 階層の段階的開示」。Claude は全スキルの name/description だけを先読みし、関連すると判断したスキルの SKILL.md（Level 2）を bash で読み込む。
- **スクリプトのコード自体はコンテキストに入らない**。実行結果だけが入るため、ソート等の決定的処理はトークン生成より圧倒的に安い。
- 同梱ファイルは参照されるまで 0 トークン。だから大きな API リファレンスやデータも同梱できる（context penalty なし）。

## 本リポジトリでの実例

`quiver-diagram` がこの 3 層を体現している。SKILL.md（Level 2）から、`scripts/`（Python エンコーダ・`templates.py`）と `references/format-spec.md` / `references/style-reference.md`（Level 3）を必要時にだけ参照させる。SKILL.md 本文には「単純な図はインラインで、複雑な図はスクリプトを使え」という分岐を置き、深掘りが要る局面でのみ references を読ませる。詳細は [スキル執筆の規約](/this-repo/skill-authoring-conventions.md) と [ベストプラクティス](/agent-skills/authoring-best-practices.md)。

# Citations

[1] Agent Skills Overview（platform docs）: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
[2] Equipping agents for the real world with Agent Skills（engineering blog）: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
