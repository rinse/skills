---
name: skill-creator
description: Write or revise an Agent Skill to this collection's conventions, putting the skill's core judgment first. Use when asked to create or improve a skill in this style (スキルを作って, スキルを直して, create a skill). Does not run benchmark evals.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# Skill Creator

Agent Skill を新しく書く、または既存のスキルを直すためのスキルです。
核は、書こうとしているスキルにしかない判断（機械的なコマンドでは埋められない部分）を見つけ、本文をその判断に使うことです。
書式の規約は機械的に守れば済むので、思考はそこに使いません。

## 先に読むもの

対象リポジトリに独自の規約があれば、それが本スキルの既定より優先します。
規約を書いた文書や knowledge bundle（`AGENTS.md` や `knowledge/` など）と、既存の SKILL.md を数本読み、食い違うところはリポジトリ側に合わせる。
既存スキルを直す場合は、そのスキル全体と、それを呼ぶスキルや呼ばれるスキルも読む。

## スキルにする価値があるか

書き始める前に、そのスキルの核を一文で言えるか確かめる。
例えば PR を作るスキルの核は「中間コミットのメッセージを流用せず、差分全体からタイトルと本文を合成すること」、リリースを切るスキルの核は「bump 種別の判断とノートの合成」と言える。
核を言えないなら、スクリプトかエイリアスで足りる。

- 既存の CLI を決まった順に繋ぐだけの処理は、LLM の判断を要しないのでスクリプトにする。
- コマンド一行と大差ない処理をスキルにしても、発火時に読むトークンが増えるだけになる。
- 既存スキルと役割や発火条件が重なるなら、新設せずに既存スキルを直すか、既存スキルへ処理を引き渡す形にする。

## description

description は全スキル分が常時ロードされる（段階的開示の Level 1）ので、短く保つ。
スキルが増えるとハーネスは description を切り詰めて表示するため、長い description は自分の発火条件を見えなくする。

- 英語で書く。「何をするか」1 文と「いつ使うか」1 文に絞る。
- 日英のトリガー語句を括弧で 2〜3 個添える。
- 末尾に適用範囲の限定を一言添える（`GitHub only.`、`Does not fix.` など）。
- 本文の要約、手順、仕組みは書かない。
- 他のスキルと発火条件を重ねない。「レビューして」「ログインして」のような広い語を単独のトリガーにしない。
- YAML の plain scalar では `: ` が使えないので、コロンで区切らず文を分ける。
- name と合わせて 100 トークン（400 文字）程度に収める。

```
description: Create a GitHub pull request from the current branch, synthesizing the title and body from the full diff. Use when asked to create or open a PR (PR を作って, create a PR). GitHub only.
```

## frontmatter と命名

仕様上の制約は次のとおり。

- **name**：最大 64 文字で、小文字と数字とハイフンのみ。ディレクトリ名と一致させる。`anthropic` と `claude` を含めない。
- **description**：空にしない。最大 1024 文字で、XML タグを含めない。

name とディレクトリ名の食い違いは、全スキルを読み比べないと気づきにくい。
name は機能を表す動詞句か名詞句にし、リポジトリの接頭辞の慣習（GitHub 連携なら `gh-` など）に合わせる。
`license` や `metadata` などその他のフィールドは、隣のスキルの形をそのまま写す。
ツールを限定したいときだけ `allowed-tools` を足す。

## 本文

本文はリポジトリの規約の言語で書き、規約が無ければ日本語にする。
日本語で書くときは、technical-writing-ja が利用可能なら先に呼び出してその規範を適用する。

- 冒頭で核を一文で宣言する。実行するエージェントが、どこに思考を集中すべきかを最初に知るため。
- 手順書より判断を書く。モデルは細かいレシピが無くても進められ、レシピはかえって判断を狭める。書くのは「どこに判断があるか」「何を守るか」と、どこまでやって止まるかという完了条件。
- 入力をそのまま流用せず、全体を読んで出力を組み立て直すよう書く。
- 定型は一行で済ませる。依存ツールが無いときの導入提案、GitHub MCP での代替、push 失敗時の委譲、一時ファイルの置き場所は、モデルとハーネスが扱えるので手順を書かない。
- 一枚岩にせず、既存スキルに処理を引き渡す（コミットは git-commit に、PR 作成は gh-pr-create に、など）。
- 他のスキルはプレーンなスキル名で参照する。`../git-commit/SKILL.md` のような相対リンクは、スキルを単体でインストールすると壊れる。同じ理由で、リポジトリの `knowledge/` や README へのリンクも張らない。
- 末尾に要約や振り返りの節を置かない。

外部に作用するスキル（PR、Issue、レビュー、マージ、リリース、タグ、push）や、Subagent に作業を委譲するスキルを書くときは、[references/action-skills.md](references/action-skills.md) を読む。

## ファイル構成

- 既定は `SKILL.md` 1 枚にする。本文は 5k トークン未満を目安にする。
- 書式仕様のように必要な局面でだけ読む資料と、稀にしか通らない経路は `references/` に分ける。本文にはいつ開くかだけを書く。同梱ファイルは読まれるまでコンテキストを消費しない。
- 決定的な処理（ソート、計算、機械的な検査）は `scripts/` に置いて実行させる。スクリプトのコード自体はコンテキストに入らず出力だけが入るので、トークン生成で同じ処理をさせるより安く確実になる。実行するものか読むものかを本文で明示する。
- 組にして配るスキル群（フックを伴うものを含む）はプラグインにする。このリポジトリでは `plugins/<name>/` に置き、`.claude-plugin/marketplace.json` に `source: "./plugins/<name>"` で登録する。

## 仕上げ

1. 検証スクリプトがあれば実行する。このリポジトリでは `uv run scripts/validate_skills.py skills/<name> --strict` を使う。
2. README にスキルの一覧があれば、既存の書式で項目を足す。直した場合は既存の項目を実体に合わせる。
3. 代表的なタスクを 1 つ想定し、書いたスキルだけを頼りに実行して詰まる箇所が無いかを確かめる。詰まる箇所があればそこだけを足し、最初から網羅を狙わない。
4. 他のスキルにも通じる規約が新しく生まれたら、okf-knowledge で knowledge に残すことを提案する。

コミットはユーザーが求めたときに git-commit の規約で行う。
