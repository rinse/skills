---
type: Design Principle
title: スキル設計の思想
description: 「核（判断）」と機械作業を分離し、合成主義で出力を組み立てる本リポジトリ共通の設計思想と、アクションスキルの共通骨格。
tags: [skill-authoring, design-principle, philosophy]
timestamp: 2026-06-18T00:00:00Z
---

個々のスキルの手順の裏にある、繰り返し現れる設計上の判断。これを掴むと「なぜこのスキルはこう書かれているか」が読める。

# 「核」を明示する

多くのスキルが冒頭で **「このスキルの核」** を一文で宣言する。核とは、**機械的なコマンドでは埋められない判断**の所在を指す。

- `gh-release`: 「バージョンの決定とノートの生成という、機械的なコマンドでは埋められない判断がこのスキルの核」
- `gh-pr-create` / `gh-merge`: 差分全体を読んでタイトル・本文（squash メッセージ）を**合成**することが核。
- `concurrent-dev`: 開発を Subagent に委譲しつつ、一貫性を守るレビュー・マージを自分が担うことが核。
- `okf-knowledge`: 「何を・どの粒度で concept にするか」の判断が核。

書き手への含意: スキルは「手順の列挙」で終わらせず、**どこに思考を集中すべきか**を読み手（実行する Agent）に教える。

# 合成主義 ── パススルーしない

入力をそのまま流用せず、**全体を読んで出力を組み立て直す**のが一貫した態度。

- `gh-pr-create` は `gh pr create --fill` を使わない。中間コミットの雑なメッセージを流用せず、差分全体からタイトル・本文を合成する。
- `gh-merge` の squash は `--subject` を自分で組み、`--body ""` で過程のコミットメッセージ（"WIP", "fix typo"）を混入させない。
- `gh-release` のノートも最終的な変更だけを反映し、過程は捨てる。
- コミットメッセージは単一行 + conventional-commit 風 prefix で統一（[git 規律](/this-repo/external-action-safety.md) 参照）。

# アクションスキルの共通骨格

外部に作用するスキル（gh-*、release など）はほぼ同じ流れを踏む。新規スキルもこの骨格に乗せると一貫する。

1. **ガードと前提確認** — 依存ツールの有無・対象が適用範囲か（[ツール検出とフォールバック](/this-repo/tool-gating-and-fallbacks.md)）
2. **コンテキストの収集** — 差分・ログ・テンプレートを読む
3. **合成** — タイトル・本文・バージョン等を組み立てる
4. **確認** — 実行前にユーザーへ提示して了承を取る（[外向き操作の安全則](/this-repo/external-action-safety.md)）
5. **実行**
6. **後処理** — 一時ファイルの片付け・結果（URL 等）の報告

# スキルは合成される単位

スキルどうしが処理を引き渡し合う。一枚岩の巨大スキルを避け、小さなスキルの連携で大きな仕事をこなす。

- `git-init` はリモート作成を `gh-init` に委譲する。
- `concurrent-dev` はコミットを `git-commit` の規約に従わせ、PR 化は `gh-pr-create` に渡す（「push・PR 作成はしない」と明示）。

この姿勢は Agent Skills 公式の「compose capabilities」「structure for scale」と整合する（[ベストプラクティス](/agent-skills/authoring-best-practices.md)）。

# Citations

[1] `skills/gh-release/SKILL.md`, `skills/gh-pr-create/SKILL.md`, `skills/gh-merge/SKILL.md`, `skills/concurrent-dev/SKILL.md`, `skills/okf-knowledge/SKILL.md`, `skills/git-init/SKILL.md` の本文。
[2] 公式の設計原則: [スキル執筆のベストプラクティス](/agent-skills/authoring-best-practices.md)
