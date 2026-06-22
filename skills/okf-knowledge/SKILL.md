---
name: okf-knowledge
description: Use this skill whenever the user wants to capture, accumulate, or consolidate knowledge/insights gained during work into a persistent, reusable form. Triggers on phrases like "知見を貯めて", "知見をまとめて", "知見を記録して", "ナレッジ化して", "学びを残して", "ここまでの知見を整理して", "capture this knowledge", "accumulate knowledge", "write this up as knowledge". Produces an Open Knowledge Format (OKF) knowledge bundle — a directory of markdown concept files with YAML frontmatter — under the project's knowledge/ directory, maintaining index.md, log.md, and a pointer in AGENTS.md as appropriate.
metadata:
  author: rinse <rinse418@gmail.com>
  license: MIT
  source: https://github.com/rinse/skills
---

# OKF Knowledge

作業の中で得た**知見**を、後から人間にも Agent にも再利用できる形で残すためのスキルです。知見を [Open Knowledge Format (OKF)](#references) に従った **knowledge bundle**（YAML frontmatter 付き markdown ファイルのディレクトリ）として記録します。

「知見を貯めて」「知見をまとめて」のような依頼が来たら、いま終えた（または進行中の）作業・会話から再利用価値のある知見を抽出し、OKF の concept ファイルとして bundle に書き出します。

## このスキルの肝は「何を knowledge にするか」の判断

OKF の書式（frontmatter のフィールド、リンク記法、ファイル構成）は後半の[リファレンス](#okf-リファレンス)にまとめてあります。書式は機械的に従えば済むので、このスキルで本当に難しく価値があるのは **「いま得た知見のうち何を、どの粒度で、どんな concept として残すか」という判断**です。ここに思考を集中させてください。

### 何を残すか

残す価値があるのは、**次に同じ文脈に来た人（や Agent）が知らずに同じ落とし穴にはまる／同じ調査をやり直す**ような知見です。例:

- 非自明な事実・制約（「この API は X のとき Y を返す」「このテーブルの `status` は歴史的経緯で 3 種類の意味を持つ」）
- ハマりどころと回避策（「ビルドが Z で失敗するのは W が原因」）
- 設計判断とその理由（なぜその方式を選んだか／選ばなかったか）
- 手順・プレイブック（再現性のある操作手順）
- ドメイン用語・概念の定義と関係

逆に**残さないもの**: コード・git 履歴・既存ドキュメントを読めば自明なこと、その場限りで再利用されない一過性の事情。迷ったら「3 ヶ月後の誰かがこれを読んで時間を節約できるか？」で判断します。

### どの粒度で分けるか（1 concept = 1 つの知識単位）

OKF の concept は「1 つの知識単位」を表す 1 ファイルです。粒度の指針:

- **1 つの対象・トピックにつき 1 concept。** 「テーブル orders」「認証フロー」「デプロイ手順」のように、見出しを付けられる単位で切る。
- 複数の独立した知見を 1 ファイルに詰め込まない。逆に、互いに切り離すと意味をなさない断片を無理に分けない。
- 関連する concept はサブディレクトリでまとめてよい（例: `tables/`, `playbooks/`, `concepts/`）。最初は浅い構成で始め、増えてきたら整理する。

### type / title / リンクを丁寧に選ぶ

- **`type`**（必須）: その concept の種類を表す短い文字列。`Playbook`, `API Endpoint`, `Domain Concept`, `Gotcha`, `Design Decision`, `BigQuery Table` など、**説明的で自己説明的**な値を選ぶ。中央レジストリはないので、プロジェクト内で一貫した語彙を使う。
- **`title`**: 人が一覧で見て中身が分かる名前。
- **クロスリンク**: concept どうしの関係は、本文中の markdown リンクで表現する（[リンク記法](#クロスリンク)参照）。関連する既存 concept があれば積極的にリンクし、知識をグラフとしてつなぐ。リンク先がまだ無くてもよい（未執筆の知見を指しているだけ、と解釈される）。

判断に迷う・知見が大量にある場合は、**先に「どんな concept を作るつもりか」を箇条書きでユーザーに提示して合意を取って**から書き出すと手戻りが減ります。

## 手順

### 1. bundle の場所を決める

特に指示がなければ、**プロジェクトルート直下の `knowledge/`** を bundle ルートとします。プロジェクトルートは次で判定します（この git 判定は後の `log.md` の判断にも使うので、ここで一度だけ確認しておく）:

```
git rev-parse --is-inside-work-tree   # git 管理下か
git rev-parse --show-toplevel         # git 管理下ならこれがプロジェクトルート
```

- **git 管理下**: `show-toplevel` の出力をプロジェクトルートとし、その直下の `knowledge/` を使う。
- **git 管理外**: カレントディレクトリをプロジェクトルートとみなす（曖昧なら場所をユーザーに確認する）。
- ユーザーが別の場所を指定した場合はそれに従う。

`knowledge/` が既に存在する場合は**新規作成ではなく既存 bundle への追記**として扱います（後述の「既存 bundle への追記」）。

### 2. concept ファイルを書き出す

上の「何を knowledge にするか」の判断に基づき、concept を OKF 準拠の markdown ファイルとして作成します。必須・推奨の frontmatter と本文の書き方は[リファレンス](#okf-リファレンス)に従ってください。

- 既存の concept と同じ対象を扱う場合は**新規ファイルを作らず既存ファイルを更新**する（重複を作らない）。
- `timestamp` には現在日時（ISO 8601）を入れる。

### 3. index.md を作成・更新する（常に）

bundle ルートの `index.md` は**常に**作成・維持します。サブディレクトリを作った場合はその階層にも `index.md` を置きます。`index.md` は progressive disclosure（中身を開く前に何があるか分かる）ためのもので、書式は[リファレンス](#index-files)参照。

- 新しく作った concept を、適切なセクションの箇条書きに、frontmatter の `description` 付きで追加する。
- 既存 `index.md` がある場合は該当セクションに**追記**する（全面書き換えしない）。

### 4. log.md の扱い（git 管理下かどうかで分岐）

`log.md` は変更履歴を記録する予約ファイルです。**作成するかどうかは bundle が git 管理下かで決めます**（手順 1 の判定を再利用）:

- **git 管理下**: `log.md` を**作成しない**。変更履歴は git が担うため。
- **git 管理外**: `log.md` を作成するかどうか**ユーザーに尋ねる**。希望されたら作成する。

ただしこの分岐は**新規作成の話**です。**既に `log.md` が存在する場合は、git 管理下かどうかに関わらず追記して維持します**（過去に非 git で作られた bundle が後から git 化したケースなどを壊さないため）。追記の書式は[リファレンス](#log-files)参照（ISO 8601 の日付見出し、新しい順）。

### 5. AGENTS.md にポインタを張る（ほとんどの場合に必要）

Agent が knowledge bundle の存在にスムーズに気づけるよう、**プロジェクトルートの `AGENTS.md` から bundle へのポインタ**を張ります。

1. `AGENTS.md` を読む。
2. **既に bundle への言及（`knowledge/` への参照など）がある場合**: 何もしない。
3. **`AGENTS.md` はあるが bundle への言及がない場合**: 「Agent が見つけられるよう `AGENTS.md` にリンクを張ってよいか」をユーザーに尋ね、了承を得たら追記する（例: 「## Knowledge」セクションに `knowledge/index.md` への 1 行リンクと一言説明）。
4. **`AGENTS.md` が存在しない場合**: ポインタを記載した `AGENTS.md` を新規作成してよいか**尋ねる**。勝手に作らず、勝手に飛ばさない。

### 既存 bundle への追記（「知見を貯めて」の通常ケース）

`knowledge/` が既にある場合は、上の手順を**追記モード**で行います。要点:

- concept は対象ごとに**更新 or 新規**を判断（既存対象なら同じファイルを更新し、重複ファイルを作らない）。
- `index.md` は該当セクションに追記。
- `log.md` が**既にあれば**追記する（手順 4 の git ルールは「作るか否か」にのみ適用）。
- `AGENTS.md` のポインタが**既にあれば**手順 5 の確認はスキップ。

---

## OKF リファレンス

OKF v0.1 の書式。困ったときに参照する。`type` 以外の制約は**ソフトな指針**であり、consumer は欠損フィールド・未知の type・壊れたリンクを理由に bundle を拒否してはならない、という寛容な設計が前提。

### bundle 構成

```
knowledge/                    # bundle ルート
├── index.md                  # 常に作成（progressive disclosure）
├── log.md                    # git 管理下では作らない／既存なら維持
├── <concept>.md              # ルート直下の concept
└── <subdir>/                 # concept のグループ
    ├── index.md
    └── <concept>.md
```

- `index.md` と `log.md` は**予約ファイル名**。concept ドキュメントには使わない。それ以外の `.md` はすべて concept。
- **Concept ID** = `.md` を除いたファイルパス（例: `tables/orders`）。

### concept ドキュメント

frontmatter（YAML）+ markdown 本文。

```yaml
---
type: <種類名>                 # 必須・非空。これだけが唯一の必須フィールド
title: <表示名>                # 推奨。無ければファイル名から導出される
description: <1 行要約>        # 推奨。index やプレビューで使われる
resource: <正規 URI>          # 任意。対象資産を一意に指す URI
tags: [<tag>, <tag>]          # 任意
timestamp: <ISO 8601 日時>    # 任意。最終更新日時
# producer 独自のキーを追加してよい
---
```

本文は**構造化 markdown**を優先（見出し・箇条書き・表・コードブロック）。散文より構造の方が人間の読解にも Agent の検索にも効く。慣例的な見出し（いずれも任意）:

| 見出し | 用途 |
|--------|------|
| `# Schema` | 対象のカラム/フィールドの構造的記述 |
| `# Examples` | コードブロックでの具体的な利用例 |
| `# Citations` | 本文の主張を裏付ける外部出典 |

### クロスリンク

concept どうしは標準 markdown リンクでつなぐ。リンク A→B は「A と B に関係がある」という主張で、関係の種類は周囲の文章で表す（リンク自体は無向・無型として扱われる）。

- **絶対（bundle 相対）リンク**: `/` 始まりで bundle ルートから解釈。ドキュメント移動に強いので**推奨**。例: `[orders テーブル](/tables/orders.md)`
- **相対リンク**: 通常の相対パス。例: `[隣の concept](./other.md)`
- リンク先が存在しなくてもよい（未執筆の知見を指しているだけ、と解釈される）。

### index files

`index.md` は**frontmatter を持たない**（唯一の例外: bundle ルートの `index.md` は `okf_version: "0.1"` の宣言**のみ**を目的とした frontmatter を持ってよい。サブディレクトリの `index.md` は frontmatter なし）。本文はセクションごとに concept を箇条書きする:

```markdown
# セクション見出し

* [Title 1](relative-url-1) - 短い説明
* [Title 2](relative-url-2) - 短い説明

# 別のセクション

* [サブディレクトリ](subdir/) - 説明
```

各エントリの説明はリンク先 concept の `description` から取る。

### log files

`log.md` は変更履歴。日付でグループ化したフラットなリストで、**新しい順**。日付は ISO 8601 `YYYY-MM-DD`。エントリは散文で、先頭の太字は慣例（必須ではない）。

```markdown
# Update Log

## 2026-06-18
* **Update**: Added [Customer Metrics](/tables/customer-metrics.md).
* **Creation**: Established [Dataplex Playbook](/playbooks/dataplex.md).

## 2026-06-15
* **Initialization**: Created directory structure.
```

### citations

本文が外部資料に基づく主張をする場合、出典を `# Citations` 見出し以下に番号付きで列挙する。リンクは絶対 URL でも bundle 相対パスでも、`references/` サブディレクトリ内の資料でもよい。

```markdown
# Citations

[1] [BigQuery announcement](https://cloud.google.com/blog/...)
[2] [Internal runbook](https://wiki.acme.internal/data/quality)
```

### conformance（適合条件）

bundle が OKF v0.1 に適合するのは:

1. 予約ファイル以外のすべての `.md` がパース可能な YAML frontmatter を持つ
2. すべての frontmatter が非空の `type` フィールドを持つ
3. 予約ファイル名（`index.md` / `log.md`）が存在する場合は所定の構造に従う

それ以外（欠損フィールド・未知 type・未知キー・壊れたリンク・index 欠如）は適合性を損なわない。

## References

OKF の一次資料:

- README（概要）: https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf/README.md
- SPEC（仕様）: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
