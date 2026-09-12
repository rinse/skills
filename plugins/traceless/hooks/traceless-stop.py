#!/usr/bin/env python3
"""Stop hook: after a turn that edited files, run the cleanup-* skills on them, each in its own
headless session (speculation -> tests -> comments -> docs), then block once so the main session reviews."""
import json, os, subprocess, sys, time

if os.environ.get("TRACELESS_CLEANUP"):  # we are one of the cleanup sessions: never recurse
    sys.exit(0)

inp = json.load(sys.stdin)
cwd = inp.get("cwd") or os.getcwd()
state_dir = os.path.join(os.path.expanduser("~"), ".claude", "traceless-hook")
os.makedirs(state_dir, exist_ok=True)
state = os.path.join(state_dir, inp["session_id"])

if inp.get("stop_hook_active"):          # review pass just finished: remember and let it stop
    open(state, "w").write(str(time.time()))
    sys.exit(0)

since = float(open(state).read()) if os.path.exists(state) else 0.0


def epoch(ts):                            # "2026-09-06T01:02:03.456Z" -> epoch seconds
    return time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone


def dirty_files(after):                   # tracked/untracked files modified at or after `after`
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                         cwd=cwd, capture_output=True, text=True).stdout
    for l in out.splitlines():
        p = l[3:].split(" -> ")[-1]
        full = os.path.join(cwd, p)
        if os.path.isfile(full) and os.path.getmtime(full) >= after:
            yield p


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
try:                                        # edits made via shell (sed, heredoc)
    files.update(dirty_files(since))
except OSError:
    pass

if not files:
    sys.exit(0)

targets = ", ".join(sorted(files))
started = time.time()
env = dict(os.environ, TRACELESS_CLEANUP="1")
for skill in ("cleanup-speculation", "cleanup-tests", "cleanup-comments", "cleanup-docs"):
    subprocess.run(["claude", "-p", f"/{skill} 対象を次のファイルに限定する: {targets}。"
                    "リストアップした候補は実際に適用する。振る舞いは変えず、コミットはしない。",
                    "--permission-mode", "acceptEdits"],
                   cwd=cwd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
open(state, "w").write(str(time.time()))

changed = sorted(dirty_files(started))
if not changed:
    sys.exit(0)
print(json.dumps({"decision": "block", "reason":
    "cleanup セッション（speculation → tests → comments → docs）を別セッションで実行し、次のファイルが変更されました: "
    + ", ".join(changed) + "。差分を確認し、test / build / lint を流して、結果をユーザーに報告してください。"},
    ensure_ascii=False))
