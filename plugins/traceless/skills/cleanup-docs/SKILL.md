---
name: cleanup-docs
description: List edit residue in prose (README, docs, docstrings) so it reads as written once. Use when asked to remove edit traces from documents (編集痕を消して, 一発で書いたようにして, cleanup docs).
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---
文書内の編集の残滓を精査し、書き直すべき箇所をすべてリストアップします。
差分・git 履歴・会話は参照せず、完成した文書だけを読んで判断します。

判断基準は「最終版だけを読んだ初見の読者が、これは編集されたものだと気づけるか」です。
旧版を知っている人にしか意味が通らない文、文書の外にある会話を前提にした文は、すべて残滓です。

削る対象:
- 旧状態の否定（A は B ではなく C である、not X but Y）。B は文書のどこにも存在しない
- 変更の物語化（以前は〜だったが、previously、used to、no longer、now）
- 理由の混入（〜という事情により、to fix #123）。コミットメッセージに書くべき内容
- 付記型（注:、追記:、NOTE:、UPDATE:、日付入りの但し書き）
- 構造の堆積。「また」「なお」で末尾に足された段落、二箇所に分かれた同じ主題、旧構成のままの見出しと並び順
- 会話の漏出（ご指摘の通り、上記の議論を踏まえ、as discussed）

残す対象:
- 履歴を書くこと自体が目的の文書。CHANGELOG、リリースノート、ADR、移行ガイド、History 節、deprecation 注記
- 「なぜ今この形なのか」の説明のうち、その理由が現在も成立しているもの
- 実行時の状態を述べる「現在は」

修正は文単位の置換ではなく、段落・節の単位で行います。
その単位が主張すべき事実を箇条書きにし、旧文の言い回しを捨てて、事実だけから書き直します。
文単位の置換は「B ではなく C」を生み、旧文のために組まれた前後の構造を残します。

出力は、候補ごとに対象・残滓の形・書き直し案を挙げます。
