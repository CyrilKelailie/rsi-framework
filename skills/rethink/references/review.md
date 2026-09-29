# Review method

## §1 Review checklist

- Which step produced the most value? Which wasted resources?
- Any repeated thinking, overturned assumptions, missed real-world constraints?
- Did the rebuttal attack the strongest version? Was the user's proposal rebutted with equal force?
- Was the evidence level high enough? Was any L0/L1 written as a conclusion?
- Were unnecessary questions asked, or necessary ones skipped?
- Where did /retry happen, and why? (one of the highest-weight signals)

Evidence weight: user correction > /retry reason > overturned by rebuttal > failed rubric item > rework in the flow.

## §2 Lessons

| Not acceptable | Acceptable |
|---|---|
| Be more careful | When three plans share the same core mechanism, do not treat them as three independent plans |
| Consider cost more | When the constraints include a budget cap, estimate each plan's first-month cost before scoring |

- Seen in one task type only: add to the lessons list, tagged with that task type
- Seen in 2+ task types, or the user explicitly calls it a process problem: only then may a flow rule change
- A single user preference may never become a rule

## §3 Patch

```
PATCH
Target:        {branches / plan generation / rebuttal / verification / scoring / examples / asking / retry / output format / lessons}
Problem:       {…}
Evidence:      {IDs, retry records or user corrections}
Change:        {exactly which line changes}
Expected gain: {which rubric item improves}
Side effects:  {…}
Validation:    {question-bank items, or external review}
```

## §4 Evaluation and anti-overfitting

Three methods; the user chooses:

| Method | How | Possible verdicts |
|---|---|---|
| ① Question bank | Pick 2–3 questions related to the change; run current and candidate up to Summary 2; compare with the rubric | keep / discard / inconclusive |
| ② External review | Export the review packet; another AI checks it; paste the feedback back and check each point | keep / discard / inconclusive |
| ③ Skip | No evaluation | inconclusive only; no upgrade submitted |

- Candidate total below current, or any item going from pass to fail → discard
- Also check: longer output, more questions, more complex rules — these count as regressions too
- Lessons max 15; when adding one, merge or remove one where possible
- Every 5 /rethinks, run an ablation: temporarily drop one rule and rerun the question bank; if nothing gets worse, delete it
- 3 consecutive changes in the same direction (longer, more conservative) → pause and ask the user
- 2 consecutive reviews with no evidence-backed change → the framework is stable; record only, do not upgrade
