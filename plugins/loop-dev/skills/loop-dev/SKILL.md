---
name: loop-dev
description: Work through ready issues in a loop. Pick an issue, implement it with concurrent-dev, deliver it, and file new issues toward the project goals. Use when asked to run the development loop over the issue backlog (loop-dev を回して, Issue を消化して).
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# Loop Dev

Issue を 1 件ずつ、選定 → 実装 → 納品 → 新しい Issue の起票 の順に処理し、処理できる Issue が無くなるまで繰り返すスキルです。

## このスキルの核

あなたはループ全体のオーケストレーターです。各段階の作業は Subagent に任せ、自分は段階の間の判断（進めるか、差し戻すか、止めるか）だけを行います。Issue の本文や差分を自分のコンテキストに抱えると、数周でループを見通せなくなるためです。Subagent からは結論だけを受け取ります。

人間が関わるのは 2 か所です。どの Issue を ready にするか（ループへの入力）と、納品されたものを受け入れるか（PR のマージ、またはマージ済みコミットの確認）です。このスキルは Issue を自分で ready にしません。

## 前提

- git リポジトリで、作業ツリーが綺麗であること。未コミットの変更があれば始めずに報告する。
- 起動時のブランチをベースブランチとする。各周の終わりには必ずここへ戻る。
- Issue の置き場と形式は create-issue スキルに従う（ローカルは frontmatter の `status`、GitHub は `ready` ラベル）。
- このスキルと Subagent が作るコミットは、すべて git-commit スキルに従う。Subagent への指示にもそう書く。

## 1 周の流れ

### 1. 選定

`general-purpose` の Subagent（Sonnet）を起動し、pick-issue スキルで Issue を 1 件選んで確保させます。ユーザーが Issue を指定していれば、それを伝えます。

選べる Issue が無いと報告されたら、ループを終えます（→ 終了時の報告）。欠陥があって差し戻された Issue の報告は、終了時の報告まで控えておきます。

### 2. 実装

`general-purpose` の Subagent（モデルは自分と同じ）を起動し、concurrent-dev スキルで Issue を実装させます。この Subagent が concurrent-dev のオーケストレーターになり、計画の審査・テスト作成・実装の Subagent をさらに起動します。渡すのは次です。

- Issue の所在（パスまたは URL）。本文は渡さず、Subagent 自身に読ませる。
- 作業ブランチ: ベースブランチから `loop/<Issue の ID>` を切り、これを concurrent-dev のベースブランチとする。元のベースブランチには触れない。
- 無人で進めること。人間への質問や確認はせず、判断がつかなければ推測で進めずに止まって報告する。Issue の記述同士、またはテストと Issue が食い違う場合も、どちらかを選ばずに止まる。
- Issue への書き込み・push・PR 作成はしない。
- 報告: 完了か中断か、マージしたコミットの要約、残る懸念。中断なら、止まった段階・理由・人間に決めてほしいこと。

### 3. 納品

完了と報告されたら、Issue の置き場に応じて納品します。差分を読む作業なので Subagent（Sonnet）に任せます。

- **GitHub の Issue**: gh-pr-create スキルで、作業ブランチからベースブランチへのドラフト PR を作る。本文に `Closes #<番号>` と、受け入れ条件ごとの対応、残る懸念を入れる。loop-dev の起動をもって了承済みとし、作成前の確認はしない。push に失敗したら繰り返さず、差し戻しに回す。
- **ローカルの Issue**: ベースブランチで `git merge --squash` し、Issue ファイルの `status` を `done` にして、同じコミットに含める。test / build / lint を流し、通ったら作業ブランチを消す。コンフリクトや失敗があれば取り込みを取り消し、差し戻しに回す。

ブランチの削除は環境によって禁止されている場合があります。削除は他のコマンドとつなげずに単独で実行し、拒否されたら回避せず、残ったブランチを終了時の報告に含めます。差し戻しにはしません。

### 4. 新しい Issue の起票

納品が済んだら、次に取り組む価値のある Issue を起票するか検討します。`general-purpose` の Subagent（モデルは自分と同じ）に、次を指示します。

- README など、リポジトリから読み取れるプロジェクトの概要と目標を読む。読み取れなければ、何も起票せずにその旨を報告する。
- 目標と現状（コード、既存の Issue、直近の変更）の差から、次の一手として明確な Issue の案があるかを考える。明確な案が無ければ起票しない。数を埋めるための起票はしない。
- 案があれば、既存の Issue（完了済みを除く）と重複しないことを確かめ、create-issue スキルで起票する。多くても 2 件。置き場は今回の Issue と同じ。ready にはしない。

起票された Issue に着手させるかは人間が決めます。

### 5. 次の周へ

ベースブランチにいて作業ツリーが綺麗なことを確かめ、1 に戻ります。ユーザーが Issue を 1 件指定していた場合は、1 周で終えます。

## 差し戻し

実装が中断した場合、または納品に失敗した場合は、その Issue を人間に差し戻して次の周へ進みます。

- 未コミットの変更があれば `git stash -u -m "loop-dev/<ID>"` で退避し、ベースブランチに戻る。作業ブランチと `.wt/` の worktree は消さない。
- Issue にコメントを残す。内容は、止まった段階、理由、人間に決めてほしいこと、作業ブランチ名、退避した stash の名前。ローカルの Issue はファイル末尾の `## loop-dev log` 節に追記する。
- ローカルの Issue は `status` を `blocked` にしてコミットする。GitHub の Issue は ready が外れたままなので、人間が付け直せば再投入される。

同じ原因（権限の拒否、テスト環境の不備など）で 2 件続けて差し戻しになったら、Issue ではなく環境の問題なので、ループを止めて報告します。

## 終了時の報告

- 処理した Issue ごとの結果: 納品（PR の URL、またはコミット）か差し戻し（理由）か
- 起票した Issue と、起票を見送った理由
- 人間の対応待ちになっているもの: レビュー待ちの PR、blocked の Issue、ready にするか判断待ちの新しい Issue

## やらないこと

- Issue を ready にしない。PR をマージしない。
- Subagent の仕事（Issue の読解、実装、差分の読解）を自分でやらない。
- 依存する Issue の PR が未マージのうちに、その続きの Issue へ進まない（pick-issue が完了待ちとして除外する）。
