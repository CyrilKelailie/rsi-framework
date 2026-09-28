#!/usr/bin/env python3
"""RSI 状态机 v2.0：记录思考树，校验可追溯性、证据等级与中立性，生成交接说明。

状态文件：.rsi_state.json（当前目录；可用 RSI_STATE 环境变量改路径）

  init "<任务定义>" [--success "<成功标准>"]
  add <编号> <类型> "<内容>" [选项]
      类型：branch plan rebuttal example summary synthesis solution
      --parent 编号      --sources A,A-X1,E1
      --tag 事实|假设|未知|推断|偏好
      --level L0-L4     证据等级
      --score 5,4,3,3,4 plan 评分：契合,落地,成本,速度,抗风险
      --url https://…   example 必填
      --user            标记为用户提议的方案
  retry <汇总编号> "<原因>"
  round | status | handoff | check
  export [--patch "<候选改动摘要>"]   生成给其他 AI 的外部复核包
"""
import argparse
import json
import os
import sys
from datetime import datetime

STATE = os.environ.get("RSI_STATE", ".rsi_state.json")
TYPES = {"branch", "plan", "rebuttal", "example", "summary", "synthesis", "solution"}
TAGS = {"事实", "假设", "未知", "推断", "偏好"}
LEVELS = {"L0", "L1", "L2", "L3", "L4"}
MAX_DEPTH, MAX_RETRY = 3, 3


def now():
    return datetime.now().isoformat(timespec="seconds")


def load():
    if not os.path.exists(STATE):
        sys.exit("未找到状态文件，请先运行 init")
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
    print(f"[R1] 任务定义已锁定：{a.task}")


def cmd_add(a):
    if a.type not in TYPES:
        sys.exit(f"类型必须是：{' '.join(sorted(TYPES))}")
    if a.tag and a.tag not in TAGS:
        sys.exit(f"--tag 必须是：{' '.join(TAGS)}")
    if a.level and a.level not in LEVELS:
        sys.exit("--level 必须是 L0-L4")
    if a.id.count(".") + 1 > MAX_DEPTH:
        sys.exit(f"{a.id} 超过最大嵌套 {MAX_DEPTH} 层，请回流")
    if a.type == "example" and not (a.url or "").startswith("http"):
        sys.exit("实际例子必须带来源链接：--url https://...")
    score = []
    if a.score:
        try:
            score = [int(x) for x in a.score.split(",")]
        except ValueError:
            score = []
        if len(score) != 5 or not all(1 <= x <= 5 for x in score):
            sys.exit("--score 必须是 5 个 1-5 的整数：契合,落地,成本,速度,抗风险")
    s = load()
    r = cur(s)
    if a.parent and a.parent not in r["nodes"]:
        sys.exit(f"父节点 {a.parent} 不存在")
    sources = [x for x in (a.sources or "").split(",") if x]
    missing = [x for x in sources if x not in r["nodes"]]
    if missing:
        sys.exit(f"来源不存在：{', '.join(missing)}")
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
    print(f"[R{r['round']}] {a.target} 第 {n} 次 retry：{a.reason}")
    if n > MAX_RETRY:
        print("⚠️ 超过 3 次，建议 /retry 1 重新定义问题")


def cmd_round(_):
    s = load()
    n = cur(s)["round"] + 1
    s["rounds"].append({"round": n, "nodes": {}, "retries": [], "started": now()})
    save(s)
    print(f"[R{n}] 新一轮开始，任务定义不变：{s['task']}")


def cmd_status(_):
    s = load()
    r = cur(s)
    print(f"任务：{s['task']}\n轮次 R{r['round']}　节点 {len(r['nodes'])}　retry {len(r['retries'])}")
    for k, v in r["nodes"].items():
        meta = " ".join(x for x in [v["tag"], v["level"],
                                     f"{sum(v['score'])}/25" if v["score"] else "",
                                     "用户提议" if v["user"] else ""] if x)
        src = f" ← {','.join(v['sources'])}" if v["sources"] else ""
        print(f"{'  ' * k.count('.')}- {k} [{v['type']}] {v['content'][:50]}{src}  {meta}")


def cmd_handoff(_):
    s = load()
    r = cur(s)
    print(f"# 交接说明 R{r['round']}\n\n**任务定义**：{s['task']}")
    if s["success"]:
        print(f"**成功标准**：{s['success']}")
    for t, title in [("summary", "汇总"), ("synthesis", "综合"), ("solution", "解决方案")]:
        items = of(r, t)
        if items:
            print(f"\n## {title}")
            for k, v in items:
                print(f"- {k}：{v['content']}")
    plans = sorted(of(r, "plan"), key=lambda kv: -sum(kv[1]["score"] or [0]))
    if plans:
        print("\n## 方案评分")
        for k, v in plans:
            sc = v["score"]
            print(f"- {k}{'（用户提议）' if v['user'] else ''}：{v['content']}｜"
                  f"{sum(sc)}/25（{'·'.join(map(str, sc)) if sc else '未评分'}）")
    for t, title in [("rebuttal", "反驳"), ("example", "实际例子")]:
        items = of(r, t)
        if items:
            print(f"\n## {title}")
            for k, v in items:
                print(f"- {k}：{v['content']}" + (f"（{v['url']}）" if v["url"] else ""))
    if r["retries"]:
        print("\n## retry 记录")
        for x in r["retries"]:
            print(f"- {x['target']} 第{x['n']}次：{x['reason']}")


REVIEW_PROMPT = """你是独立审稿人。下面是另一个 AI 按固定框架得出的方案。请只根据材料和你能查证的事实做检查，不要迎合任何一方。

请逐项回答，每项给结论（成立 / 存疑 / 不成立）和一句理由：
1. 解决方案是否真正回答了任务定义？
2. 关键结论的证据是否足够？有没有把假设当成事实？
3. 被放弃的方案里，有没有其实更好的？
4. 实际例子是否真实、是否支持对应结论？（能查证就查证链接）
5. 有没有明显遗漏的风险、成本或更简单的做法？
6. 如果附有"候选改动"：这些改动会让框架更好、更差，还是无影响？
最后用一句话给出总体判断。"""


def cmd_export(a):
    s = load()
    r = cur(s)
    nodes = r["nodes"]
    print("===== 外部复核包：请整段复制给其他 AI =====\n")
    print(REVIEW_PROMPT)
    print(f"\n---\n\n**任务定义**：{s['task']}")
    if s["success"]:
        print(f"**成功标准**：{s['success']}")
    for t, title in [("summary", "汇总"), ("synthesis", "综合"), ("solution", "解决方案")]:
        for k, v in of(r, t):
            print(f"\n**{title} {k}**：{v['content']}")
    plans = sorted(of(r, "plan"), key=lambda kv: -sum(kv[1]["score"] or [0]))
    if plans:
        print("\n**候选方案**")
        for k, v in plans:
            reb = [n["content"] for kk, n in nodes.items() if n["type"] == "rebuttal" and kk.split("-X")[0] == k]
            print(f"- {k}：{v['content']}｜{sum(v['score'] or [0])}/25｜反驳：{'；'.join(reb) or '无'}")
    claims = [(k, v) for k, v in nodes.items() if v["level"] or v["tag"]]
    if claims:
        print("\n**关键结论（标签 / 证据等级）**")
        for k, v in claims:
            print(f"- {k}：{v['content']}（{v['tag'] or '-'} / {v['level'] or '-'}）")
    ex = of(r, "example")
    if ex:
        print("\n**实际例子**")
        for k, v in ex:
            print(f"- {k}：{v['content']}　{v['url']}")
    if a.patch:
        print(f"\n**候选改动**：{a.patch}")
    print("\n===== 复核包结束 =====")


def cmd_check(_):
    s = load()
    r = cur(s)
    nodes, p = r["nodes"], []
    plans = [k for k, v in nodes.items() if v["type"] == "plan"]
    rebutted = {k.split("-X")[0] for k, v in nodes.items() if v["type"] == "rebuttal"}
    for k, v in nodes.items():
        if v["type"] in {"summary", "synthesis", "solution"} and not v["sources"]:
            p.append(f"{k} 没有来源编号")
        if v["type"] == "solution":
            weak = [x for x in v["sources"] if nodes[x]["level"] in {"L0", "L1"}]
            if weak:
                p.append(f"解决方案依赖低证据等级结论：{', '.join(weak)}（需 ≥ L2）")
            if any(nodes[x]["tag"] == "假设" for x in v["sources"]):
                p.append("解决方案依赖未验证的假设，需在'未确认的点'中列出")
    for k in plans:
        if not nodes[k]["score"]:
            p.append(f"方案 {k} 没有评分")
        if k not in rebutted:
            p.append(f"方案 {k} 没有反驳（所有方案须同等反驳）")
    user_plans = [k for k in plans if nodes[k]["user"]]
    if plans and len(user_plans) == len(plans):
        p.append("所有方案都来自用户提议，至少需要一个独立方案")
    if len(user_plans) > 1:
        p.append("用户提议最多占一个方案")
    if plans and not of(r, "example"):
        p.append("没有实际例子；确实找不到时应写明'无先例'")
    for t in {x["target"] for x in r["retries"]}:
        c = sum(1 for x in r["retries"] if x["target"] == t)
        if c > MAX_RETRY:
            p.append(f"{t} retry {c} 次，建议重新定义问题")
    print("✅ 检查通过" if not p else "\n".join("⚠️ " + x for x in p))


def main():
    ap = argparse.ArgumentParser(description="RSI 状态机")
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
