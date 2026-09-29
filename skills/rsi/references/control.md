# Control

## §1 Ask while working

At **any step**, when something is unclear, unreadable or ambiguous, stop and ask with a multiple-choice question, then continue. Do not save questions for the end:

| When to ask | Example |
|---|---|
| The user's words have two or more readings that lead to different results | "New buyers": new countries, or new buyer types? |
| Missing information would change a plan or a score | Budget cap, deadline, whether outside partners are allowed |
| Two plans tie and the choice depends on the user's values | Faster results vs lower cost |
| Verified information conflicts with what the user said | The user's figure differs from the source |

**Do not ask** when you can decide technically and the answer would not change the conclusion → tag *assumption*, continue, and state it in the summary.

Format:
- Use AskUserQuestion: 1–2 questions at a time, 2–4 options each, recommended option first and marked "(Recommended)", one line per option on its consequence; the user can always type their own answer
- If unavailable, list numbered options 1, 2, 3 in text
- After the answer, do not repeat earlier output; continue from where you stopped
- Record the answer verbatim as *fact* or *preference*; never use it to rewrite the task definition or the scoring criteria (neutrality)

**Fixed decision point** after the Synthesis. Options must include at least: adopt the recommendation / choose another plan / wrong direction, start over (back to the five branches).

## §2 /retry: same goal, new path

| Command | Recomputed from |
|---|---|
| `/retry` | The most recent summary |
| `/retry 1` | Summary 1, everything after is redone |
| `/retry 2` | Summary 2 (including examples), everything after is redone |

1. Keep: task definition, success criteria, constraints (unless the user says they are wrong, in which case use `/retry 1`)
2. If the user gave no reason, ask: misunderstood me / plans not good enough / missed a condition / examples not relevant / verification too weak
3. Find where the previous version failed: which assumption was wrong, which plan was overturned, what information was missing, which verification was weak
4. **Change at least one**: plan, information source, decomposition, verification method, key assumption. Rewording alone is forbidden
5. Start the recomputed summary with three lines:
   ```
   Retry reason: …
   Previous failure point: …
   What changed: …
   ```
6. Record: `rsi_state.py retry <summary> "<reason>"`

## §3 Stop conditions

If any holds, stop expanding and go to the Solution or tell the user:

- The success criteria are met
- A new round adds no substantive information
- Verification costs clearly exceed the potential benefit
- The remaining uncertainty can only be resolved by real-world action or other people
- Two consecutive /retry results are highly similar → say "this is close to converging"
- The same summary retried more than 3 times → suggest `/retry 1` to redefine the problem
- Nesting deeper than 3 levels → force it back up
