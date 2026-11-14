#!/usr/bin/env python3
"""concurrent-dev の計画 (plan.json) を機械的に検査し、通れば審査用チェックリストを出力する。

使い方: python3 check_plan.py <plan.json>   (自己テスト: python3 check_plan.py --selftest)
終了コード: 0 = 検査を通過（標準出力にチェックリスト）, 1 = 問題あり（標準出力に問題の一覧）
"""
import json
import sys

MODELS = {"haiku", "sonnet", "opus"}

# 審査 Subagent が判定する観点。機械的に決められないものだけを置く。
ISSUE_CHECKS = [
    ("criteria-complete", "依頼の受け入れ条件が、漏れも改変もなく criteria に写されている"),
    ("constraints-complete", "依頼の制約が、漏れも改変もなく constraints に写されている"),
    ("no-open-question", "人間が決めないと実装方針が定まらない曖昧さが依頼に残っていない"),
]
TASK_CHECKS = [
    ("satisfies-criteria", "detail のとおり実装すれば、covers の受け入れ条件を実際に満たせる"),
    ("in-scope", "受け入れ条件を満たすのに必要な作業だけからなる"),
    ("files-valid", "files の既存ファイルは実在し、新規ファイルの置き場所は既存の構成に沿う"),
    ("model-fits", "model が「モデル割り当ての目安」と釣り合っている"),
]
CONSTRAINT_CHECK = ("constraint-kept", "どのタスクもこの制約に違反しない")


def lint(plan):
    out = []
    tasks = plan.get("tasks", [])
    ac = [c["id"] for c in plan.get("criteria", [])]
    by_id = {t["id"]: t for t in tasks}
    if not ac:
        out.append("受け入れ条件がない")
    if not tasks:
        out.append("タスクがない")
    for key in ("id", "branch"):
        vals = [t[key] for t in tasks]
        dup = sorted({v for v in vals if vals.count(v) > 1})
        if dup:
            out.append(f"タスクの {key} が重複: {', '.join(dup)}")
    for a in ac:
        if not any(a in t["covers"] for t in tasks):
            out.append(f"{a} を担うタスクがない")
    for i, t in enumerate(tasks):
        if t["model"] not in MODELS:
            out.append(f"{t['id']} の model が不正: {t['model']}")
        if not t["covers"]:
            out.append(f"{t['id']} はどの受け入れ条件にも対応しない")
        for a in t["covers"]:
            if a not in ac:
                out.append(f"{t['id']} の covers に未定義の {a}")
        if not t["files"]:
            out.append(f"{t['id']} に変更ファイルがない")
        if not t.get("detail"):
            out.append(f"{t['id']} に detail がない")
        for d in t["dependsOn"]:
            if d not in by_id:
                out.append(f"{t['id']} の依存先 {d} が存在しない")
            elif by_id[d]["wave"] >= t["wave"]:
                out.append(f"{t['id']}（波{t['wave']}）は依存先 {d}（波{by_id[d]['wave']}）より後の波でなければならない")
        for u in tasks[i + 1:]:
            shared = sorted(set(t["files"]) & set(u["files"]))
            if u["wave"] == t["wave"] and shared:
                out.append(f"{t['id']} と {u['id']} が同じ波で同じファイルを変更: {', '.join(shared)}")
    return out


def checklist(plan):
    rows = [(cid, "依頼", text) for cid, text in ISSUE_CHECKS]
    for t in plan["tasks"]:
        rows += [(cid, t["id"], text) for cid, text in TASK_CHECKS]
    rows += [(CONSTRAINT_CHECK[0], c["id"], CONSTRAINT_CHECK[1]) for c in plan.get("constraints", [])]
    lines = ["| # | 観点 | 対象 | 確かめること | 判定 | 根拠 |", "|---|---|---|---|---|---|"]
    lines += [f"| {n} | {cid} | {target} | {text} | | |" for n, (cid, target, text) in enumerate(rows, 1)]
    return "\n".join(lines)


def selftest():
    def task(tid, **over):
        base = dict(id=tid, title=tid, detail="d", branch=tid.lower(), model="sonnet", dependsOn=[], wave=1,
                    covers=["AC1"], files=[f"{tid}.js"], tdd=True)
        return {**base, **over}

    good = {
        "criteria": [{"id": "AC1", "text": "a"}, {"id": "AC2", "text": "b"}],
        "constraints": [{"id": "C1", "text": "c"}],
        "tasks": [task("T1"), task("T2", covers=["AC2"], dependsOn=["T1"], wave=2)],
    }
    assert lint(good) == []
    assert checklist(good).count("\n") == 1 + 3 + 4 * 2 + 1  # ヘッダ2行 + 依頼3 + タスク4×2 + 制約1
    # 担い手のない AC2、同じ波への依存、同じ波でのファイル重複
    bad = {**good, "tasks": [task("T1", dependsOn=["T2"]), task("T2", files=["T1.js"])]}
    assert len(lint(bad)) == 3, lint(bad)
    assert lint({"criteria": [], "tasks": []}) == ["受け入れ条件がない", "タスクがない"]
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--selftest":
        selftest()
        sys.exit(0)
    with open(sys.argv[1], encoding="utf-8") as f:
        plan = json.load(f)
    problems = lint(plan)
    if problems:
        print("\n".join(f"- {p}" for p in problems))
        sys.exit(1)
    print(checklist(plan))
