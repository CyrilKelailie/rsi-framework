# RSI Framework v2.3

> Multi-branch reasoning + neutral verification + human-gated self-improvement. Two Agent Skills for Claude (claude.ai / Claude Code).
>
> [中文说明](README.zh-CN.md)

**Runs only when you type `/rsi`, `/retry` or `/rethink`. It is never an always-on background process.** Replies follow the user's language.

```
/rsi <idea>
  ├─ Five branches (internal): Purpose · First principles · Constraints · Success criteria · Resources
  ├─ ① Summary 1: task definition
  ├─ Plans (internal): Plan A/B/C → divide → steelman rebuttal → verification → scoring
  ├─ ② Summary 2: one-line description · score · strongest rebuttal · evidence level
  ├─ ③ Real-world examples: real cases + source links
  ├─ ④ Synthesis: decision variables, not a repeat of the plans
  ├─ Decision point: multiple-choice (and ask on the spot whenever something is unclear)
  └─ ⑤ Solution: end of the round, stop

/retry [1|2]   Same goal, new path (change at least one: plan / source / decomposition / verification / assumption)
/rethink       Review the method → Patch → evaluate (question bank / external review) → collect question → next round
```

## Neutrality (not steered by the user's opinion or any single plan)

1. The user's own idea may occupy at most one plan; at least one plan must not use it
2. Success criteria and scoring dimensions are fixed before plans are generated
3. Every plan receives an equally strong steelman rebuttal
4. User statements are split into *fact* and *preference*; preferences affect the choice, never the scores
5. Strength of a conclusion depends on its evidence level (L0 intuition → L4 computed), not on who proposed it

All of the above are checked automatically by `rsi_state.py check`.

## Layout

```
skills/
├── rsi/
│   ├── SKILL.md              Flow · invariant principles · lessons · question bank
│   ├── references/
│   │   ├── method.md         Tags & evidence levels · branches · plans · rebuttal · scoring · examples
│   │   └── control.md        Asking · /retry · stop conditions
│   ├── templates/            The five output templates ①–⑤
│   ├── scripts/rsi_state.py  State machine: IDs, traceability, evidence, neutrality checks, handoff, review packet
│   └── evals/rubric.md       Scoring rubric (locked)
└── rethink/
    ├── SKILL.md              Review → Patch → candidate version → evaluate → next round
    ├── references/review.md  Review checklist · lesson format · Patch format · anti-overfitting
    └── templates/            Review report
```

## Evaluation

A general-purpose framework has no fixed exam, so there are two routes:

- **Question bank**: each `/rethink` asks (multiple choice) whether to add this round's task to the bank; the bank grows from real use (max 10)
- **External review**: `rsi_state.py export` produces a review packet to paste into another AI; its feedback is checked item by item, never accepted wholesale. The packet does not reveal which plan came from the user, so the reviewer is not biased

## Roadmap

- [x] v2.3 English edition; replies follow the user's language
- [x] v2.2 Personal edition: question bank grows with use; external AI review
- [ ] Company edition: independent verifier agent; tiered autonomy; unattended loop with drift alerts

## Install

**claude.ai (web)**: go to claude.ai/customize/skills → **+** → **Create skill** → **Upload a skill**, and upload `rsi.zip` and `rethink.zip` separately. Requires *Code execution and file creation* to be enabled.

**Claude Code**: `cp -r skills/rsi skills/rethink ~/.claude/skills/`

Dependencies: the `divide-into-several-pieces` skill (optional; built-in rules are used if absent), Python 3.8+ (standard library only).

## License

MIT
