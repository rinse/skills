---
name: git-init
description: Initialize a git repository, settle the user name and email its commits will record, and create an empty initial commit. Use when asked to initialize a repository or version control (git init して, リポジトリを初期化して, git init). Does not create the remote itself.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# Git Init

新しい git リポジトリを初期化し、コミットに使う name / email を設定して、空の initial commit を作るスキル。

## スキル固有の判断

このスキル固有の判断は、最初のコミットにどの name / email を記録するかを確定させ、確定するまでコミットを作らないことである。
identity は既存の local 設定、記憶している設定方法、global 設定、ユーザーへの質問のどれからでも決まりうる。誤った author のコミットは、push した後には履歴を書き換えないと直せない。

対象は、依頼でパスが指定されればそのディレクトリ（無ければ作る）、指定が無ければカレントディレクトリとする。

## 親リポジトリの中では入れ子にせず尋ねる

対象に `.git` が無くても、`git rev-parse --show-toplevel` が成功して別のディレクトリを返すなら、対象は親リポジトリの作業ツリーの中にある。
このときは `git init` せずに止まり、親リポジトリのパスを示して、入れ子のリポジトリを作るかを尋ねる。入れ子のリポジトリはまず意図されておらず、作ると親の側から中身が追跡されなくなる。
作ると答えられたら続け、断られたら何も変えずに終える。

## 既存の .git と履歴はそのまま使う

- 対象に `.git` が既にあれば `git init` を飛ばし、その旨を伝えて identity の設定に進む。途中で止まった後の再実行も、この経路で続きから進む。
- 既にコミットがあるリポジトリでは、既存の履歴に空コミットを足さないよう、initial commit を作らずにリモートの章に進む。

## ブランチ名は未設定なら main にする

- 依頼でブランチ名が指定されていれば `git init -b <名前>` にする。
- 指定が無く、`git config --get init.defaultBranch` が値を返せば、`-b` を付けずに git の設定に従う。
- `init.defaultBranch` が未設定なら `git init -b main` にする。未設定の git は master で作り、GitHub の既定の main と食い違う。

## name と email が決まるまでコミットしない

次の順に確かめ、最初に決まったもので進める。

1. 既存の `.git` に local の `user.name` / `user.email` が既にあれば、その値を示し、そのまま使うか変えるかを尋ねる。ユーザーが明示的に設定した値を黙って上書きしないため。ただし、この会話や記憶にある、ユーザーが示した値や方法と一致すれば、尋ねずにその値を使う。再実行のたびに同じ質問を繰り返さないため。
2. identity の設定方法を記憶していれば、尋ねずにその方法で設定する。
3. `git config --global user.name` / `user.email` が揃っていれば、確認せずにその値でコミットし、使った値を報告に書く。push 前の空のルートコミットは author を直しやすく、毎回の確認に見合わない。
4. どれでも決まらなければ、identity をどう設定するかをユーザーに尋ねる。答えは name と email でも、ユーザー独自の方法（プロファイルを切り替えるツールとそのコマンドなど）でもよく、示されたとおりに適用する。name と email が示されたら、`git config user.name` / `user.email` でこのリポジトリの local に書く。global の片方だけが揃っているなら、欠けている方だけを尋ねて local に書く。global に書くと、他のすべてのリポジトリの identity が変わる。

ユーザーから聞いた設定方法は、次回から尋ねずに使えるよう、必要に応じて記憶に保存する。

設定したら、`git config user.name` / `user.email` で値が決まったことを確かめる。設定に失敗したか値が決まらなければ、意図しない name / email でコミットしないよう、コミットに進まずに止まる。失敗内容と、`.git` は作成済みで、再実行すれば `git init` を飛ばして続きから進めることを伝える。

## 既存のファイルは含めず空コミットだけ作る

対象に既存のファイルがあっても何もステージせず、空の initial commit だけを作る。既存のファイルには秘密やビルド成果物が混じりうるので、何をコミットするかは git-commit やユーザーに任せる。`.gitignore` も作らない。`.env` や鍵のように秘密を含みそうな未追跡のファイルがあれば、報告で名前を挙げて警告する。

コミットは、エイリアスではなく次のフルコマンドで実行する。ユーザーの git エイリアスは環境ごとに異なり、意図しないオプションが付きうるため。

```
git commit -m 'initial commit' --allow-empty
```

失敗したら繰り返さず、エラーと上のコマンドを示してユーザーに実行を依頼する。

## リモートは gh-init に任せる

`origin` が無く、依頼や会話でリモートの要否がまだ決まっていなければ、リモートリポジトリを作るかをユーザーに尋ね、作るなら gh-init に委譲する。

- `origin` が既にあれば尋ねない。
- 依頼や会話でリモートを作ると決まっていれば、尋ねずに gh-init に委譲する。作らないと決まっていれば尋ねない。
- 利用できるスキルに gh-init が無ければ尋ねず、リモートは作っていないことを報告に書く。素の `gh repo create` で代替しない。

## 報告して止まる

報告には次を書く。

- `.git` を作ったか、既存のものを使ったか
- ブランチ名
- 適用した name / email と、その出所（既存の local、記憶していた方法、global、ユーザーの回答）
- initial commit のハッシュ、または作らなかった理由
- コミットせずに残した未追跡のファイル
- リモートの結果（gh-init に委譲した、断られた、`origin` が既にある、gh-init が使えない）

途中で止まったときは、止まった理由と、その時点で何ができているかを書く。
