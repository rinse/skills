# エスカレーション経路: 実 Chrome を CDP + netlog で立ち上げてアタッチする

標準経路（playwright-cli 単体）が自動化検知・captcha・ログインで通らないときの手順。
システムの Chrome を **明示プロファイル + CDP ポート + netlog** で起動し、`playwright-cli attach --cdp` でアタッチする。以下のコマンドは実機で検証済み。

## 1. スクラッチ領域を決める

作業ツリーを汚さないよう、セッションのスクラッチ領域（無ければ `/tmp`）に置く。

```bash
WORK="${SCRATCH:-/tmp}/inspect-web-traffic"
mkdir -p "$WORK"
PROFILE="$WORK/chrome-profile"     # 明示プロファイル（ログインセッションがここに残る）
NETLOG="$WORK/netlog.json"
PORT=9222
```

## 2. Chrome を起動する

**headful で起動する**（ユーザーに captcha・ログインを解いてもらうため）。WSL では WSLg のディスプレイを渡す。

```bash
DISPLAY="${DISPLAY:-:0}" google-chrome-stable \
  --remote-debugging-port="$PORT" \
  --user-data-dir="$PROFILE" \
  --log-net-log="$NETLOG" \
  --net-log-capture-mode=IncludeSensitive \
  --no-first-run --no-default-browser-check \
  'about:blank' >"$WORK/chrome.log" 2>&1 &
```

- `--remote-debugging-port` … CDP。ここに playwright を後付けで繋ぐ。
- `--user-data-dir` … **明示プロファイル**。ユーザーが解いたログインがここに永続する。既定プロファイルを指すと稼働中の Chrome と衝突するので、必ず専用ディレクトリにする。
- `--log-net-log` … netlog の出力先。
- `--net-log-capture-mode` … `IncludeSensitive`（Cookie・認証ヘッダを含む＝**再現に必要**。既定モードはこれらを伏せる）。生バイトまで要るなら `Everything`（ファイルが巨大になる。小さなセッションでも数十 MB）。
- `google-chrome-stable` が無ければ `google-chrome`。

CDP が上がったか確認する:

```bash
curl -s "http://localhost:${PORT}/json/version" --max-time 5
```

`webSocketDebuggerUrl` と非 headless の `User-Agent` が返れば OK。

## 3. ユーザーに操作を依頼する

ログイン・captcha・2FA は**あなたの代わりにユーザーが解く**。資格情報を要求してはいけない（playwright-cli-auth スキルと同じ原則）。

```
自動化検知（または captcha / ログイン）に阻まれたため、あなたの Chrome を開きました。
このウィンドウで対象サイトにログイン（captcha があれば解決、2FA も）してください。
その後、解析したい操作を実行する直前で報告してください。

[Choice]
1. ログイン/captcha を解決しました。
2. 別の手段を検討してください。
```

## 4. playwright-cli をアタッチする

ユーザーが認証を終えたら CDP に繋ぐ。

```bash
playwright-cli attach --cdp="http://localhost:${PORT}"
```

以降は `playwright-cli --s=default <command>` で操作する（`attach` が作るセッション名は `default`）。
対象タブを選び、**目的の操作をここで実行**する:

```bash
playwright-cli --s=default tab-list
playwright-cli --s=default tab-select <index>
# 操作を再現（click / fill / press …）。あるいはユーザーに実行してもらう。
playwright-cli --s=default requests --static
playwright-cli --s=default request <N>
playwright-cli --s=default response-body <N>
```

## 5. 二重の記録を使い分ける

| 記録 | 範囲 | 役割 |
|------|------|------|
| **playwright のキャプチャ**（`requests`/`request`） | **アタッチ後**に発火した通信のみ | 構造化されて読みやすい。**スクリプト合成の主たる材料**はこちら |
| **netlog** | Chrome 起動〜終了の**セッション全体**（アタッチ前の認証フェーズ含む） | 完全なフォレンジック記録。playwright が見逃した通信（アタッチ前・別タブ・worker・別コンテキスト）を拾う穴埋め・裏取り |

**なぜ両方要るか**: playwright はアタッチ後の通信しか見ない（検証済み: アタッチ前に読み込んだページは `requests` に出ず、netlog にだけ残る）。目的の操作がアタッチ後なら playwright のキャプチャで十分。だが「認証時に一度だけ飛ぶトークン発行」のようにアタッチ前・別経路で起きる通信は netlog でしか追えない。

## 6. netlog から目的の通信を探す

netlog は有効な JSON だが**そのままスクリプト化には向かない**（イベント種別が数値で、定数辞書 `constants` と突き合わせが要る）。用途は完全性の担保と裏取り。URL 文字列は生で入っているので、まず素朴に grep して当たりを付ける:

```bash
python3 -c "import json; d=json.load(open('$NETLOG')); print('events:', len(d['events']))"
grep -o 'https://[^\"]*api\.example\.com[^\"]*' "$NETLOG" | sort -u | head
```

スクリプトの合成はあくまで playwright の `request <N>` を起点にする。netlog は「playwright に映らなかった 1 本」を復元するときだけ深掘りする（イベントを URL/リクエスト ID で辿り、`constants.logEventTypes` で種別を解決する）。**自動 netlog→curl 変換は約束しない**（パーサを都度組む必要がある）。

## 7. 後始末

```bash
playwright-cli --s=default detach          # ブラウザは閉じない（netlog を flush させたい）
pkill -TERM -f "remote-debugging-port=${PORT}"   # 正常終了 → netlog が完全に書き出される
```

- **正常終了させる**こと。`kill -9` だと netlog の末尾が欠ける。
- `PROFILE` / `NETLOG` は Cookie・トークンを含む。再利用しないなら削除する。ログインを使い回すなら `PROFILE` を残し、netlog だけ消す。
