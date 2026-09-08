#!/usr/bin/env python3
"""Stop hook: after a turn that edited files, block once and ask for a clean-rewrite pass."""
import json, os, subprocess, sys, time

inp = json.load(sys.stdin)
cwd = inp.get("cwd") or os.getcwd()
state_dir = os.path.join(os.path.expanduser("~"), ".claude", "clean-rewrite-hook")
os.makedirs(state_dir, exist_ok=True)
state = os.path.join(state_dir, inp["session_id"])

if inp.get("stop_hook_active"):          # rewrite pass just finished: remember and let it stop
    open(state, "w").write(str(time.time()))
    sys.exit(0)

since = float(open(state).read()) if os.path.exists(state) else 0.0


def epoch(ts):                            # "2026-09-06T01:02:03.456Z" -> epoch seconds
    return time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone


files = set()
for line in open(inp["transcript_path"]):   # edits made through Edit/Write tools
    try:
        d = json.loads(line)
    except ValueError:
        continue
    if d.get("timestamp") and epoch(d["timestamp"]) < since:
        continue
    content = (d.get("message") or {}).get("content")
    for b in content if isinstance(content, list) else []:
        if b.get("type") == "tool_use" and b.get("name") in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
            p = b["input"].get("file_path") or b["input"].get("notebook_path")
            if p and os.path.abspath(p).startswith(cwd + os.sep):
                files.add(os.path.relpath(p, cwd))
try:                                        # edits made via shell (sed, heredoc): dirty files touched after `since`
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                         cwd=cwd, capture_output=True, text=True).stdout
    for l in out.splitlines():
        p = l[3:].split(" -> ")[-1]
        full = os.path.join(cwd, p)
        if os.path.isfile(full) and os.path.getmtime(full) >= since:
            files.add(p)
except OSError:
    pass

if not files:
    sys.exit(0)
print(json.dumps({"decision": "block", "reason":
    "このターンで編集したファイルに編集痕（文章の残滓、コードの互換経路や旧概念を指す名前）が残っていないか、"
    "clean-rewrite スキルを呼び出して点検し、必要なら書き直してください。対象: " + ", ".join(sorted(files))
    + "。振る舞いは変えないこと。"}, ensure_ascii=False))
