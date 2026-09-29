# Method

## General: information tags and evidence levels

Tag every piece of information. Never silently promote an *assumption* to a *fact*:

| Tag | Meaning |
|---|---|
| fact | Confirmed: has a source, or an objective situation the user stated clearly |
| assumption | Treated as true for now; needs verification |
| unknown | Not known yet, and it affects the conclusion |
| inference | A judgment derived from facts and evidence |
| preference | The user's inclination; affects the choice, never the scores |

Give every key conclusion an evidence level, as high as possible:

| Level | Method | Examples |
|---|---|---|
| L4 | Computed / executed | calculation, code, tests, simulation |
| L3 | External evidence | official docs, reliable data, several independent sources |
| L2 | Structured evaluation | item-by-item rubric assessment |
| L1 | Model self-check | internal consistency check |
| L0 | Intuition | "feels right" |

L0 and L1 must never be written as firm conclusions. Key conclusions the Solution depends on need at least L2.

## §1 Five branches

Each branch is reasoned independently, without looking at the others:

| ID | Branch | Answers |
|---|---|---|
| G | Purpose | What does the user really want? Separate the stated request from the real intent |
| F | First principles | What are the irreducible facts or mechanisms (2–4)? Which conventional assumption does not hold? |
| L | Constraints | Time, cost, permissions, technology, law, anything the user explicitly forbids |
| S | Success criteria | What counts as done, written as a checkable condition |
| R | Resources | What is actually available: information, files, tools, channels, people, money |

An unknown that would change the plan completely → ask with a multiple-choice question. Minor → tag *assumption* and continue.

## §2 Generating plans

- Plans A/B/C must differ in **mechanism**: at least one of technical route, decision logic, cost structure or risk structure
- Forbidden: A = do X, B = do X more carefully, C = do X more thoroughly
- The user's proposed approach may occupy at most one plan; at least one plan must not use it
- If only one reasonable route exists, fewer than three is fine, but explain why in Summary 2
- Break each plan into sub-problems with divide-into-several-pieces (or the same logic if that skill is absent) and check each: does it hold, preconditions, failure conditions, can it be verified. A plan that sounds reasonable overall does not mean every step holds

## §3 Steelman rebuttal (ID X)

Against the **strongest version** of each plan, find:

1. The strongest counterexample
2. The step most likely to fail
3. Hidden assumptions
4. Overlooked costs
5. A simpler way to achieve the same thing
6. Whether it is "clever-looking but useless"
7. Whether it drifts from the task definition

Apply equal force to every plan, regardless of user preference or first impressions.

## §4 Scoring (after rebuttal and verification)

Dimensions are fixed **before** plans are generated; 1–5 each, 25 max:

| Dimension | 1 | 5 |
|---|---|---|
| Fit | Drifts from the purpose | Directly meets the success criteria |
| Feasibility | Depends on conditions not available | Can start this week with current resources |
| Cost | Far exceeds the constraints | Clearly below the constraints |
| Speed | More than a year to show results | Verifiable within weeks |
| Resilience | A fatal issue remains after rebuttal | Every rebuttal point has a response |

- An infeasible plan scores at most 10
- One-line description per plan (≤ 15 words): what it does + why it wins
- A difference of ≤ 2 points counts as a tie
- If the user picks a lower-scoring plan: record it as a *preference*; do not go back and change scores

## §5 Real-world examples (ID E)

Purpose: let reality correct the reasoning, not decorate the answer.

- Must be verified online; each case needs a clickable source link. If none can be found, do not output it and never invent one
- Search order: same industry and scale → same industry, different scale → different industry, same problem. Failure cases count too
- For each case: who (scale), what they did, result, what transfers / what does not, source
- A plan with no cases: write "no precedent (searched: …)" and list it as an uncertainty in the Synthesis
- Summarize in your own words; quote at most one sentence of the source
