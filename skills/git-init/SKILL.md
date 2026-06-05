---
name: git-init
description: Use this skill whenever initializing a git repository. This includes when the user asks to "git init", "git-init", set up a new repo, or initialize version control in a directory. Runs git init, switches the git profile (user name / email), and creates an empty initial commit.
---

# Git Init

新しい git リポジトリを初期化するための手順です。以下を順に実行します。

1. `git init` でリポジトリを初期化する
2. git profile を切り替えて user name / email を設定する
3. 空の initial commit を作成する
4. リモートリポジトリを作成するかユーザーに尋ねる（任意）

## 1. git init

```
git init
```

すでに `.git` が存在する（初期化済み）場合は `git init` をスキップし、その旨をユーザーに伝えてから次の手順に進む。

## 2. git profile の切り替え

コミットには user name / email が必要です。`git-profile` という自作コマンドでプロファイルを切り替えます。状況に応じて手順を選んでください。

### git-profile がインストールされているか確認

```
command -v git-profile
```

### インストールされている場合

`git-profile list` でプロファイル一覧を取得する（`*` が現在のプロファイル）。

```
git-profile list
```

- **プロファイルが複数ある場合**: どれを使うかユーザーに選ばせる。選択後 `git-profile switch <PROFILE_NAME>` で切り替える。
- **プロファイルが1つだけの場合**: 確認を取らずそのプロファイルを `git-profile switch <PROFILE_NAME>` で適用する。
- **プロファイルが0個の場合**: 使えるプロファイルがないので、下記「インストールされていない場合」と同様にグローバルの user name / email を確認する。

```
git-profile switch <PROFILE_NAME>
```

### インストールされていない場合

グローバルの user name / email が設定済みか確認する。

```
git config --global user.name
git config --global user.email
```

- **両方とも設定されている場合**: それをそのまま使うので、追加の設定は不要。次の手順に進む。
- **どちらか欠けている場合**: ユーザーに name / email を尋ねてから、ローカル（またはグローバル）に設定する。

## 3. initial commit

空の initial commit を作成します。**エイリアス（`git initial-commit` など）ではなく、必ず以下のフルコマンドで実行してください。**

```
git commit -m 'initial commit' --allow-empty
```

## 4. リモートリポジトリの作成（任意）

リモートリポジトリを作成するかどうかをユーザーに尋ねる。作成しない場合はここで終了。

作成する場合、以下を順に決める。認証はいずれも済んでいる前提とする。

### 使用ツールの判定

1. **`gh` コマンドが使える場合** → `gh` を使う（`command -v gh` で確認）
2. **`gh` がなく GitHub MCP が使える場合** → GitHub MCP のリポジトリ作成ツールを使う
3. **いずれもない場合** → どちらも利用できないためリモートリポジトリの作成を見送る旨をユーザーに伝えて終了する

### リポジトリ名

プロンプトの内容やディレクトリ名から名前を推測し、選択肢として提示する。

1. `<推測した名前>`
2. （ユーザーによる自由入力）

### 公開 / 非公開

選択肢として提示する。

1. public
2. private

### 作成コマンド

**`gh` の場合** — リポジトリを作成し、`origin` リモートを登録する。

```
gh repo create <名前> --public --source=. --remote=origin
```

- 非公開なら `--public` の代わりに `--private` を使う。

**GitHub MCP の場合** — GitHub MCP のリポジトリ作成ツールで、決定した名前・公開設定でリポジトリを作成する。作成後、返ってきた URL を `git remote add origin <URL>` で登録する。

### push

**push はエージェントが実行せず、ユーザー自身に行ってもらう。** SSH 鍵のパスフレーズ入力が対話的に必要になる場合があり、`! ` で実行するサブシェルではパスフレーズを入力できず失敗するため。

`origin` の登録まで終えたら、ユーザーに次の手順を案内する（push 先は常に明示する）。

1. `Ctrl+Z` で Claude Code を一時停止する
2. 自分のシェルで `git push origin <ブランチ名>` を実行する（ここでパスフレーズを入力できる）
3. `fg` で Claude Code に戻ってくる
