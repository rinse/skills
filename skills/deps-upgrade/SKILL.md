---
name: deps-upgrade
description: Use whenever the user asks to upgrade or bump project dependencies. Triggers on "依存を更新", "依存関係を上げて", "パッケージを更新", "upgrade dependencies", "bump deps", "update packages", "npm audit fix". Batches patch/minor together, isolates each major, reads changelogs for real impact, migrates code, verifies with tests before committing per batch.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# Deps Upgrade

プロジェクトの依存パッケージを、changelog を読んで影響を判断しながら安全に更新するスキルです。

**このスキルの核は 2 つの判断です。** (1) **バッチ戦略** ── 何をまとめて上げ、何を単独で上げるか。(2) **changelog から「自プロジェクトへの影響の有無」を読み取る判断** ── 破壊的変更が実際にこのプロジェクトの使用箇所に触れるか。どちらも `npm update` のような機械的なコマンドでは埋まりません。

トークンを食う changelog / リリースノートの読解は、[gh-release](../gh-release/SKILL.md) と同じパターンで Haiku の Subagent に委譲します。Subagent には**事実抽出だけ**を任せます（破壊的変更の列挙、必要な移行作業、自プロジェクトが使っている API との関係）。「上げるか・どう上げるか」の判断は常にオーケストレーター（自分）が行います。

## 全体の流れ

1. ガードと前提確認
2. 現状の棚卸し
3. バッチ計画の合成と確認
4. バッチごとの実行
5. コミット
6. 報告

## 1. ガードと前提確認

- **エコシステムの特定** ── マニフェストとロックファイルから判定します。

  | マニフェスト | ロックファイル | エコシステム / パッケージマネージャ |
  |---|---|---|
  | `package.json` | `package-lock.json` | npm |
  | `package.json` | `yarn.lock` | yarn |
  | `package.json` | `pnpm-lock.yaml` | pnpm |
  | `Cargo.toml` | `Cargo.lock` | cargo |
  | `pyproject.toml`（`[tool.uv]` 等） | `uv.lock` | uv |
  | `pyproject.toml`（`[tool.poetry]`） | `poetry.lock` | poetry |
  | `pyproject.toml` / `requirements.txt` | 無し・`requirements.txt` | pip |
  | `go.mod` | `go.sum` | go modules |
  | `Gemfile` | `Gemfile.lock` | bundler |

  複数のエコシステムが同居するモノレポでは、対象をユーザーに確認します。

- **テスト・ビルド・lint コマンドの特定** ── `package.json` の `scripts`、`Makefile`、CI 設定（`.github/workflows/*`）等から検出します。見つからなければユーザーに尋ねます。
- **テストが無いプロジェクトでは、検証の裏付けが取れない旨を最初にユーザーへ伝え、それでも進めるか確認します。** 進める場合も、後段の確認・報告のたびに「未検証」であることを明記します。

## 2. 現状の棚卸し

古い依存を一覧化し、**direct（自分の manifest に書かれている依存）と transitive（依存の依存）を区別**します。

| エコシステム | 一覧化コマンド例 |
|---|---|
| npm | `npm outdated` |
| yarn | `yarn outdated` |
| pnpm | `pnpm outdated` |
| cargo | `cargo update --dry-run` |
| uv | `uv lock --upgrade --dry-run` |
| poetry | `poetry show --outdated` |
| pip | `pip list --outdated` |
| go | `go list -u -m all` |
| bundler | `bundle outdated` |

セキュリティアドバイザリも合わせて確認します（`npm audit`、`cargo audit`、`pip-audit`、`bundle audit` 等、導入されていれば）。

## 3. バッチ計画の合成と確認

棚卸し結果から更新計画を組み立て、実行前にユーザーへ提示して確認を取ります。

- **patch / minor はまとめて 1 バッチ。** semver を信じて一括で上げますが、後段のテストで裏を取ります。
- **major は 1 つずつ独立のバッチ。** それぞれ changelog の読解と移行作業が必要になるためです。
- **ロックファイルのみの更新（transitive の refresh）は独立のバッチ。** direct の版は変えず、解決結果だけを更新するものは切り分けます。
- **セキュリティアドバイザリの対象は優先**して先に扱います。
- **バージョンが pin されている依存は、理由がある可能性が高いです。** コメント、lockfile 上の固定、Renovate/Dependabot の設定（`renovate.json`, `.github/dependabot.yml` の `ignore` 等）を確認します。pin を外す判断は必ずユーザーに確認し、勝手に外しません。

提示する内容には、各バッチの中身（対象パッケージとバージョン）、バッチに分けた理由、見送り候補（pin・大きすぎる major 等）を含めます。

## 4. バッチごとの実行

各バッチについて、以下の順で進めます。

1. **ベースラインを取る。** 更新前に一度テスト・ビルド・lint を流し、現状が green かを確認しておきます（既存の flaky と更新起因の失敗を切り分けるため）。
2. **更新を実行する**（`npm install <pkg>@<version>` 等、エコシステムに応じたコマンド）。
3. **major の場合は changelog / リリースノートを取得します。** 長い場合は Agent ツールで Haiku の Subagent に委譲します（`subagent_type: "general-purpose"`, `model: "haiku"`）。Subagent には次を指示します。
   - 取得するもの: changelog / リリースノート本文（GitHub Releases、`CHANGELOG.md`、公式ドキュメントの migration guide 等）。
   - 報告してほしいこと（**判断はこちらで行うので、事実抽出だけを求めます**）:
     - 出典 URL。
     - 破壊的変更の列挙（根拠となる API 名・設定項目つき）。
     - 必要な移行手順の要約。
     - 自プロジェクトが実際に使っている API・設定との関係（該当するコード箇所を伝え、影響があるかを照合させる）。
   - bump するかどうかや移行の要否は Subagent に決めさせません。事実報告に徹させます。
4. **報告を受けて移行要否を判断し、必要な移行（コード修正）を行います。** 更新と無関係な改善は混ぜません。
5. **テスト・ビルド・lint を流し、green を確認します。**
   - **赤くなった場合**、まず「更新が原因か既存の flaky か」を切り分けます（手順 1 のベースラインと比較する）。
   - 更新が原因で、かつ移行コストが大きい（設計変更が要る、影響範囲が広い等）場合は、**このバッチを見送り**、理由を記録して報告に残します。
   - テストが無いプロジェクトでの更新は、green であっても「検証できていない」ことを正直に報告し、確信度を下げて伝えます。

## 5. コミット

**1 バッチ = 1 コミット**です。[git-commit](../git-commit/SKILL.md) の規約に従います。

- コミットメッセージは一行。
- 対象ファイルを明示列挙してステージングします（`git add -A` は禁止）。
- メッセージ例: `chore(deps): bump lodash from 4.17.20 to 4.17.21`
- **更新と無関係なリファクタを同じコミットに混ぜません。** 移行に必要な最小のコード修正のみを同居させます。

## 6. 報告

作業の最後に、次を表で報告します。

| パッケージ | 変更前 | 変更後 | 結果 | 備考 |
|---|---|---|---|---|
| 例: lodash | 4.17.20 | 4.17.21 | 更新済み | patch バッチに含めた |
| 例: express | 4.x | 5.x | 見送り | 破壊的変更が大きく移行コスト高。理由: ... |
| 例: foo | 1.2.0 | (pin 継続) | 見送り | バージョンが pin 済み。理由未確認、ユーザー確認待ち |

見送ったものは理由（破壊的変更が大きい、pin されている、テストが赤くなった等）を必ず添えます。テストが無い状態で進めた更新は、確信度が低いことを報告に明記します。

## push・PR 作成はしない

このスキルは push や PR 作成を行いません。ローカルにバッチごとのコミットを積むところまでです。続けるなら [gh-pr-create](../gh-pr-create/SKILL.md) に渡してください。
