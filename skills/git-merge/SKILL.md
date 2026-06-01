---
name: git-merge
description: Use this skill when merging code via the `gh` command, GitHub MCP tools, or `git merge`. Also triggers on phrases like "squash and merge", "merge this PR", "merge the branch", or any merge operation. Provides instructions on how to write merge commit messages depending on the merge strategy (squash vs. merge commit).
---

# Git Merge

## Squash merge の場合

squash merge では、複数のコミットを一つにまとめるため、コミットメッセージは**最終的な変更内容のみ**を反映したものにしてください。修正やレビューの過程（"fix typo", "address review comments", "WIP" など）は含めないこと。

### `git merge --squash <branch>` の場合

`git merge --squash` はステージングのみで commit は作成しません。その後 `git commit` を実行するので、そこで適切なメッセージを書いてください。

```
git merge --squash <branch>
git commit -m "feat: add CSV export to dashboard"
```

### `gh pr merge --squash` の場合

リポジトリの設定によっては PR の全コミットメッセージが連結されることがあります。設定に依存せず確実にクリーンなメッセージにするため、`--subject` (`-t`) と `--body` (`-b`) で明示的に上書きしてください。

```
gh pr merge <PR番号> --squash --subject "feat: add CSV export to dashboard" --body ""
```

- `--subject`: squash commit のタイトル（一行）
- `--body ""`: 不要な過程のコミットメッセージを含めないよう空にする

**メッセージの書き方:**

- 変更の目的・結果を端的に伝える一行メッセージ
- 例: `feat: add CSV export to dashboard`
- 例: `fix: resolve null pointer in user authentication`
- 例: `refactor: simplify database connection pooling`

## Merge commit を残す場合

merge commit のコミットメッセージは**デフォルトのまま**にしてください。

- `git merge` が自動生成するメッセージ（例: `Merge branch 'feature/foo' into main`）を変更しない
- `gh pr merge --merge` 等で GitHub が生成するデフォルトメッセージもそのまま使う
