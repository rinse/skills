---
name: create-issue
description: Create a structured issue from a rough description. Use when asked to file or open an issue (Issue を作って, 課題を起票, create an issue).
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# Create Issue

雑な思いつきや要望から構造化された Issue を組み立て、確認のうえ起票するスキルです。タイトルと本文をきれいに組み立てるのが核です。

## 起票先

- GitHub なら `gh`（無ければ導入を提案する。GitHub MCP があればそれで代替してよい）。
- GitHub 以外のホストなら相当するコマンド。分からなければ尋ねる。
- リモートが無い、または `gh` を入れない場合は、リポジトリの Issue 置き場（`issues/`、無ければ `docs/issues/`。どちらも無ければ `issues/` を作る）に `<4 桁の連番>-<slug>.md` として書く。この場合ラベルは付けず、状態は次の frontmatter で表す。

```markdown
---
status: draft
priority: medium
---

# <タイトル>
```

- `status`: `draft`（起票しただけ）、`ready`（着手してよい）、`in-progress`、`done`、`blocked`（人間の判断待ち）。起票時は `draft`。`in-progress` 以降は loop-dev スキルが書き換える。
- `priority`: `high` / `medium` / `low`。判断材料が無ければ書かない。

## 着手可能の印（ready）

loop-dev スキルは、ローカルなら `status: ready`、GitHub なら `ready` ラベルの付いた Issue だけを実装する。`ready` を付けるのは、ユーザーが「すぐ着手してよい」と明示したときだけ。受け入れ条件が書けていない Issue には付けない。

loop-dev スキルから呼ばれた場合（新しい Issue の起票）は、`ready` を付けず、質問と作成前の確認を省く。本文を組み立てられないほど曖昧なものは起票しない。

## 本文の合成

記述から意図を読み取り、曖昧で本文を組み立てられない点だけを一つ二つ尋ねる。関連コードがあれば軽く確認し、制約や受け入れ条件を具体的にする。

Issue テンプレート（`ISSUE_TEMPLATE.md`、`.github/ISSUE_TEMPLATE/`、`.github/ISSUE_TEMPLATE.md`、`docs/ISSUE_TEMPLATE.md`）があれば、各セクションを実内容で埋める（プレースホルダやコメントを残さない）。複数あれば内容に最も合うものを選ぶ。YAML フォームなら各フィールドの趣旨に沿って本文を構成する。

無ければ次の構成で書く。

```markdown
## 概要
(3 行程度。コンセプトが伝わる文章にする)

## 目的
(箇条書き。一項目に収まるのが理想)

## 制約
(実装上の制約、ユーザーの指示、避けるべき点)

## 受け入れ条件
(箇条書き。すべて確認できたら即マージできる性質のもの)
```

- 目的が複数行に膨らむなら、Issue の分割か Epic 化を提案する。
- 受け入れ条件は可能な限り自動テストにできる形で書く（Unit > 統合 > E2E）。人手のレビューが要る条件はそのまま条件として明記する。

## タイトルとラベル

- タイトルは主題を端的に一行で。バグなら現象、要望なら達成したいこと。リポジトリの慣習に prefix があれば合わせる。
- ラベルは `gh label list` の既存ラベル（description も読む）から、内容に確信を持てるものだけを選ぶ。無いラベルは作らない。付けすぎない。

## 確認と作成

Issue 作成はウォッチャーに通知される取り消しづらい操作なので、タイトル・本文・ラベルを提示して了承を得てから作成する。担当者・マイルストーンはユーザーが希望したときだけ。本文はファイルに書いて `--body-file` で渡す。

```
gh issue create --title "..." --body-file <path> --label "<label>"
```

作成した Issue の URL（またはファイルパス）を報告する。
