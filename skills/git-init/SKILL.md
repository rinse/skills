---
name: git-init
description: Use this skill whenever initializing a git repository. This includes when the user asks to "git init", "git-init", set up a new repo, or initialize version control in a directory. Runs git init, switches the git profile (user name / email), and creates an empty initial commit.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
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

まず **`git-profile` をインストールするかどうかユーザーに尋ねる**。

- **インストールを希望する場合**: 下記「git-profile のインストール」に従ってインストールし、完了後に「インストールされている場合」の手順へ進む。
- **インストールを希望しない場合**: 下記「グローバル設定で代替する」に従う。

#### git-profile のインストール

`git-profile` は [rinse/git-profile-rs](https://github.com/rinse/git-profile-rs) で開発されており、GitHub Releases からインストールできる。`gh` CLI が使える前提で、以下の手順で導入する。

1. 最新リリースのアセット一覧を確認する。

   ```
   gh release view --repo rinse/git-profile-rs
   ```

2. 一覧の中から実行環境（OS / アーキテクチャ）に合うアセットを **自分で判断して選ぶ**。`uname -sm` 等で現在のプラットフォームを確認してよい。アセット名はリリースごとに変わり得るので、固定の名前を仮定せず必ず実際の一覧から選ぶこと。

3. 選んだアセットをダウンロードして展開し、PATH の通った場所に配置する。

   ```
   TMP=$(mktemp -d)
   gh release download --repo rinse/git-profile-rs --pattern '<選んだアセット名>' --dir "$TMP"
   tar -xzf "$TMP"/*.tar.gz -C "$TMP"
   mkdir -p "$HOME/.local/bin"
   mv "$TMP/git-profile" "$HOME/.local/bin/"
   ```

`$HOME/.local/bin` が PATH に含まれていない場合は、その旨をユーザーに伝える。Rust 環境がある場合は `cargo install git-profile` でも導入できる。

インストール後、まだプロファイルが1つも無いはずなので、`git-profile list` で確認し、無ければユーザーに name / email を尋ねてプロファイルを作成する（`$XDG_CONFIG_HOME`（既定 `~/.config`）の `git-profile/<PROFILE_NAME>.gitconfig` に `[user] name / email` を書く）。その後 `git-profile switch <PROFILE_NAME>` で適用する。

#### グローバル設定で代替する

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

作成する場合は **`gh-init` スキルを呼び出して** リモートリポジトリの作成・`origin` 登録・push 案内を任せる。
