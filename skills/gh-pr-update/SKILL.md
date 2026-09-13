---
name: gh-pr-update
description: Re-synthesize an open GitHub PR's title, body, and labels from its current diff. Use when asked to update a PR description, or after a PR's code has changed (PR の説明を更新して, update the PR description). GitHub only; does not create or merge PRs.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# GitHub PR Update

既存の GitHub PR の title・body・labels を、現在の差分と一致した状態に描き直すスキルです。古い本文に追記するのではなく、いまの差分全体から合成し直すのが核です。「コードを直したら本文も直す」を成立させるためのスキルで、gh-address-review など PR のコードを変える作業の最後に呼ばれます。

## 前提

- `gh` が必要（無ければ導入を提案する。GitHub MCP があればそれで代替してよい）。GitHub PR でなければ対象外。
- 対象 PR は、ユーザーが番号・URL を示したか、文脈から一意に明らかな場合だけ確定させる。定まらなければ尋ねる。`gh pr view <num> --json number,title,url,headRefName,baseRefName` で取得したタイトル・ブランチが意図した PR か確かめる。

## コンテキストの収集

- 現在のメタ情報: `gh pr view <num> --json title,body,labels`（確認時の before として使う）。
- 差分: ブランチをチェックアウト済みなら `git -P diff <base>...HEAD` と `git --no-pager log <base>..HEAD`、そうでなければ `gh pr diff <num>`。
- 未コミットの変更は差分に現れず、修正前の状態から本文を組み立ててしまう。`git status` を確認し、あれば先にコミットする（git-commit の規約で）。未 push のコミットがあればローカルの差分を正とし、後で push する。
- なぜ変わったか（レビュー指摘・追加要望）は本文の「なぜ」を正確にするために読む。コメントへの逐一の返答を本文に書き写すためではない。

## 再合成

- title: 変更の目的を一行で、conventional-commit 風 prefix 付き。主目的が変わったなら title も変える。
- body: 現在の差分全体を「最終的に何を・なぜ」として書く。古くなった記述・過程・WIP の名残は消す。PR テンプレート（検出場所は gh-pr-create と同じ）があればその構成を保つ。
- labels: 既存ラベルから内容に合うものを増減する。無いラベルは作らない。

## 確認と更新

PR の編集は関係者に見える操作なので、before → after（title・body の要点・labels の増減・未 push の有無）を提示して了承を得てから更新する。変える項目だけを指定し、body はファイルから `--body-file` で渡す。

```
gh pr edit <num> --title "..." --body-file <path> --add-label "<label>" --remove-label "<label>"
```

未 push のコミットがあれば `git push origin <branch>` を一度試し、認証などで失敗したら繰り返さずユーザーに依頼する。更新後の URL と変更点を報告する。
