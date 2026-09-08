---
name: redraw
description: Use when a file has become layered by repeated edits and patching it further would keep the old structure. Triggers on "一から書き直して", "描き直して", "地層になっている", "redraw this file", "rewrite from scratch". A writer who never sees the old version rewrites the file from its tests and a fact list; an inspector then diffs it against the old version and reports dropped behavior and residue.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# 旧版を見ずに描き直す

一つのファイル（またはディレクトリ）を、旧版を見ない書き手に事実とテストだけから書き直させるスキルです。
日々の変更には使いません。
残滓を clean-rewrite で取り除いてもなお構造が旧版に引きずられているとき、ユーザーの指示で使います。

## 役

- **オーケストレーター**：このスキルを実行するエージェント。事実を揃え、書き手と検査役を出し、報告を裁定する。コードは書かない。
- **書き手**：新しいコンテキスト。事実、境界、テストからファイルを新規に書く。旧版を受け取らず、git の履歴も見ない。
- **検査役**：新しいコンテキスト。新版と旧版を読み、落ちた振る舞いと残滓を報告する。何も書かない。

書き手と検査役は Agent ツールで出し、指示には [references/writer.md](references/writer.md) か [references/inspector.md](references/inspector.md) の本文をそのまま含めます。

## 手順

### 1. 事実を揃える

対象ファイルが満たすべき事実を箇条書きにします。
出どころは、そのファイルのテスト、README やドキュメント、呼び出し側のコード、ユーザーの指示です。
旧版から事実を拾ってよいですが、言い回しと構造は拾いません。
呼び出し側が使う公開シグネチャは**境界**として別に列挙します。

事実が曖昧なら一つか二つだけユーザーに尋ね、残りは自分で埋めます。

### 2. 旧版を退け、書き手を出す

作業ツリーから対象ファイルを消します。
旧版は `git show HEAD:<path>` で取り出せるので、退避は要りません。

```
git rm -q <path>
```

書き手に渡すものは次の通りです。

- 事実の箇条書きと境界
- 書くパスと、受け入れ条件となるテストのパス
- テストの実行コマンド
- 差し戻しなら検査役の指摘（到達状態で書き、「X を Y に変える」という形は使わない）
- `references/writer.md` の本文

変更の理由と会話は渡しません。

### 3. 検査役を出す

書き手が書き上げたら検査役を出します。
渡すものは、事実と境界、新版のパス、旧版の取り出し方（`git show HEAD:<path>`）、`references/inspector.md` の本文です。

### 4. 裁定する

| 指摘 | 裁定 |
|---|---|
| 不足、残滓 | 差し戻す |
| 落ちた振る舞い | 今も必要なら事実に加えて差し戻す。不要ならユーザーに確認して落とす |
| 書き手が曖昧と判断した点 | 事実を一意にし、書き手の判断と違えば差し戻す |

同じファイルへの差し戻しは三回までです。
超えたら手順を止め、新版を作業ツリーに残したまま指摘と状態をユーザーに報告します。

### 5. 終える

プロジェクト全体のテストを通し、新版を作業ツリーに残します。
コミットはしません。
返信には、落とした振る舞い、曖昧だった事実をどう定めたか、退けた指摘とその理由を書きます。
