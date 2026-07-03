---
name: inspect-web-traffic
description: Capture the network traffic behind a browser action and build a one-shot script that reproduces it. Use this skill to inspect or reproduce a web request or API call, triggerd by phrases such as "ブラウザの通信を解析して", "ブラウザ操作を curl で再現して", "ブラウザ操作をスクリプト化して", or anything like that.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

Make sure to read the playwright-cli skill as well.

## このスキルの核

ブラウザ操作の裏で流れる通信を捕捉し、その操作を**再現するワンショットスクリプト**（既定は curl、指示があれば TypeScript / Python）を作る。

核は**捕捉の機械作業ではなく合成の判断**にある。捕捉した何十本ものリクエストから、

1. **その操作を構成するリクエストを選ぶ**（1 本とは限らない。認証 → トークン取得 → 本命 API のように連なることがある）
2. **ノイズを削る**（`sec-ch-ua-*`, `referer`, `user-agent` など再現に不要なヘッダを落とす）
3. **秘密情報をパラメータ化する**（Cookie・`Authorization`・CSRF トークンを環境変数やプレースホルダに逃がし、値をそのまま埋め込まない）
4. **リプレイで再現を検証する**（生成したスクリプトを実行し、ブラウザが得たレスポンスと突き合わせる）

`playwright-cli request N` の出力を curl にそのまま書き写すのは**アンチパターン**。全体を読んで組み立て直す（[合成主義](../../knowledge/this-repo/skill-design-philosophy.md)）。

## 前提の確認

- `command -v playwright-cli` — 存在しない場合はスキルを終了してユーザーに判断を仰ぐ。
- `command -v curl`（既定の出力先）、TypeScript/Python 出力なら `node` / `python3`、ユーザーが他のスクリプトを要望したときにはそれに対応するスクリプト言語。
- エスカレーション経路のみ: `command -v google-chrome-stable`（または `google-chrome`）。headful 表示に `DISPLAY`（WSL は WSLg の `:0`）。

## 経路の選択 ── まず標準、必要ならエスカレーション

### 標準経路: playwright-cli 単体で捕捉する

自動化検知・captcha・ログインのどれも要らない対象は、これで足りる。

```bash
playwright-cli open
playwright-cli goto '<操作の起点 URL>'
# ここでユーザーの操作を再現する（click / fill / press など）。
# 目的の操作を実行した「後」に通信を一覧する。
playwright-cli requests --static      # 番号付きで一覧（静的リソースも含める）
playwright-cli request <N>            # 1 本の全体（ヘッダ・ボディ・レスポンス）
playwright-cli request-headers <N>
playwright-cli request-body <N>
playwright-cli response-body <N>      # ブラウザが得た正解。リプレイの照合先
```

**アタッチ／キャプチャ境界（重要）**: `requests` に出るのは playwright がページを追跡し始めた「後」に発火したリクエストだけ。`goto` やユーザー操作より前に完了した通信は一覧に出ない。標準経路では起点 URL を `goto` してから操作するのでほぼ問題ないが、「見えるはずの通信が出ない」ときはこの境界を疑う。エスカレーション経路では netlog がこの穴を埋める。

### エスカレーション経路: 実 Chrome を CDP + netlog で立ち上げてアタッチ

以下のいずれかが分かったら標準経路を諦め、システムの Chrome を **1. 明示プロファイル 2. CDP ポート 3. netlog 有効** で起動し、そこへ `playwright-cli attach --cdp` でアタッチする。

- 自動化ブラウザとして**検知**されている（`navigator.webdriver` 判定、headless UA 弾き、Cloudflare 等）
- **captcha** が出る
- **ログイン／認証情報**が要る

これで得られるもの:

- **検知回避**: ユーザーの本物の Chrome（実 UA・実プロファイル・実フィンガープリント）に後付けで繋ぐ。最も効くのは構造そのもの ── **機微な局面（初回ロード・ログイン・captcha）ではそもそも自動化クライアントが未接続**で、ユーザーが素の Chrome を操作し、playwright はその後で繋ぐだけ。加えて **headful + 実プロファイル**が効く。playwright 自前起動は既定で headless になり、`HeadlessChrome` UA や headless 固有のフィンガープリント（plugins/WebGL 等）で弾かれやすいが、この経路は headful の実 Chrome とユーザーのプロファイル（Cookie・履歴・拡張）で通る。※ `navigator.webdriver` は**この経路でも playwright 自前起動でも `false`**（実測）で差別化要因ではない。
- **ユーザー支援**: 同じウィンドウでユーザーに captcha・ログイン・2FA を解いてもらえる。
- **netlog**: playwright のアタッチ後キャプチャに加え、**セッション全体（アタッチ前の認証フェーズ含む）**を Chrome 自身が記録する完全なフォレンジックログが残る。

手順・フラグ・netlog の扱いは **[references/escalation.md](references/escalation.md)** に分けてある。エスカレーションするときはそちらを開くこと。netlog は再現に必要な Cookie・認証ヘッダを含む `--net-log-capture-mode=IncludeSensitive` を既定に推奨する（既定モードはこれらを伏せ、`Everything` は生バイトまで含み肥大化する）。

## 合成とスクリプト化

捕捉できたら、上の「核」の 1〜3 を実行して 1 本のスクリプトに落とす。既定は **curl**。

```bash
# 例: パラメータ化した curl（トークンは値を埋め込まず環境変数へ逃がす）
TOKEN="${DEMO_TOKEN:?set DEMO_TOKEN}"
curl -sS -X POST 'https://api.example.com/posts' \
  -H 'Content-Type: application/json' \
  -H "X-Demo-Token: ${TOKEN}" \
  -d '{"title":"foo","body":"bar","userId":1}'
```

- Cookie 依存の操作は `-b 'name=value'`（curl）等でセッションを渡す。値はプレースホルダにし、取得元（どのレスポンスの `Set-Cookie` か）をコメントで示す。
- 連鎖する操作は、前段のレスポンスから値を取り出して次段へ渡す形にする（トークンをハードコードしない）。

## リプレイで検証する ── ここまでやって完了

生成したスクリプトを**実際に実行**し、`response-body <N>` で見たブラウザの正解と突き合わせる。

- 一致（同じ実体が返る）→ 再現成功。ユーザーに渡す。
- 401/403/419 等 → 認証・CSRF・オリジン系ヘッダの削りすぎ、またはトークンの期限切れ。削ったヘッダを一つずつ戻して切り分ける。
- 検証できたことと、パラメータ化した秘密情報（何を環境変数にしたか）を明記して報告する。

## 後片付け

- エスカレーションで起動した Chrome は**正常終了**させる（netlog は終了時に flush される。強制 kill だと欠けることがある）。
- netlog・保存済みレスポンスボディ・一時プロファイルは作業ツリーを汚さない場所（スクラッチ領域か `/tmp`）に置き、済んだら消す。**netlog は Cookie・トークンを含み得る**ので特に扱いに注意し、不要になったら削除する。
