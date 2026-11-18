---
type: Best Practices
title: スキル執筆のベストプラクティス
description: Agent Skills 公式が示す、eval 駆動の開発（文脈を共有しない試行）・規則への理由の添付・スケール時のファイル分割・code と reference の使い分け・description の質・実使用の観測といった執筆指針。
resource: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
tags: [agent-skills, best-practices, authoring]
timestamp: 2026-11-19T00:00:00Z
---

Anthropic 公式が示すスキル執筆の指針。本リポジトリの [スキル設計の思想](/this-repo/skill-design-philosophy.md) はこれらを具体化したものとして読める。

# eval 駆動で作る

representative なタスクで Agent を走らせ、**詰まる／文脈が足りない箇所を観察**して capability gap を特定し、それを埋めるように**少しずつ**スキルを足す。最初から完璧を狙わない。

試行は、スキルを書いた本人ではなく**文脈を共有しない Subagent** に、スキルのパスを渡して実行させる。
書いた本人が試すと、本文に書いていない前提を会話から補ってしまい、欠けている記述が見えない。
結果だけでなくトランスクリプトも読む。
詰まった箇所や推測で埋めた箇所は本文に足し、無駄な作業を生んだ記述は削り、複数の試行が同じ補助スクリプトを書いていたら `scripts/` に同梱する。
スキル無し（改修なら旧版）でも同じ依頼を走らせ、スキルが差を生んでいるかを比べる。

# スケールに合わせて分割する

SKILL.md が肥大化したら、**内容を別ファイルに分けて参照させる**。互いに排他的・併用されにくい文脈はパスを分けて持つと、不要なトークンを読まずに済む。これは段階的開示の Level 3 を活かす書き方（[フォーマットと段階的開示](/agent-skills/skill-format-and-loading.md)）。

本リポジトリでは `okf-knowledge` が書式仕様を `references/okf-spec.md` に分けている好例。逆に単純なスキルは SKILL.md 1 枚に保たれている。

# code と reference を区別する

コードは「実行するもの」と「読んで参照するもの」の両義になりうる。**どちらなのかを明示**する。決定的な処理は実行（run）させる方が、トークン生成で同等処理をやらせるより安く確実（例: ソートはアルゴリズムを走らせる）。

# description の質がトリガーを決める

`name` と `description` は段階的開示の第 1 階層で、**いつ使うか**の判断材料になる。description には「何をするか」と「いつ使うか」を両方書くが、**それ以上は書かない**。スキルが増えるとハーネスは description を切り詰めて表示するため、長い description は自分の発火条件を見えなくする。また「データベースに触るとき」のような広い条件は、無関係なタスクにまでスキルを読み込ませる。本リポジトリでは 1〜2 文 + 日英トリガー語句 2〜3 個 + 適用範囲の限定（「GitHub only」等）に収める（[スキル執筆の規約](/this-repo/skill-authoring-conventions.md)）。

# 手順書より判断を書く

モデルが賢くなるほど、細かい手順（itinerary / recipe）は助けにならず、かえって判断を狭める。スキルには「どこに判断があるか」「何を守るか」を書き、ツールの導入方法や失敗時のリトライのような定型はモデルに任せる。完了条件（どこまでやって止まるか）は明示する。

# 規則には理由を添える

守らせたい規則には理由を添える。
理由があれば、モデルは規則が想定していない場面にも趣旨を当てはめられる。
理由のない「必ず」「絶対に」の重ね書きは、規則の字面に合う場面でしか効かない。
本リポジトリでも、`git-commit` は `git add -A` の禁止に「意図しないファイルを巻き込む恐れがあるため」と理由を添えている。
同じ理由で、例は試行に使った依頼に過適合させず一般化して書く。

# 実使用を観測して反復する

実際の使われ方を監視し、想定外の経路や特定文脈への過依存に注意して反復改善する。Claude 自身に「うまくいった手順・よくある失敗」を再利用可能な context / code としてスキルに書き留めさせる、というやり方も推奨される。

# Citations

[1] Equipping agents for the real world with Agent Skills（engineering blog）: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
[2] Agent Skills Overview / Best practices（platform docs）: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
[3] Rethinking skills and prompts for GPT-6 Astra（OpenAI developers blog、description の長さ・段階的開示・手順書の弊害・完了条件について）: https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
[4] anthropics/skills の skill-creator（試行と改善のループ、理由を添える書き方）: https://github.com/anthropics/skills/tree/main/skills/skill-creator
