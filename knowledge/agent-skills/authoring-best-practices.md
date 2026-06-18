---
type: Best Practices
title: スキル執筆のベストプラクティス
description: Agent Skills 公式が示す、eval 駆動の開発・スケール時のファイル分割・code と reference の使い分け・description の質・実使用の観測といった執筆指針。
resource: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
tags: [agent-skills, best-practices, authoring]
timestamp: 2026-06-18T00:00:00Z
---

Anthropic 公式が示すスキル執筆の指針。本リポジトリの [スキル設計の思想](/this-repo/skill-design-philosophy.md) はこれらを具体化したものとして読める。

# eval 駆動で作る

representative なタスクで Agent を走らせ、**詰まる／文脈が足りない箇所を観察**して capability gap を特定し、それを埋めるように**少しずつ**スキルを足す。最初から完璧を狙わない。

# スケールに合わせて分割する

SKILL.md が肥大化したら、**内容を別ファイルに分けて参照させる**。互いに排他的・併用されにくい文脈はパスを分けて持つと、不要なトークンを読まずに済む。これは段階的開示の Level 3 を活かす書き方（[フォーマットと段階的開示](/agent-skills/skill-format-and-loading.md)）。

本リポジトリでは `quiver-diagram` が `scripts/` と `references/` に分割している好例。逆に単純なスキルは SKILL.md 1 枚に保たれている。

# code と reference を区別する

コードは「実行するもの」と「読んで参照するもの」の両義になりうる。**どちらなのかを明示**する。決定的な処理は実行（run）させる方が、トークン生成で同等処理をやらせるより安く確実（例: ソートはアルゴリズムを走らせる）。

# description の質がトリガーを決める

`name` と `description` は段階的開示の第 1 階層で、**いつ使うか**の判断材料になる。description には「何をするか」と「いつ使うか」を両方書く。本リポジトリは日英のトリガー語句を列挙し、適用範囲の限定（「GitHub の PR 専用」等）まで書き込んでトリガー精度を上げている。

# 実使用を観測して反復する

実際の使われ方を監視し、想定外の経路や特定文脈への過依存に注意して反復改善する。Claude 自身に「うまくいった手順・よくある失敗」を再利用可能な context / code としてスキルに書き留めさせる、というやり方も推奨される。

# Citations

[1] Equipping agents for the real world with Agent Skills（engineering blog）: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
[2] Agent Skills Overview / Best practices（platform docs）: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
