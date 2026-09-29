---
name: rsi
description: Multi-branch reasoning framework. Use ONLY when the user's message explicitly contains /rsi or /retry, or when /rethink starts the next round. Never trigger otherwise, even for complex questions or mentions of thinking, analysis or decisions.
---

# RSI Reasoning Framework v2.3

The goal is not to think more, but to solve problems with increasingly reliable methods.

## 0. Trigger (highest priority; /rethink may not change this)

- Respond only to three commands: `/rsi` starts a round; `/retry` recomputes a summary; `/rethink` reviews and starts the next round
- Without one of these commands, answer as a normal conversation. Words like "think", "analyze", "RSI" or "review" do not start the framework
- Each round stops at the **Solution**. No automatic continuation, no endless loops
- After stopping, return to normal conversation and drop the framework format; exit immediately if the user clearly switches to an unrelated topic
- **Reply in the user's language** (e.g. Chinese in, Chinese out)

## 1. Invariant principles (neutrality)

1. **The user's idea is only one candidate**: it may occupy at most one plan; at least one plan must not use it
2. **Criteria before plans**: success criteria and scoring dimensions are fixed before plans are generated and never adjusted afterwards
3. **Equal rebuttal**: attack the strongest version of every plan; the user's favorite gets no softer treatment
4. **Separate fact from preference**: tag user statements as *fact* or *preference*; preferences affect the choice only, never scores, evidence or feasibility
5. **Evidence over origin**: a conclusion's strength depends on its evidence level, not on who proposed it
6. **Change ≠ improvement; more complex ≠ better; no counterexample found ≠ no counterexample exists**

## 2. Flow

| # | Step | Shown to user | Details |
|---|---|---|---|
| 1 | Five branches: purpose · first principles · constraints · success criteria · resources | internal | `method.md` §1 |
| 2 | **① Summary 1**: task definition | **output** | `templates/summary-1.md` |
| 3 | Generate Plan A/B/C → divide each → steelman rebuttal → verify → score | internal | `method.md` §2–§4 |
| 4 | **② Summary 2**: plans, scores, rebuttals, evidence levels | **output** | `templates/summary-2.md` |
| 5 | **③ Real-world examples**: real cases + source links | **output** | `method.md` §5; template inside summary-2 |
| 6 | **④ Synthesis**: decision variables, not a repeat of the plans | **output** | `templates/synthesis.md` |
| 7 | Decision point: confirm direction with a multiple-choice question after the synthesis | question | `control.md` §1 |
| 8 | **⑤ Solution**: end of round, stop | **output** | `templates/solution.md` |

Show only the five outputs and the questions. Decomposition, rebuttal and verification appear only as IDs and conclusions inside the summaries.

**Ask while working**: at any step, if something is unclear, ambiguous or missing and would change the result, stop and ask a multiple-choice question on the spot, then continue from where you stopped (`control.md` §1). Minor points that would not change the conclusion are not asked; tag them as *assumption* and continue.

## 3. /retry and stop conditions

See `control.md` §2–§3. In one line: **same goal, new path**.

## 4. State tracking

Record every node with `scripts/rsi_state.py` (ID, tag, evidence level, sources, score). Output the Solution only after `check` passes.

## 5. Evolvable areas

Only §6 (lessons) and §7 (question bank) may be changed by /rethink, and only after user confirmation. The trigger, the invariant principles and `evals/rubric.md` are locked unless the user explicitly asks.

## 6. Lessons

Max 15 entries, format `- [version] [task type] situation: action`. Each must be an actionable general rule ("when X, do Y"); "be more careful next time" does not count.

(none yet)

## 7. Question bank

Added by /rethink after the user chooses to, drawn from real tasks. Used only to compare versions, never to learn from. Max 10; when full, the user chooses which to replace. Aim to cover different task types.
Format: `- [type] question | pass line: must include …`

(none yet)
