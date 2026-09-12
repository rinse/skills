---
name: cleanup-speculation
description: Use this skill whenever the user asks to remove speculative or defensive code, unused abstractions, unused options, or leftover compatibility paths. Triggers on phrases like "過剰な抽象化を削って", "防御的なコードを整理して", "使われていないオプションを消して", "互換コードを消して", "remove speculative code", "remove unused abstractions", "remove legacy paths".
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---
コードベース内の投機的な構造を精査し、削除できるものをすべてリストアップします。
差分は参照せず、完成したコードだけを読んで判断します。

判断基準は「現在のコードベースに、この入力・経路・差し替えを実際に発生させる呼び出し元が存在するか」です。
存在しないものは、将来の要求への先払いか過去の要求の残骸であり、どちらも削除対象です。

削る対象:
- 到達不能な防御（型で排除済みの null チェック、直前で検証済みの値の再検証）
- 例外を握りつぶす try/catch。ログのみで継続するもの
- 呼び出し元が一箇所しかない抽象化・インターフェース・ファクトリ
- 常に既定値でしか呼ばれないオプション引数・設定フラグ
- 使われていないエクスポート・分岐・設定項目
- 「将来〜になったときのため」と説明される拡張点
- 旧形式を受け付ける分岐、呼び出し元のない関数、渡されなくなった引数（legacy 経路）
- 現在のコードベースに存在しない概念や、変更に対する相対位置を指す名前（`fooV2`、`newFoo`、`legacyBar`）。
  名前だけを現在の役割に合わせて改める

残す対象:
- 外部入力の境界での検証（ユーザー入力、ネットワーク、ファイル、パース結果）。
  型の保証が切れる場所なので防御が必要です
- 呼び出し元が一箇所でも、テスト以外の理由で差し替えが必要なもの

削除により呼び出し側が単純化できる場合は、その変更もあわせて提案します。
