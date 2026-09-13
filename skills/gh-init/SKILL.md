---
name: gh-init
description: Create a GitHub repository for the current local repo and register it as origin. Use when asked to create a remote or GitHub repo (リモートリポジトリを作成, GitHub にリポジトリを作って, gh repo create).
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# GitHub Init

ローカルの git リポジトリに対して GitHub 上のリモートリポジトリを作成し、`origin` として登録するスキルです。

## 前提

- ローカルが git リポジトリであること（`gh repo create --source=.` はそうでないと失敗する）。そうでなければ対象外で、git-init が使えるなら先にそれで初期化するよう案内する。
- `gh` が必要（無ければ導入を提案する。GitHub MCP があればそれで代替してよい）。認証は済んでいる前提。

## 決めること

リポジトリ作成は GitHub 上に公開の資産ができる取り消しづらい操作なので、次の 3 点を提示して了承を得てから実行する。

- 名前: プロンプトやディレクトリ名から推測した候補を提示し、自由入力も受ける。
- 公開 / 非公開。
- 作成先: 既定は認証中のユーザー（`gh api user --jq .login`）。organization なら `<org>/<名前>`。

## 作成と push

```
gh repo create <名前> --public --source=. --remote=origin
```

非公開なら `--private`。GitHub MCP で作った場合は、返ってきた URL を `git remote add origin <URL>` で登録する。

続けて `git push origin <ブランチ名>` を一度試す。認証などで失敗したら繰り返さず、そのコマンドを示してユーザーに push を依頼する。
