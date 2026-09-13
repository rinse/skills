# git-profile のインストール

`git-profile` は [rinse/git-profile-rs](https://github.com/rinse/git-profile-rs) で開発されており、GitHub Releases から入れる。

`gh` がある場合:

1. `gh release view --repo rinse/git-profile-rs` でアセット一覧を見る。
2. 実行環境（`uname -sm`）に合うアセットを選ぶ。アセット名はリリースごとに変わりうるので、固定名を仮定せず一覧から選ぶ。
3. `gh release download --repo rinse/git-profile-rs --pattern '<アセット名>' --dir "$(mktemp -d)"` で取得し、形式（tar.gz / zip / 生バイナリ）に応じて展開して、実行ファイルを `$HOME/.local/bin/git-profile` に置く。`$HOME/.local/bin` が PATH に無ければその旨を伝える。

`gh` が無い場合: Rust 環境があれば `cargo install git-profile`。無ければ `gh` の導入を提案するか、グローバル設定で代替する。

導入直後はプロファイルが無いので、ユーザーに name / email を尋ねて `$XDG_CONFIG_HOME`（既定 `~/.config`）の `git-profile/<name>.gitconfig` に `[user] name / email` を書き、`git-profile switch <name>` で適用する。
