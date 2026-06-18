---
type: Convention
title: スキル執筆の規約
description: 本リポジトリのスキルに共通する言語・命名・frontmatter・ファイル構成の取り決め。
tags: [skill-authoring, convention, frontmatter]
timestamp: 2026-06-18T00:00:00Z
---

リポジトリ内の全 SKILL.md に共通して観察される、書式上の取り決め。新しいスキルを足すときはこれに倣う。Agent Skills 自体の必須仕様（フィールドの制限値など）は [Skill フォーマットと段階的開示](/agent-skills/skill-format-and-loading.md) を参照。

# 言語の使い分け

- **`description`（frontmatter）は英語で書く。** トリガー判定に使われる第 1 階層であり、日本語・英語の両方のトリガー語句を列挙する（例: `Triggers on phrases like "PR を作って", "create a PR", ...`）。
- **本文は日本語で書く。** 手順・判断基準・注意点を日本語で記述する。
- 例外: `quiver-diagram` は本文も英語。対象ドメイン（圏論の作図、KaTeX/LaTeX ラベル）が英語前提のため。一貫性より読み手の自然さを優先した判断と読める。

# 命名

- `name` はディレクトリ名と一致させ、kebab-case（小文字・数字・ハイフン）にする。
- 機能を表す動詞句・名詞句（`gh-pr-create`, `git-init`, `tdd`, `concurrent-dev`）。`gh-*` は GitHub 連携スキルの接頭辞として機能している。

# frontmatter

- ほとんどのスキルは **`name` と `description` のみ**（Agent Skills の必須 2 フィールド）。
- 拡張フィールドを使う例:
  - `technical-writing-ja`: `metadata.source` に出典 gist の URL。
  - `playwright-cli-auth`: `allowed-tools: Bash(playwright-cli:*)` でツールを限定。
- `description` は「何をするか」と「いつ使うか（トリガー）」の両方を必ず含める。多くは末尾に「これは GitHub の PR 専用」のような**適用範囲の限定**まで書いている。

# ファイル構成

- 単純なスキルは `SKILL.md` 1 枚（`git-commit`, `tdd`, `external-action-safety` 系の gh スキル）。
- 大きなスキルは補助ファイルに分割し、SKILL.md から参照する。`quiver-diagram` が典型で、`scripts/`（Python エンコーダ・テンプレート）と `references/`（`format-spec.md`, `style-reference.md`）を持つ。これは Agent Skills の Level 3（段階的開示）の実例であり、詳しくは [段階的開示](/agent-skills/skill-format-and-loading.md) と [ベストプラクティス](/agent-skills/authoring-best-practices.md) を参照。
- スキル間は相対リンクで参照し合う（例: `concurrent-dev` の本文から `../git-commit/SKILL.md`）。スキルは互いに合成される単位として書かれている（[スキル設計の思想](/this-repo/skill-design-philosophy.md) 参照）。

# Gotcha

- **`name` とディレクトリ名は必ず一致させる。** 全スキルを読み比べないと気づきにくい不整合の温床。実例として `playwright-cli-auth/SKILL.md` は以前 `name: playwright-cli-signin` でディレクトリ名と食い違っていた（現在は修正済み）。新規・改修時は name とディレクトリ名の一致を確認すること。

# Citations

[1] リポジトリ内の全 SKILL.md（`skills/*/SKILL.md`）を読み比べて抽出。
[2] frontmatter フィールドの公式仕様: [Skill フォーマットと段階的開示](/agent-skills/skill-format-and-loading.md)
