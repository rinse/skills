---
name: cleanup
description: Run cleanup-speculation, cleanup-tests, cleanup-comments, and cleanup-docs in order, each in a fresh subagent, then review the result and run tests. Use only when the user explicitly asks to run traceless or all cleanups (traceless して, 全部クリーンアップして).
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---
四つの cleanup スキルを対象ファイルに順に適用し、結果を確認してユーザーに報告します。

## 対象

ユーザーがパスを指定していればそれを対象にします。
指定が無ければ `git status --porcelain --untracked-files=all` に出る変更ファイルを対象にします。
どちらも無ければ、対象が無い旨を伝えて終わります。

開始前に対象ファイルをスクラッチ領域にコピーしておきます。
対象に元から未コミットの変更がある場合でも、完了後にクリーンアップによる変更だけを比較できるようにするためです。

## 実行

speculation → tests → comments → docs の順に、一つずつ `general-purpose` の Subagent を起動します。
前の Subagent が完了してから次を起動します。
編集権限の無い読み取り専用の種別や、会話を引き継ぐ fork は使いません。
投機的なコードを先に削ると、それに付随するテストやコメントが消え、後段が精査する量が減るためです。

各 Subagent には次だけを渡します。
会話の経緯や差分は渡しません。
cleanup スキルは完成したコードだけを読んで判断する前提で、変更の経緯を知ると残滓を残滓と認識できなくなるためです。

- 読むべきスキル: このスキルのディレクトリと同階層にある `cleanup-<name>/SKILL.md`（絶対パスで渡す）
- 対象ファイルの一覧
- 制約: リストアップした候補は実際に適用する。振る舞いは変えない。コミットしない。
- 報告: 適用した変更と、判断に迷って適用しなかった候補

## 確認と報告

四つが終わったら、対象ごとにコピーと現在のファイルを `git diff --no-index` で比較し、クリーンアップによる変更を読みます。
プロジェクトの test / build / lint を流します。
失敗した場合は、原因になったクリーンアップの変更を戻すか直し、緑にしてから報告します。

報告には、スキルごとの変更の要約、戻した変更とその理由、適用しなかった候補を含めます。
コミットはしません。
