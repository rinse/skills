---
name: kickoff
description: Use this skill whenever bootstrapping a brand-new project from scratch — turning an empty directory into a working repo. Triggers on phrases like "プロジェクトを一から作って", "新規プロジェクトを立ち上げて", "kick off a new project", "bootstrap this repo", "set up a fresh project from scratch", or any request to initialize a brand-new codebase end-to-end (not for adding a feature to an existing project, and not plain "git init" alone — use git-init for that). Sets up the repo via git-init/gh-init, installs the project's baseline skill set via `gh skill install` (git-commit, okf-knowledge, technical-writing-ja, concurrent-dev always; other git-* by choice; all gh-* if a remote exists — never git-init/gh-init, which are init-only), skipping any step whose tool isn't available, then writes minimal README.md/AGENTS.md splitting docs into docs/ (human) and knowledge/ (agent), and commits them via git-commit.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# Kickoff

プロジェクトを一から立ち上げるためのスキルです。**このスキルの核は、立ち上げ時に必要な一連の意思決定（どのスキルを入れるか、リモートを作るか、ドキュメントをどこに置くか）を代行し、抜け漏れのない初期状態を一気に整えること**です。個々の作業（git 初期化、リモート作成、スキル導入、コミット）はそれぞれ専用のスキル・コマンドに委譲します（合成主義）。

## 全体の流れ

1. ガードと前提確認
2. リポジトリのセットアップ（`git-init` → `gh-init`）
3. プロジェクトの baseline スキルを導入する（`gh skill install`）
4. README.md / AGENTS.md を書く
5. コミットして終了する（`git-commit`）

各手順は、対応するツール・スキルが無ければ**エラーにせずスキップ**します。無いことを黙って無視するのではなく、スキップした旨を毎回ユーザーに一言伝えてから次に進んでください。

## 1. ガードと前提確認

- **すでに作り込まれたプロジェクトの場合**（`README.md` や `AGENTS.md` に実質的な内容が既にある、コミット履歴が長い、等）→ このスキルは「一から作る」ためのものであり対象外です。その旨を伝え、本当にこのスキルで進めてよいか（既存の `README.md` / `AGENTS.md` を上書きしてよいか）を確認してから進めてください。空リポジトリ・初回コミットのみ、といった「これから立ち上げる」状態なら確認不要でそのまま進めます。
- 現在地が git リポジトリかどうかを `git rev-parse --is-inside-work-tree` 等で確認しておく（次の手順の分岐に使います）。

## 2. リポジトリのセットアップ

### 2-1. `git-init`

利用可能なスキル一覧に `git-init` があれば Skill ツールで起動する。無ければこのステップをスキップし、その旨を伝えて次に進む（素の `git init` で代替しない — `git-init` はプロファイル切り替えや initial commit まで含む一連の作法を持つため、無ければ丸ごと見送るのが安全側）。

`git-init` は実行の最後に「リモートリポジトリを作るか」をユーザーに尋ね、希望されれば自分で `gh-init` を呼び出します。ここで既にリモートまで作られている場合、次の 2-2 は不要です。

### 2-2. `gh-init`（リモートがまだ無い場合）

`git remote -v` で `origin` の有無を確認する。

- **すでに `origin` がある**（2-1 の中で作成済み、または元々あった）→ このステップは不要。次の手順 2-3 へ。
- **まだ無い**（`git-init` が使えなかった、使ったが「リモートは今は作らない」を選んだ、等）→ 改めてリモートリポジトリを作るかどうかをユーザーに尋ねる。作成を希望する場合、利用可能なスキル一覧に `gh-init` があれば起動する。無ければこのステップをスキップし、その旨を伝える。

### 2-3. リモート有無の確定

`git remote -v` で最終的な `origin` の有無を確認する。ただし `gh-*` 系スキルはいずれも GitHub の PR/Issue 専用なので、ここで見るべきは「`origin` があるか」だけでなく**「`origin` が GitHub か」**です。`gh repo view` が成功するか、`origin` の URL に `github.com` が含まれるかで判定してください。GitLab や自前ホスティングなど GitHub 以外のリモートしか無い場合は「リモートなし」と同じ扱いにする（`gh-*` は導入しても発火しないため）。この判定結果を、以降「リモートあり / なし」として手順 3 で使います。

## 3. プロジェクトの baseline スキルを導入する

### 3-1. スキルのインストールコマンドの有無を確認する

`command -v gh` を確認したうえで、`gh skill install --help` と `gh skills install --help`（サブコマンド名が単数形・複数形のどちらの環境もあり得るため両方試す）のどちらが通るかを確認し、通った方を以降で使う。どちらも使えなければ手順 3 全体をスキップし、その旨をユーザーに伝えて手順 4 に進む。

### 3-2. 導入するスキルを決める

まず、インストール可能なスキルの一覧を取得する。3-1 で確認したコマンド（`gh skill` / `gh skills`）に一覧サブコマンド（`list` 等）があればそれを使う。一覧取得手段が無ければ、現在のセッションで見えているスキル一覧（Skill ツールの一覧）から拾うが、これはインストール元カタログの全体を反映するとは限らない点に留意する。

取得した一覧をもとに、次の3グループで導入対象を決める。

- **常時導入**（基本的にすべてのリポジトリで入れる）: `git-commit`, `okf-knowledge`, `technical-writing-ja`, `concurrent-dev`。一覧に無いものは黙ってスキップし、その旨を伝える。
- **`git-*`（`git-commit` を除く）**: `git-bisect` のような他の `git-*` スキルは、ユーザーの好みが分かれるところなのでインストール前に選ばせる。一覧から `git-*` かつ `git-commit` 以外のものを列挙し、AskUserQuestion（複数選択可）でどれを入れるか確認する。1つも選ばれなければ導入しない。
- **`gh-*`**: 手順 2-3 で確定した通りリモートがある場合のみ、一覧にある `gh-*` スキルを**すべて**導入する。リモートが無い場合はこのグループを丸ごと見送る（GitHub 連携スキルはリモートがあって初めて使い道があるため）。

**`git-init` と `gh-init` は導入対象から除外する**（ユーザーに選ばせもしない）。どちらもプロジェクトの初期化にしか使わず、立ち上げが済んだ後のプロジェクトでは発火する場面が無いため、プロジェクトローカルに入れる価値がありません。これらはユーザーのグローバル環境に置いておくべきスキルです。

### 3-3. 導入を実行する

決定したスキルを1つずつ `<コマンド> install <name>` で導入する（複数同時指定できる場合はまとめてよい）。個別のスキルの導入に失敗しても、その旨を伝えつつ残りは続行する（1つの失敗で全体を止めない）。既定のスコープ（プロジェクトローカル、`.claude/skills/` 相当）で導入し、グローバルへは入れない。スキルの有無はエージェントの挙動を左右するため、プロジェクト単位で明示的に管理し、そのプロジェクトを触らないエージェントのコンテキストを不要なスキルで圧迫しないためです。

## 4. README.md / AGENTS.md を書く

**役割分担**: 人間向けドキュメントは `docs/` に、エージェント向けドキュメント（knowledge bundle 等）は `knowledge/` に置きます。`README.md` と `AGENTS.md` はどちらも**索引**であり、詳細を書き込む場所ではありません。

- **`README.md`**: プロジェクトの概要・目的など極めて重要なことだけを書く。それ以外は書かず、`docs/` 配下のドキュメントへのリンク集にする。
- **`AGENTS.md`**: プロジェクトの概要・目的に加えて、上記のドキュメント管理規則（README は索引専用・人間向けは docs/・エージェント向けは knowledge/）をそのまま明記する。`docs/` と `knowledge/` 配下のドキュメントへのリンクを持つ。

まだ `docs/` や `knowledge/` に実体のあるドキュメントが無い段階なら、リンク集の見出しごと省略する（空の見出しや「まだ何もありません」的なプレースホルダ行を残さない）。中身のないディレクトリも無理に作らない。ドキュメントが実際にできた時点で、その見出しとリンクを追記する運用とします。

### プロジェクトの概要・目的を確定する

この会話の中で既にプロジェクトの目的が語られていればそれを使う。語られていなければ、書き始める前にユーザーに一言確認する（何を・誰のために・なぜ作るのか、2〜3文で足りる粒度でよい）。

### テンプレート

`docs/` / `knowledge/` にまだ何も無い立ち上げ直後は、リンク集の見出しごと省く（下の例で `## ドキュメント` 等が丸ごと無い状態）。

`README.md`:

```markdown
# <プロジェクト名>

<概要・目的を2〜3文で。>
```

`AGENTS.md`:

```markdown
# AGENTS.md

<概要・目的を2〜3文で。README と同内容でよい。>

## ドキュメント管理

- `README.md`: プロジェクトの概要・目的など最重要事項のみ。詳細は書かず `docs/` へのリンク集にする。
- `docs/`: 人間向けドキュメントを置く。
- `knowledge/`: エージェント向けドキュメント（knowledge bundle 等）を置く。
```

`docs/` または `knowledge/` に実際にドキュメントができた時点で、それぞれ `## Documentation` / `## Knowledge` の見出しとリンクを両ファイルに追記する（README には `## Documentation` 相当の見出しで `docs/` へのリンクのみ、AGENTS には両方）。

見出し・文言はプロジェクトの言語（日本語 / 英語）に合わせて調整してよい。日本語で書く場合、利用可能なら `technical-writing-ja` スキルの規範（一文一改行、体言止めの禁止など）に従う。

**上書きに注意**: 手順 1 のガードで確認済みでない限り、既存の `README.md` / `AGENTS.md` に実質的な内容がある状態でこの手順に来ることは無いはずです。もし来た場合は書き換える前に必ず確認を取る。

## 5. コミットして終了する

`README.md` と `AGENTS.md` をコミットします。

- 利用可能なスキル一覧に `git-commit` があれば Skill ツールで起動する（手順 3 で導入されていれば、この時点で使えるようになっているはず）。
- 無ければ、`git-commit` の規約 ── コミットメッセージは単一行 + conventional-commit 風 prefix（例: `docs: add README and AGENTS`）、`git add -A` は使わずファイルを明示指定（`git add README.md AGENTS.md`）── に従って自分でコミットする。

コミットが完了したら、このスキルの作業は終了です。作成したファイル・導入したスキル・（作成していれば）リモートリポジトリの URL を簡潔にユーザーへ報告し、後続の作業（実装等）へは自動で進まず終了してください。
