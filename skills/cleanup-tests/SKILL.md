---
name: cleanup-tests
description: Use this skill whenever the user asks to cleanup, sort, or organize (unit) tests. Triggers on phrases like "テストを整理して", "テストを統合して", "余計なテストを消して", "organize tests", "remove unnecessary tests", "cleanup tests".
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

コードベース内の全テストを精査し、積極的に削除・統合できるテストをすべてリストアップします。
削る対象:
- 実装のコピー
- モックの自己検証
- 型・ライブラリの保証の再確認
- 他テストとの重複
- 内部実装への過剰な依存
- 過剰なケース分け

判断基準は「削除すると、どんな現実的な不具合を見逃すか」です。
念のためは理由にならず、実行時間・不安定さ・修正負担と保証の価値を比較します。
テスト件数やカバレッジ維持自体は目的ではありません。
