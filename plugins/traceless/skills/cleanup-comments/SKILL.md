---
name: cleanup-comments
description: List code comments that narrate edits or restate code, keeping only those that constrain future editors. Use when asked to clean up or reduce comments (コメントを整理して, cleanup comments).
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---
コードベース内の全コメントを精査し、削除できるコメントをすべてリストアップします。
差分は参照せず、完成したコードだけを読んで判断します。

判断基準は「このコードを一発書きしたとき、このコメントを書くか」です。
補助的に、残す価値のあるコメントは現在形で書けます（〜なので〜している）。
過去形・完了形にしかならないものは、変更の記録であって説明ではありません。

削る対象:
- 変更の叙述（〜に変更した、以前は〜だった、〜を追加）
- 作業報告
- コードの言い換え
- コメントアウトされたコード
- 担当者も期限もない TODO / FIXME
- 構造から自明なセクション見出し・ファイル冒頭の要約

残す対象:
- 将来の編集を制約する情報。これがないと次の編集者が「改善」してバグを再導入するもの
  （外部システムの都合、仕様上の制約、性能上の理由、非自明な実装を意図的に選んだ理由）
- 公開 API の JavaDoc / JSDoc などドキュメント生成の入力になるもの

歴史的経緯を別ファイルに移す作業はしません。上の基準で残るものは少量に収まるので、
コードに併置したまま管理できます。移設先を用意すると、コードと同期しない記述が増えます。
