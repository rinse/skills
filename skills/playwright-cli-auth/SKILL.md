---
name: playwright-cli-auth
description: Have the user log in themselves in a temporarily headful browser, then continue headless with the saved session. Use whenever a task needs an authenticated web session — dashboards, account pages, anything behind a login wall. Triggers on phrases like "ログインして", "ログインが必要", "log in to the site". Never asks the user for credentials.
allowed-tools: Bash(playwright-cli:*)
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# Playwright CLI Auth

playwright-cli スキルが環境で利用可能なら、先にそちらも読むこと。

## 概要

認証情報やログインセッションが必要になった場合、あなたはログインに必要な資格情報をユーザーに求めることはできません。
なぜならユーザーの資格情報は決して他人に漏らしてはいけないものであり、生成 AI を運用している企業に対して送信するわけにはいかないためです。

そのため、あなたはログインに必要な資格情報をユーザーに要求する代わりに、その時だけ headful なブラウザを表示して、ユーザーにログイン操作を行うことを要求し、取得したログインセッションを利用してその後の操作を行います。

## セッションの保存戦略

playwright-cli には 2 種類のセッション保持方法があります。

| 方法 | コマンド | 用途 |
|------|----------|------|
| 永続プロファイル | `open --persistent` | 同じマシンで継続的に使う場合。プロファイルにセッションを保持 |
| 状態ファイル | `state-save` / `state-load` | セッションをファイルに書き出して headless セッションへ引き継ぐ |

基本的には **両方を組み合わせる** のが確実です。
headful で `--persistent` ログイン → `state-save` でファイルにバックアップ → headless 再起動後に `state-load` で読み込み。

### 認証状態ファイル（auth.json）の安全な取り扱い

- 状態ファイルはセッショントークンを平文で含む機微なファイルです。
- **リポジトリの作業ツリーには置かない** でください。セッション用のスクラッチ領域があればそこに、無ければ `/tmp` などの一時領域にパスを明示して保存します（例: `playwright-cli state-save "${SCRATCH:-/tmp}/auth.json"`）。誤って git にコミットされる事故を防ぐためです。
- タスク完了後は、状態ファイルを残すか消すかを判断してください。継続して利用する予定が無ければ削除します。残す場合は、その保存場所と機微な情報であることをユーザーに伝えてください。

## ステップ 0: 既存セッションの確認

ユーザーにログインを頼む前に、すでに有効なセッションがないかを確認します。
毎回 headed ブラウザを起動してユーザーを煩わせないよう、次の順に試みます。

1. まず headless + 永続プロファイル（`--persistent`）で対象ページにアクセスし、スナップショットを確認します。

    ```bash
    playwright-cli open --persistent
    playwright-cli goto 'https://example.com/dashboard'
    playwright-cli snapshot
    ```

2. ログインできていなければ、保存済みの状態ファイルがある場合に読み込んで再確認します。

    ```bash
    playwright-cli state-load "${SCRATCH:-/tmp}/auth.json"   # ファイルがなければ次のステップへ
    playwright-cli goto 'https://example.com/dashboard'
    playwright-cli snapshot
    ```

3. どちらもログインページにリダイレクトされる場合は、以下の「ステップ 1–5」に進みます。

いずれかの時点でログイン後のページが確認できれば、再ログインは不要です。`playwright-cli close` でブラウザを終了し、以降の操作を続けてください。

## ステップ 1–5: ユーザーにログインを依頼する手順

既存セッションが使えない場合にのみ、以下を実施します。

### 1. headful ブラウザを起動する

`--headed` で画面を表示し、`--persistent` でプロファイルにセッションを保持します。

```bash
playwright-cli open --headed --persistent
```

### 2. ログインページに遷移する

```bash
playwright-cli goto 'https://example.com/login'
```

### 3. ユーザーにログイン操作を依頼する

なぜログインが必要なのかを説明し、2FA（二段階認証）や OAuth のリダイレクト画面が表示される場合もあることを伝えます。

```
○○を行うにあたり、××へのログインが必要です。
ブラウザウィンドウが開いているので、ログインが完了したら報告してください。
二段階認証が必要な場合は、その操作も行ってください。

[Choice]
1. ログインが完了しました。
2. 別の手段を検討してください。
```

### 4. 認証状態をファイルに保存する

ログイン完了後、`state-save` で認証状態をファイルに書き出します。
これにより次回は headless でセッションを引き継げます。
状態ファイルはセッショントークンを含む機微な情報なので、リポジトリの作業ツリーではなくスクラッチ領域や `/tmp` などに保存してください（詳細は前述の「認証状態ファイルの安全な取り扱い」を参照）。

```bash
playwright-cli state-save "${SCRATCH:-/tmp}/auth.json"
```

### 5. headful ブラウザを閉じ、headless で続行する

```bash
playwright-cli close

# headless で再起動して認証状態を読み込む
playwright-cli open
playwright-cli state-load "${SCRATCH:-/tmp}/auth.json"
playwright-cli goto 'https://example.com/dashboard'
playwright-cli snapshot
```

スナップショットでログイン後のページが確認できれば成功です。
ユーザーから headful を使い続けるよう指示がある場合は `playwright-cli open --headed --persistent` を代わりに使います。

タスクが完了したら、状態ファイルを残すか消すかを判断してください。継続して利用する予定が無ければ削除し、残す場合は保存場所と機微な情報であることをユーザーに伝えてください。
