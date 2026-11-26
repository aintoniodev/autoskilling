## Round 3 review: `SKILL.md` (C4 body)

**Score: 9 / 10.** Ship it once the SH batch confirms the shipped wrapper; the body is byte-identical to C4 apart from the heading.

### Why 9

Reproduced with `pool.py`, n=24: rubric 71.4 (+4.5 [+2.2, +6.8]), lasting 59.3 (+9.2 [+4.0, +14.5]), launch 77.5 (+0.7 [−2.4, +3.7]), noticed 58.2 (+2.1 [−1.3, +5.6]). Two axes clear of zero, two level with point estimates above B0, none below. Every round 2 variant scored worse on rubric and lasting. C4 is a measured local optimum at this length.

### Blocking issues

None under the brief's definition.

- **(a) Axis at or below B0:** none. The only negative cells are S1 launch (−2.7) and S4 noticed (−1.2), both n=6, inside the 4–6 point batch noise.
- **(b) Unsupported claim:** every `SKILL.md` claim has a row. Two *instructions* have no dedicated D row: "count an event a system already records" and "start the reward a few weeks apart by team" (GLM, round 2; never applied). That is a gap in `evidence.md`, not a false claim in the skill.
- **(c) Heavy without gain:** none. Both things the ops leader calls heavy pay for themselves. The staggered start is c10 (+2.1 vs B0); making it optional (C11) cost rubric −4.7 and lasting −7.1. Shortening the checks (C9) lowered all four axes.

Non-blocking: "modest reward" appears in 24/24 C4 and 23/24 B0 notes, so it is the judge and scenario, not the text. C5's salient reward bought noticed +2.4 over C4 and cost lasting −3.7 and launch −2.9: a measured trade, not a free fix.

### One concrete edit

The codex "not launchable" flag (8/24 C4, 0/24 B0; claude 0 for both) has one cluster no variant has touched: the **decision number**. It is the named worst flaw in 5 of 48 C4 judgements: S1-r1 "post-reward decision uses digital completion alone"; C4r S3-r2 "rollout rule can make the kiosk the default based on one usable entry… even if audited compliance declines"; S3-r3 "logs per occupied bed-day can rise even as nurses log a smaller share of eligible moments, yet that rate drives the decision"; S4-r2 "decision metric is coverage corrected by a 10-ticket sample". The skill is strict about what is *credited* ("count the outcome, not activity") but silent about what is *decided on*, so designers keep the easy adoption rate for keep/change/drop.

**Old** (ending bullet):
> Before launch, name the one number that decides keep, change or drop, and check it again a few weeks after prizes stop.

**New**:
> Before launch, name the one number that decides keep, change or drop: the result the work is for (audited compliance, safe jobs, resolved tickets), not the count of tool use. Check it again a few weeks after prizes stop.

**Expected:** rubric +1 to +2 on 71.4, via c9 ("measures… quality after payout") and fewer S3/S4 codex launch flags; lasting flat to +1; launch and noticed unchanged.

**Why this is not a re-run:** the line is identical in C4–C11. It adds no fallback, no prize removal and no owner's note (the C6 failure modes). It extends the counting bullet's own rule rather than adding scope, and since nothing else changes it reads cleanly as a parallel batch against C4.
