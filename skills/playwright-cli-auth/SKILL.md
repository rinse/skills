---
name: playwright-cli-auth
description: Automates browser authentication and login flows using Playwright. Use when a website requires a logged-in session to complete a task - such as accessing dashboards, user accounts, or any page behind a login wall or any task where a persistent session must be established before proceeding.
allowed-tools: Bash(playwright-cli:*)
metadata:
  author: rinse <rinse418@gmail.com>
  license: MIT
  source: https://github.com/rinse/skills
---

Make sure to read the playwright-cli skill as well.

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

## ステップ 0: 既存セッションの確認

ユーザーにログインを頼む前に、すでに有効なセッションがないかを確認します。
毎回 headed ブラウザを起動してユーザーを煩わせないよう、まず headless で試みます。

```bash
# 保存済み状態ファイルがある場合は試してみる
playwright-cli open
playwright-cli state-load auth.json   # ファイルがなければ次のステップへ
playwright-cli goto 'https://example.com/dashboard'
playwright-cli snapshot
playwright-cli close
```

スナップショットを見てログイン後のページが表示されていれば、再ログインは不要です。
ログインページにリダイレクトされた場合は、以下の手順に進みます。

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

ログイン完了後、`state-save` で認証状態を `auth.json` に書き出します。
これにより次回は headless でセッションを引き継げます。

```bash
playwright-cli state-save auth.json
```

### 5. headful ブラウザを閉じ、headless で続行する

```bash
playwright-cli close

# headless で再起動して認証状態を読み込む
playwright-cli open
playwright-cli state-load auth.json
playwright-cli goto 'https://example.com/dashboard'
playwright-cli snapshot
```

スナップショットでログイン後のページが確認できれば成功です。
ユーザーから headful を使い続けるよう指示がある場合は `playwright-cli open --headed --persistent` を代わりに使います。
