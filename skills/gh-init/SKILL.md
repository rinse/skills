---
name: gh-init
description: Create a GitHub repository for the current local repo, register it as origin, and push the current branch. Use when asked to create a remote or GitHub repo (リモートリポジトリを作成, GitHub にリポジトリを作って, gh repo create). GitHub only.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# GitHub Init

ローカルの git リポジトリに対して GitHub 上のリポジトリを作成し、`origin` として登録して push するスキル。

## スキル固有の判断

このスキル固有の判断は、作るリポジトリの名前・公開範囲・作成先と push 先の `origin` を、ユーザーが意図しない公開や push 先の変更が起きないように決め、作成と push の前に了承を取ることである。

## 対象と前提を確かめてから始める

- ローカルが git リポジトリでなければ対象外とする（`gh repo create --source=.` はそうでないと失敗する）。git-init が使えるなら、先にそれで初期化するよう案内する。
- `gh` が必要（無ければ導入を提案する。GitHub MCP があればそれで代替してよい）。`gh auth status` が未認証を示したら、`gh auth login` をユーザーに実行してもらうよう示して止まる。ログインは対話が要り、エージェントの実行環境では済ませられない。
- `origin` が既にあれば、作成の前に止めてその URL を示し、どうするか（別の remote 名で登録する、既存の `origin` を置き換えるなど）を尋ねる。黙って置き換えると push 先が変わるため。ただし作ろうとしている GitHub のリポジトリを既に指していれば（再実行の場合）、作成を飛ばして push に進む。

## 公開範囲は明示が無ければ非公開にする

ユーザーが公開を明示しない限り private で作る。
公開は取り消しにくく、push と合わさるとその時点でソースコードが公開される。
description（`--description`）も外から見える文面なので、ユーザーが指定したときだけ付ける。

## 作成と push の内容を示して了承を取る

リポジトリ作成は GitHub 上に資産ができる取り消しづらい操作なので、次を提示して了承を得てから実行する。
依頼で名前・公開範囲・作成先がすべて明示されていても、呼び出し元のスキルがリモートを作るかを既に尋ねていても、この了承は省かない。

- 名前: 依頼の文面やディレクトリ名から推測した候補を提示し、自由入力も受ける。
- 公開範囲: 前章の既定に従い、明示が無ければ private と示す。
- 作成先: 既定は認証中のユーザー（`gh api user --jq .login`）。organization なら `<org>/<名前>`。
- push: 作成後に現在のブランチだけを `origin` に push すること（コミットが 0 件なら push しないこと）。

修正の指示があれば反映して再提示する。了承が得られなければ何も作らずに終える。

## 作成に失敗したら名前を変えずに尋ねる

```
gh repo create <名前> --private --source=. --remote=origin
```

公開を明示されたときだけ `--private` を `--public` にする。
GitHub MCP で作った場合は、返ってきた HTTPS の `clone_url` を `git remote add origin <URL>` で登録する。SSH などプロトコルの好みは利用者ごとに違うので、gh 経路では gh の設定に任せる。

同名のリポジトリが既にあって作成に失敗したら、名前を変えて再試行しない。今回は何も作っていないことと、既存のリポジトリの URL、公開範囲、コミットの有無を示し、別の名前で作るか、既存のリポジトリを `origin` に登録するかを尋ねる。前回の実行で作成後に `origin` の登録だけ失敗した場合は後者が正しい続きになるが、無関係な既存のリポジトリに push しないよう、どちらかはユーザーに選ばせる。
権限やネットワークなど、それ以外の理由で失敗したら再試行せず、エラーと実行したコマンドを示して止まる。

## push は一度だけ試し、失敗したら委ねる

続けて `git push origin <現在のブランチ名>` を一度試す。push するのは現在のブランチだけで、タグや他のブランチは push しない。
コミットが 0 件なら push せず、最初のコミットの後に push するよう伝える。
認証などで失敗したら繰り返さず、そのコマンドを示してユーザーに push を依頼する。

## 作った物は取り消さずに報告する

push しなかった場合も失敗した場合も、作成したリポジトリと `origin` の登録は取り消さず、空のリポジトリが GitHub に残っていることを報告に含める。
報告には、リポジトリの URL、公開範囲、`origin` の登録先、push の結果（成功、失敗、未実施とその理由）を書く。
