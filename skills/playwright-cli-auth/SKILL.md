---
name: playwright-cli-signin
description: Automates browser authentication and login flows using Playwright. Use when a website requires a logged-in session to complete a task - such as accessing dashboards, user accounts, or any page behind a login wall or any task where a persistent session must be established before proceeding.
allowed-tools: Bash(playwright-cli:*)
---

Make sure to read the playwright-cli skill as well.

## 概要

認証情報やログインセッションが必要になった場合、あなたはログインに必要な資格情報をユーザーに求めることはできません。
なぜならユーザーの資格情報は決して他人に漏らしてはいけないものであり、生成 AI を運用している企業に対して送信するわけにはいかないためです。
また生成 AI を運用する企業も、通常は個人情報や認証情報などの取り扱いに注意が必要な情報は入れてはいけないと規約で取り決めています。

そのため、あなたはログインに必要な資格情報をユーザーに要求する代わりに、その時だけ headful なブラウザを表示して、ユーザーにログイン操作を行うことを要求し、取得したログインセッションを利用してその後の操作を行います。

## ユーザーにログイン操作を代行させる手順

以下はユーザーにログイン操作を代行してもらい、ログイン後の環境を得るための、具体的なステップ・バイ・ステップ手順です。

1. ブラウザを open します
    `--headed` はユーザーがログイン操作を行うため、
    `--persistent` はログインセッションの保存のために必要です。

    ```bash
    playwright-cli open --headed --persistent
    ```
2. ログインページに遷移します
    ```bash
    playwright-cli goto 'https://example.com'
    ```
3. ユーザーにログイン操作を要求します
    - ユーザーになぜログインが必要なのかを説明します。

    Example:
    ```
    ○○を行うにあたり、××へのログインが必要です。
    ブラウザウィンドウを表示したので、ログインが完了したら報告してください。

    [Choice]
    1. ログインが完了しました。
    2. 別の手段を検討してください。（ユーザーの自由入力による代替案の提案）
    ```
4. 認証情報を保存します
    認証情報の保存戦略はウェブサイトによって異なります。
    `playwright-cli --help` の Storage セクションか playwright-cli Skill を参照して、
    適切な `playwright-cli` コマンドを通じてどこに認証情報が保存されているかを調査し、
    また認証情報を保存します。
    通常は `playwright-cli --persistent state-save` を最初に試すべきです。

    > state-save [filename]       saves the current storage (authentication) state to a file
5. headful ブラウザを閉じます
    `playwright-cli close` コマンドでブラウザを閉じます。
    引き続き `playwright-cli` でブラウザ操作を行いたい場合は、
    `playwright-cli open --persistent` コマンドを実行して headless なブラウザを開きなおし、操作を続行します。
    ユーザーから headful ブラウザを使うよう指示がある場合はこの限りではありません。

