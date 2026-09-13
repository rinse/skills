---
name: gh-release
description: Cut a release. Decide the next semantic version from the diff since the last tag, write release notes, and create an annotated tag (optionally a GitHub Release). Use when asked to release, tag, or bump the version (リリースして, バージョンを上げて, cut a release).
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# GitHub Release

最後のリリース以降の差分から次のセマンティックバージョンを判断し、リリースノートを合成して注釈付きタグ（任意で GitHub Release）を作るスキルです。バージョンの決定とノートの合成が核です。

バージョンは Semantic Versioning 2.0.0。タグは既定で `v` 無しの `X.Y.Z`（初回は `0.1.0`）だが、既存タグがあればその規約（prefix の有無）に合わせる。

## 前提

- git リポジトリであること。GitHub Release も作る場合だけ `gh` が要る（無ければ導入を提案する。GitHub MCP があればそれで代替してよい）。
- 次の状態は黙って進めず、確認時に併せて提示する: デフォルトブランチ以外に居る、未コミットの変更がある（タグに含まれない）、`git fetch origin <branch>` 後に `HEAD..origin/<branch>` が空でない（origin より遅れている）。

## 前バージョンの特定

HEAD から到達可能なタグの中でセマンティックバージョンとして最大のものを前バージョン `<prev>` とする。リポジトリ全体の最大タグと食い違う（別ブランチのリリース系列がある）場合は、どちらを前バージョンとするかユーザーに確認する。到達可能なタグが無ければ初回リリースで `0.1.0`。

```
git tag --merged HEAD --sort=-version:refname
git tag --list --sort=-version:refname
```

`git log <prev>..HEAD` が空なら切るべきバージョンは無い。その旨を伝えて終了する。

## コンテキストの収集

ログは自分で読み、トークンを食う差分の読解は Haiku の Subagent に委譲して報告を受ける。Subagent には事実の抽出だけを求め、bump 種別は決めさせない。

- 指示: `git -P diff <prev>..HEAD` を読み、変更を「機能追加 / 挙動変更 / バグ修正 / 内部リファクタ / ドキュメント・テストのみ」に分類して利用者目線で要約する。後方互換を壊しうる変更（公開 API の削除・シグネチャ変更、設定・データ形式の非互換、サブコマンドの削除等）はファイル・関数名付きで列挙し、無ければ「無し」と明記する。
- 報告だけで破壊的変更の有無に確信が持てなければ、該当ファイルの差分を `git -P diff <prev>..HEAD -- <path>` で自分で確認する。

## バージョンの決定

ログと報告を突き合わせ、変更全体のうち最も大きい変化で bump 種別を決める。コミットの prefix は手がかりに過ぎず、最終判断は差分の実体に基づく。

| 種別 | 目安 |
|------|------|
| major | 後方互換を壊す変更（`feat!` や `BREAKING CHANGE` も手がかり） |
| minor | 後方互換を保つ機能追加 |
| patch | バグ修正・内部改善・ドキュメントやテストのみ |

- 上げた桁より下位は 0 に戻す（minor なら `1.4.2 → 1.5.0`）。
- 前バージョンが `1.0.0` 未満なら、破壊的変更があっても major は上げず minor を上げる。確認時にその旨を明示する。
- ユーザーが種別・バージョン・プレリリース（`1.0.0-beta.0` 等）を指定していればそれを優先する。

## リリースノート

利用者目線で、最終的な変更だけをまとめる（"fix typo"、"WIP"、"address review" のような過程は含めない）。`### Added` / `### Changed` / `### Fixed` の該当する節だけを書き、破壊的変更があれば **Breaking changes** を最上部に立てて移行方法も書く。`CHANGELOG.md` があればその書式に合わせ、追記まで行うか（コミットが要る）を確認する。

## 確認と作成

タグと Release は共有され取り消しづらい操作なので、`<prev> → <next>` と bump 種別、その根拠（例:「公開関数 `foo` のシグネチャ変更 → 破壊的だが 0.x のため minor」）、ノート本文、何を作るか（タグのみ / タグ + Release）を提示して了承を得てから実行する。

注釈付きタグで作る（git-bump 系のツールが注釈付きタグを読むため）。ノートはファイルに書き、1 行目をタグの要約、空行を挟んで本文にする。CHANGELOG を更新してコミットした場合は、そのコミットにタグを打つ。

```
git tag -a <next> -F notes.md
git push origin <next>
```

push は一度試し、認証などで失敗したら繰り返さずユーザーに依頼する。

GitHub Release を希望された場合は、タグが push 済みであることを確認してから `gh release create <next> --title "<next>" --notes-file notes.md`。プレリリースなら `--prerelease`、過去バージョンの後追いなら `--latest=false`、`--draft` は明示されたときだけ。

作成したタグ名と、Release を作った場合はその URL を報告する。
