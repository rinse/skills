---
name: git-init
description: Initialize a git repository, set the git profile (user name and email), and create an empty initial commit. Use when asked to git init or set up version control in a directory.
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# Git Init

新しい git リポジトリを初期化するスキルです。

1. `git init`。`.git` が既にあればスキップし、その旨を伝えて手順 2 に進む。
2. コミット用の user name / email を設定する。
   - `git-profile`（`command -v git-profile`）があれば `git-profile list` で一覧を出し、複数あればユーザーに選ばせ、一つならそのまま `git-profile switch <name>` で適用する。
   - 無ければ導入を提案する。手順は [references/install-git-profile.md](references/install-git-profile.md)。導入しない場合や導入に失敗した場合は `git config --global user.name` / `user.email` を確認し、欠けていればユーザーに尋ねて設定する。
   - 切り替えや設定に失敗したら、意図しない name / email でコミットしないよう手順 3 に進まずに止まり、失敗内容と、`.git` は作成済みで再実行すれば手順 1 を飛ばして続きから進めることを伝える。
3. 空の initial commit を作る。エイリアスではなくフルコマンドで実行する。既にコミットがあるリポジトリでは、既存の履歴に空コミットを足さないよう作らずに手順 4 に進む。

   ```
   git commit -m 'initial commit' --allow-empty
   ```

   失敗したら繰り返さず、エラーと上のコマンドを示してユーザーに実行を依頼する。

4. リモートリポジトリを作るかユーザーに尋ね、作るなら gh-init に委譲する。
