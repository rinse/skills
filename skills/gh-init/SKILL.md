---
name: gh-init
description: Use this skill whenever creating a remote GitHub repository for the current local repo. Triggers on phrases like "リモートリポジトリを作成", "GitHub にリポジトリを作って", "create a GitHub repo", "gh repo create", "リモートを作って push したい", or any request to create a GitHub remote and register it as origin. Creates the repository (via gh or GitHub MCP), registers the origin remote, and hands push off to the user.
metadata:
  author: rinse <rinse418@gmail.com>
  license: MIT
  source: https://github.com/rinse/skills
---

# GitHub Init

ローカルの git リポジトリに対して、GitHub 上のリモートリポジトリを作成し `origin` として登録するためのスキルです。最後の push はまず試し、失敗したらユーザーに依頼します。

認証はいずれも済んでいる前提とします。

## 使用ツールの判定

1. **`gh` コマンドが使える場合** → `gh` を使う（`command -v gh` で確認）
2. **`gh` がなく GitHub MCP が使える場合** → GitHub MCP のリポジトリ作成ツールを使う
3. **いずれもない場合** → `gh` を **インストールするかどうかユーザーに尋ねる**。希望する場合は実行環境（OS / パッケージマネージャ）に合った方法でインストールし（方法は環境に応じて判断。公式は https://cli.github.com ）、`gh` を使って続行する。希望しない場合は、リモートリポジトリの作成を見送る旨を伝えて終了する

## リポジトリ名

プロンプトの内容やディレクトリ名から名前を推測し、選択肢として提示する。

1. `<推測した名前>`
2. （ユーザーによる自由入力）

## 公開 / 非公開

選択肢として提示する。

1. public
2. private

## 作成コマンド

**`gh` の場合** — リポジトリを作成し、`origin` リモートを登録する。

```
gh repo create <名前> --public --source=. --remote=origin
```

- 非公開なら `--public` の代わりに `--private` を使う。

**GitHub MCP の場合** — GitHub MCP のリポジトリ作成ツールで、決定した名前・公開設定でリポジトリを作成する。作成後、返ってきた URL を `git remote add origin <URL>` で登録する。

## push

`origin` の登録まで終えたら、ローカルのコミットをリモートへ push する。**まず一度 `git push origin <ブランチ名>` を試す**（push 先は明示する）。

- **成功した場合** → リモートに反映される。
- **失敗した場合**（認証・パスフレーズ入力が対話的に必要、権限が無い等）→ 無理に繰り返さず、その時点でユーザーに push を依頼する。失敗の内容を簡潔に伝え、実行してほしいコマンド（`git push origin <ブランチ名>`）を示す。ユーザー自身のシェルなら対話的な入力もできる。
