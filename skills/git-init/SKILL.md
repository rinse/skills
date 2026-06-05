---
name: git-init
description: Use this skill whenever initializing a git repository. This includes when the user asks to "git init", "git-init", set up a new repo, or initialize version control in a directory. Runs git init, switches the git profile (user name / email), and creates an empty initial commit.
---

# Git Init

新しい git リポジトリを初期化するための手順です。以下を順に実行します。

1. `git init` でリポジトリを初期化する
2. git profile を切り替えて user name / email を設定する
3. 空の initial commit を作成する

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
