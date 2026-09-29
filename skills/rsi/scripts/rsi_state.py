#!/usr/bin/env python3
"""RSI state machine v2.3: records the reasoning tree, checks traceability,
evidence levels and neutrality, and produces handoff / external review packets.

State file: .rsi_state.json in the current directory (override with RSI_STATE).

  init "<task definition>" [--success "<success criteria>"]
  add <id> <type> "<content>" [options]
      types: branch plan rebuttal example summary synthesis solution
      --parent ID        --sources A,A-X1,E1
      --tag fact|assumption|unknown|inference|preference
      --level L0-L4      evidence level
      --score 5,4,3,3,4  plan score: fit,feasibility,cost,speed,resilience
      --url https://...  required for examples
      --user             marks a plan proposed by the user
  retry <summary id> "<reason>"
  round | status | handoff | check
  export [--patch "<candidate change summary>"]   external review packet for another AI
"""
import argparse
import json
import os
import sys
from datetime import datetime

STATE = os.environ.get("RSI_STATE", ".rsi_state.json")
TYPES = {"branch", "plan", "rebuttal", "example", "summary", "synthesis", "solution"}
TAGS = {"fact", "assumption", "unknown", "inference", "preference"}
LEVELS = {"L0", "L1", "L2", "L3", "L4"}
MAX_DEPTH, MAX_RETRY = 3, 3


def now():
    return datetime.now().isoformat(timespec="seconds")


def load():
    if not os.path.exists(STATE):
        sys.exit("No state file found. Run init first.")
    with open(STATE, encoding="utf-8") as f:
        return json.load(f)


def save(s):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)


def cur(s):
    return s["rounds"][-1]


def of(r, t):
    return [(k, v) for k, v in r["nodes"].items() if v["type"] == t]


def cmd_init(a):
    save({"task": a.task, "success": a.success or "", "created": now(),
          "rounds": [{"round": 1, "nodes": {}, "retries": [], "started": now()}]})
    print(f"[R1] Task definition locked: {a.task}")


def cmd_add(a):
    if a.type not in TYPES:
        sys.exit(f"type must be one of: {' '.join(sorted(TYPES))}")
    if a.tag and a.tag not in TAGS:
        sys.exit(f"--tag must be one of: {' '.join(sorted(TAGS))}")
    if a.level and a.level not in LEVELS:
        sys.exit("--level must be L0-L4")
    if a.id.count(".") + 1 > MAX_DEPTH:
        sys.exit(f"{a.id} exceeds max nesting depth {MAX_DEPTH}; fold it back up")
    if a.type == "example" and not (a.url or "").startswith("http"):
        sys.exit("Examples need a source link: --url https://...")
    score = []
    if a.score:
        try:
            score = [int(x) for x in a.score.split(",")]
        except ValueError:
            score = []
        if len(score) != 5 or not all(1 <= x <= 5 for x in score):
            sys.exit("--score must be five integers 1-5: fit,feasibility,cost,speed,resilience")
    s = load()
    r = cur(s)
    if a.parent and a.parent not in r["nodes"]:
        sys.exit(f"Parent {a.parent} does not exist")
    sources = [x for x in (a.sources or "").split(",") if x]
    missing = [x for x in sources if x not in r["nodes"]]
    if missing:
        sys.exit(f"Unknown sources: {', '.join(missing)}")
    old = r["nodes"].get(a.id)
    r["nodes"][a.id] = {
        "type": a.type, "content": a.content, "parent": a.parent, "sources": sources,
        "tag": a.tag or "", "level": a.level or "", "score": score, "url": a.url or "",
        "user": bool(a.user), "version": (old["version"] + 1) if old else 1, "time": now(),
    }
    save(s)
    extra = f"  {sum(score)}/25" if score else ""
    print(f"[R{r['round']}] {a.id} ({a.type}) v{r['nodes'][a.id]['version']}{extra}")


def cmd_retry(a):
    s = load()
    r = cur(s)
    n = sum(1 for x in r["retries"] if x["target"] == a.target) + 1
    r["retries"].append({"target": a.target, "reason": a.reason, "n": n, "time": now()})
    save(s)
    print(f"[R{r['round']}] {a.target} retry #{n}: {a.reason}")
    if n > MAX_RETRY:
        print("⚠️ More than 3 retries; suggest /retry 1 to redefine the problem")


def cmd_round(_):
    s = load()
    n = cur(s)["round"] + 1
    s["rounds"].append({"round": n, "nodes": {}, "retries": [], "started": now()})
    save(s)
    print(f"[R{n}] New round started; task definition unchanged: {s['task']}")


def cmd_status(_):
    s = load()
    r = cur(s)
    print(f"Task: {s['task']}\nRound R{r['round']}  nodes {len(r['nodes'])}  retries {len(r['retries'])}")
    for k, v in r["nodes"].items():
        meta = " ".join(x for x in [v["tag"], v["level"],
                                     f"{sum(v['score'])}/25" if v["score"] else "",
                                     "user proposal" if v["user"] else ""] if x)
        src = f" <- {','.join(v['sources'])}" if v["sources"] else ""
        print(f"{'  ' * k.count('.')}- {k} [{v['type']}] {v['content'][:60]}{src}  {meta}")


def cmd_handoff(_):
    s = load()
    r = cur(s)
    print(f"# Handoff R{r['round']}\n\n**Task definition**: {s['task']}")
    if s["success"]:
        print(f"**Success criteria**: {s['success']}")
    for t, title in [("summary", "Summaries"), ("synthesis", "Synthesis"), ("solution", "Solution")]:
        items = of(r, t)
        if items:
            print(f"\n## {title}")
            for k, v in items:
                print(f"- {k}: {v['content']}")
    plans = sorted(of(r, "plan"), key=lambda kv: -sum(kv[1]["score"] or [0]))
    if plans:
        print("\n## Plan scores")
        for k, v in plans:
            sc = v["score"]
            print(f"- {k}{' (user proposal)' if v['user'] else ''}: {v['content']} | "
                  f"{sum(sc)}/25 ({'·'.join(map(str, sc)) if sc else 'unscored'})")
    for t, title in [("rebuttal", "Rebuttals"), ("example", "Real-world examples")]:
        items = of(r, t)
        if items:
            print(f"\n## {title}")
            for k, v in items:
                print(f"- {k}: {v['content']}" + (f" ({v['url']})" if v["url"] else ""))
    if r["retries"]:
        print("\n## Retry log")
        for x in r["retries"]:
            print(f"- {x['target']} #{x['n']}: {x['reason']}")


REVIEW_PROMPT = """You are an independent reviewer. Below is a plan another AI produced using a fixed framework. Check it using only this material and facts you can verify. Do not try to please either side.

Answer each item with a verdict (holds / doubtful / does not hold) and one sentence of reasoning:
1. Does the solution actually answer the task definition?
2. Is the evidence for key conclusions sufficient? Is any assumption treated as fact?
3. Among the rejected plans, is any actually better?
4. Are the real-world examples genuine, and do they support their conclusions? (Check the links if you can.)
5. Are there obvious missing risks, costs, or a simpler approach?
6. If a "candidate change" is attached: would it make the framework better, worse, or no different?
Finish with a one-sentence overall judgment.
Please answer in the same language as the task definition."""


def cmd_export(a):
    s = load()
    r = cur(s)
    nodes = r["nodes"]
    print("===== External review packet: copy everything below into another AI =====\n")
    print(REVIEW_PROMPT)
    print(f"\n---\n\n**Task definition**: {s['task']}")
    if s["success"]:
        print(f"**Success criteria**: {s['success']}")
    for t, title in [("summary", "Summary"), ("synthesis", "Synthesis"), ("solution", "Solution")]:
        for k, v in of(r, t):
            print(f"\n**{title} {k}**: {v['content']}")
    plans = sorted(of(r, "plan"), key=lambda kv: -sum(kv[1]["score"] or [0]))
    if plans:
        print("\n**Candidate plans**")
        for k, v in plans:
            reb = [n["content"] for kk, n in nodes.items()
                   if n["type"] == "rebuttal" and kk.split("-X")[0] == k]
            print(f"- {k}: {v['content']} | {sum(v['score'] or [0])}/25 | rebuttal: {'; '.join(reb) or 'none'}")
    claims = [(k, v) for k, v in nodes.items() if v["level"] or v["tag"]]
    if claims:
        print("\n**Key conclusions (tag / evidence level)**")
        for k, v in claims:
            print(f"- {k}: {v['content']} ({v['tag'] or '-'} / {v['level'] or '-'})")
    ex = of(r, "example")
    if ex:
        print("\n**Real-world examples**")
        for k, v in ex:
            print(f"- {k}: {v['content']}  {v['url']}")
    if a.patch:
        print(f"\n**Candidate change**: {a.patch}")
    print("\n===== End of review packet =====")


def cmd_check(_):
    s = load()
    r = cur(s)
    nodes, p = r["nodes"], []
    plans = [k for k, v in nodes.items() if v["type"] == "plan"]
    rebutted = {k.split("-X")[0] for k, v in nodes.items() if v["type"] == "rebuttal"}
    for k, v in nodes.items():
        if v["type"] in {"summary", "synthesis", "solution"} and not v["sources"]:
            p.append(f"{k} cites no source IDs")
        if v["type"] == "solution":
            weak = [x for x in v["sources"] if nodes[x]["level"] in {"L0", "L1"}]
            if weak:
                p.append(f"Solution relies on low-evidence conclusions: {', '.join(weak)} (needs >= L2)")
            if any(nodes[x]["tag"] == "assumption" for x in v["sources"]):
                p.append("Solution relies on an unverified assumption; list it under 'Unconfirmed points'")
    for k in plans:
        if not nodes[k]["score"]:
            p.append(f"Plan {k} has no score")
        if k not in rebutted:
            p.append(f"Plan {k} has no rebuttal (every plan must be rebutted equally)")
    user_plans = [k for k in plans if nodes[k]["user"]]
    if plans and len(user_plans) == len(plans):
        p.append("All plans come from the user's proposal; at least one independent plan is required")
    if len(user_plans) > 1:
        p.append("The user's proposal may occupy at most one plan")
    if plans and not of(r, "example"):
        p.append("No real-world examples; if none exist, state 'no precedent'")
    for t in {x["target"] for x in r["retries"]}:
        c = sum(1 for x in r["retries"] if x["target"] == t)
        if c > MAX_RETRY:
            p.append(f"{t} retried {c} times; suggest redefining the problem")
    print("✅ Check passed" if not p else "\n".join("⚠️ " + x for x in p))


def main():
    ap = argparse.ArgumentParser(description="RSI state machine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    x = sub.add_parser("init"); x.add_argument("task"); x.add_argument("--success")
    x = sub.add_parser("add")
    for n in ("id", "type", "content"):
        x.add_argument(n)
    for n in ("--parent", "--sources", "--tag", "--level", "--score", "--url"):
        x.add_argument(n)
    x.add_argument("--user", action="store_true")
    x = sub.add_parser("retry"); x.add_argument("target"); x.add_argument("reason")
    for c in ("round", "status", "handoff", "check"):
        sub.add_parser(c)
    x = sub.add_parser("export"); x.add_argument("--patch")
    a = ap.parse_args()
    globals()[f"cmd_{a.cmd}"](a)


if __name__ == "__main__":
    main()
