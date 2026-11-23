# 実 Chrome を起動して CDP でアタッチする

標準経路（playwright-cli 単体）が自動化検知・captcha・ログインで通らないときの手順。
システムの Chrome を専用プロファイル・CDP ポート・netlog 付きで起動し、`playwright-cli attach --cdp` でアタッチする。以下のコマンドは実機で検証済み。

## 1. スクラッチ領域を決める

プロファイルと netlog は Cookie・トークンを含むので、コミットに紛れ込まないよう作業ツリーの外の、セッションの一時領域に置く。
実行ごとに別のディレクトリにする。前回、未検証で残した netlog を上書きしないため。

```bash
WORK="<作業ツリーの外の、セッションの一時領域>/inspect-web-traffic-$(date +%Y%m%d%H%M%S)"
mkdir -p "$WORK"
PROFILE="$WORK/chrome-profile"     # 専用プロファイル（ユーザーのログインがここに残る）
NETLOG="$WORK/netlog.json"
PORT=9222
```

## 2. 空きポートと専用プロファイルで起動する

起動前に、そのポートで何も待ち受けていないことを確かめる。次が何かを返したら、別のポート番号にする。
既存の CDP に繋ぐと無関係なブラウザを操作することになり、後始末の `pkill` でそちらまで止めてしまう。

```bash
curl -s --max-time 2 "http://localhost:${PORT}/json/version"
```

headful で起動する。ユーザーに captcha・ログインを解いてもらうため。WSL では WSLg のディスプレイを渡す。

```bash
DISPLAY="${DISPLAY:-:0}" google-chrome-stable \
  --remote-debugging-port="$PORT" \
  --user-data-dir="$PROFILE" \
  --log-net-log="$NETLOG" \
  --net-log-capture-mode=IncludeSensitive \
  --no-first-run --no-default-browser-check \
  'about:blank' >"$WORK/chrome.log" 2>&1 &
```

- `--remote-debugging-port` … CDP。ここに playwright を後から繋ぐ。
- `--user-data-dir` … 専用プロファイル。ユーザーが普段使うプロファイルは指さない。稼働中の Chrome と衝突するうえ、`IncludeSensitive` の netlog に無関係なサイトの Cookie まで記録されるため。空のプロファイルなので、ログインはユーザーにこの中でしてもらう。
- `--log-net-log` … netlog の出力先。
- `--net-log-capture-mode` … `IncludeSensitive` は Cookie・認証ヘッダを含み、再現に要る。既定のモードはこれらを伏せる。生のバイト列まで要るなら `Everything`（小さなセッションでも数十 MB になる）。
- `google-chrome-stable` が無ければ `google-chrome`。

CDP が上がったか確認する。

```bash
curl -s "http://localhost:${PORT}/json/version" --max-time 5
```

`webSocketDebuggerUrl` と、headless でない `User-Agent` が返れば起動できている。

## 3. ユーザーにログインと captcha を依頼する

ログイン・captcha・2FA はユーザーが解く。資格情報は要求しない。ユーザーの資格情報をエージェントの側に渡さないため。
ユーザーに頼むのはここまでで、目的の操作はアタッチ後にエージェントが行う。

```
自動化検知（または captcha / ログイン）に阻まれたため、専用プロファイルの Chrome を開きました。
このウィンドウで対象サイトにログインし、captcha や 2FA があれば解いてください。
目的の操作はこちらで行うので、ログインが済んだ時点で報告してください。

[Choice]
1. ログイン / captcha を解決しました。
2. 別の手段を検討してください。
```

2 が選ばれたら、起動した Chrome を「7. 後始末」のとおり正常終了させ、`PROFILE` と `NETLOG` の場所を伝え、どの手段に移るかをユーザーと決めるところで止まる。

## 4. アタッチして目的の操作を実行する

ユーザーがログインを終えたら CDP に繋ぐ。

```bash
playwright-cli attach --cdp="http://localhost:${PORT}"
```

以降は `playwright-cli --s=default <command>` で操作する（`attach` が作るセッション名は `default`）。
対象タブを選び、目的の操作をエージェントが実行する。状態を変える操作なら、実行前に SKILL.md の「状態を変える操作は了承を得てから実行する」の了承を取る。ここではユーザーのアカウントで操作するため。

```bash
playwright-cli --s=default tab-list
playwright-cli --s=default tab-select <index>
# 目的の操作を実行する（click / fill / press …）
playwright-cli --s=default requests --static
playwright-cli --s=default request <N>
playwright-cli --s=default response-body <N>
```

操作の途中で再び captcha やログインを求められたら、3 と同じようにユーザーに解いてもらってから続ける。

## 5. 二つの記録を使い分ける

| 記録 | 範囲 | 役割 |
|------|------|------|
| playwright のキャプチャ（`requests` / `request`） | アタッチ後に発火した通信のみ | 構造化されて読みやすい。スクリプト合成の主な材料 |
| netlog | Chrome の起動から終了までのセッション全体（アタッチ前の認証フェーズを含む） | playwright が見逃した通信（アタッチ前・別タブ・worker・別コンテキスト）の穴埋めと裏取り |

playwright はアタッチ後の通信しか見ない（アタッチ前に読み込んだページは `requests` に出ず、netlog にだけ残ることを確認済み）。
目的の操作がアタッチ後なら playwright のキャプチャで足りる。認証時に一度だけ飛ぶトークン発行のように、アタッチ前や別経路で起きる通信は netlog でしか追えない。

## 6. netlog から目的の通信を探す

netlog は有効な JSON だが、そのままスクリプト化には向かない（イベント種別が数値で、定数辞書 `constants` との突き合わせが要る）。URL 文字列はそのまま入っているので、まず grep して当たりを付ける。

```bash
python3 -c "import json; d=json.load(open('$NETLOG')); print('events:', len(d['events']))"
grep -o 'https://[^\"]*api\.example\.com[^\"]*' "$NETLOG" | sort -u | head
```

スクリプトの合成は playwright の `request <N>` を起点にする。netlog を深く読むのは、playwright に映らなかった 1 本を復元するときだけにする（イベントを URL やリクエスト ID でたどり、`constants.logEventTypes` で種別を解決する）。netlog から curl への自動変換は約束しない。パーサをその都度組む必要があるため。

## 7. 後始末

```bash
playwright-cli --s=default detach          # ブラウザは閉じない（netlog を書き出させるため）
pkill -TERM -f "remote-debugging-port=${PORT}"   # 正常終了させ、netlog を最後まで書き出させる
```

- 正常終了させる。`kill -9` だと netlog の末尾が欠ける。
- `PROFILE` と `NETLOG` を消すか残すかは、SKILL.md の「捕捉物は作業ツリーの外に置き済んだら消す」に従う。
