---
type: Convention
title: スキル執筆の規約
description: 本リポジトリのスキルに共通する言語・命名・frontmatter・ファイル構成の取り決め。
tags: [skill-authoring, convention, frontmatter]
timestamp: 2026-11-24T00:00:00Z
---

リポジトリ内の全 SKILL.md に共通して観察される、書式上の取り決め。新しいスキルを足すときはこれに倣う。Agent Skills 自体の必須仕様（フィールドの制限値など）は [Skill フォーマットと段階的開示](/agent-skills/skill-format-and-loading.md) を参照。

# 言語の使い分け

- **`description`（frontmatter）は英語で書く。** 常時ロードされる第 1 階層なので、「何をするか」1 文と「いつ使うか」1 文に絞る。日英のトリガー語句は括弧で 2〜3 個添える程度にし、本文の要約・手順・仕組みは書かない（例: `Create a GitHub pull request from the current branch, synthesizing the title and body from the full diff. Use when asked to create or open a PR (PR を作って, create a PR). GitHub only.`）。YAML の plain scalar では `: ` が使えないので、コロンで区切らず文を分ける。
- **本文は日本語で書く。** 手順・判断基準・注意点を日本語で記述する。

# 命名

- `name` はディレクトリ名と一致させ、kebab-case（小文字・数字・ハイフン）にする。
- 機能を表す動詞句・名詞句（`gh-pr-create`, `git-init`, `git-bisect`, `concurrent-dev`）。`gh-*` は GitHub 連携スキルの接頭辞として機能している。

# frontmatter

- Agent Skills の必須フィールドは `name` と `description` の 2 つだが、本リポジトリで書き起こしたスキルは **`license: MIT` と `metadata.author` / `metadata.source`（リポジトリの URL）** も付ける。新しいスキルは既存スキルの frontmatter をそのまま写す。
- 外部の資料を元にしたスキルは `license` を付けず、`metadata.source` に出典を書く（`technical-writing-ja` は出典 gist の URL、`dads-ui-design` は出典に加えて `metadata.version` と `metadata.attribution`）。
- `playwright-cli-auth` は `allowed-tools: Bash(playwright-cli:*)` でツールを限定している。
- `description` は「何をするか」と「いつ使うか」の両方を含め、末尾に「GitHub only」「Does not fix」のような**適用範囲の限定**を一言添える。他のスキルと発火条件を重ねない（例: 「レビュー指摘に対応」で発火するのは gh-address-review だけで、gh-pr-create の更新はそこから呼ばれる）。広すぎる語（「ログインして」「レビューして」）を単独のトリガーにしない。

# ファイル構成

- 単純なスキルは `SKILL.md` 1 枚（`git-commit`, `git-bisect`, `external-action-safety` 系の gh スキル）。
- 大きなスキルは補助ファイルに分割し、SKILL.md から参照する。`okf-knowledge` が典型で、書式仕様を `references/okf-spec.md` に分け、SKILL.md 本文は判断に集中させている。稀にしか通らない経路（`git-init` の `references/install-git-profile.md`、`inspect-web-traffic` の `references/escalation.md`）も同様に分け、本文はいつ開くかだけを書く。これは Agent Skills の Level 3（段階的開示）にあたり、詳しくは [段階的開示](/agent-skills/skill-format-and-loading.md) と [ベストプラクティス](/agent-skills/authoring-best-practices.md) を参照。
- スキル間の参照はプレーンなスキル名の言及で行う。相対リンク（`../git-commit/SKILL.md` 等）はスキルが単体でインストールされると壊れるため使わない。スキルは互いに合成される単位として書かれている（[スキル設計の思想](/this-repo/skill-design-philosophy.md) 参照）。

# Gotcha

- **`name` とディレクトリ名は必ず一致させる。** 全スキルを読み比べないと気づきにくい不整合の温床。実例として `playwright-cli-auth/SKILL.md` は以前 `name: playwright-cli-signin` でディレクトリ名と食い違っていた（現在は修正済み）。新規・改修時は name とディレクトリ名の一致を確認すること。

# Citations

[1] リポジトリ内の全 SKILL.md（`skills/*/SKILL.md`）を読み比べて抽出。
[2] frontmatter フィールドの公式仕様: [Skill フォーマットと段階的開示](/agent-skills/skill-format-and-loading.md)
