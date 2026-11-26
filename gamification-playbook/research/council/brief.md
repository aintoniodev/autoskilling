# Council brief: gamification-playbook

You are reviewing an agent skill, read-only. Do not edit any file. Reply in English.
Root: the `gamification-playbook/` folder that holds this brief (two levels up).

## Goal

`SKILL.md` is pasted into a design agent's prompt. The agent then designs a workplace
incentive programme for a scenario. We want designs that **launch** (a sponsor and the
workforce would approve it), get **noticed**, **last** after rewards stop, and score
well on the evidence rubric, while every claim stays true to the evidence.

## How it is measured

4 held-out scenarios (`research/scenarios.md`) × 3 runs = 12 designs per variant.
Designer: gpt-6.2-sol medium, max 900 words.

- Rubric: two blind judges score each design against `research/rubric.md`, 0–100.
- Holistic: a rubric-free judge (an "experienced operations leader") scores launch,
  noticed and lasting, 0–100.
- Noise: **larger than we first thought.** The same file run as a second batch of 12
  moved the rubric by 4–6 points (B0 69.9 → 63.8; C5 74.6 → 70.1) and lasting by up to
  6. So single 12-design batches cannot separate variants a few points apart. Numbers
  below pool every batch of the same text (`research/eval/pool.py`) and give a
  bootstrap 95% interval for the difference from pooled B0 (24 designs).

All numbers pool every batch of the same text; B0 has three batches (n = 36).

| Variant | n | Rubric | Launch | Noticed | Lasting |
|---|---|---|---|---|---|
| B0 no skill (3 batches) | 36 | 65.6 | 76.5 | 56.9 | 48.1 |
| **C15 = current SKILL.md** (C5 minus the "under an hour a week" line, plus "tend to") | 24 | 70.2 (+4.6 [+2.7, +6.5]) | 74.6 (−1.9 [−4.7, +0.9]) | 62.3 (+5.4 [+2.4, +8.5]) | 55.8 (+7.6 [+2.8, +12.3]) |
| C5 (C5, C5r, C5d, C5db) | 48 | 70.5 (+4.9 [+3.1, +6.8]) | 74.7 (−1.8 [−4.3, +0.9]) | 61.6 (+4.7 [+2.2, +7.3]) | 55.2 (+7.0 [+2.9, +11.2]) |
| C13 = C5 + "count an outcome a system already checks; a tick … earns nothing" | 24 | 68.0 (+2.4) | 76.2 (−0.3) | 61.4 (+4.5) | 55.8 (+7.6) |
| C14 = C5 + "sample inside a meeting the workplace already holds" | 24 | 68.1 (+2.5) | 74.0 (−2.5) | 61.1 (+4.2) | 51.6 (+3.4) |
| C4 (5 batches) | 60 | 70.4 (+4.8) | 76.0 (−0.5) | 59.0 (+2.2) | 58.0 (+9.8) |
| C12 = C4 + all five round 3 edits | 24 | 69.6 (+4.0) | 75.7 (−0.8) | 59.7 (+2.8) | 51.2 (+3.0) |
| C6–C11 round 2 attempts, one batch each | 12 each | 66.7–69.4 | 71.7–77.7 | 59.8–60.9 | 51.2–53.8 |
| V1 long evidence workflow | 12 | 74.5 | 65.6 | 46.9 | 35.3 |

Criterion means (0–10), B0 / C5 / C13: c1 8.74 / 8.48 / 8.10; c4 7.50 / 7.20 / 6.94;
c10 4.01 / 6.14 / 6.06. "Not launchable" in a judge's worst flaw: B0 0 of 72, C5 7 of
96, C13 2 of 48, C14 0 of 48. With C15, no design wrote a weekly time budget (C5: 40
of 48), and launch did not move.

**Transfer check on the real case** (`references/case-study.md`, scenario anonymised,
same judges, n = 6 designs per arm except the original): the original design 44.3 /
52.0 / 63.3 / 22.0; no skill 62.4 / 77.0 / 50.0 / 40.0; with C5 68.4 / 78.3 / 55.2 /
51.7 (rubric / launch / noticed / lasting).

C5 differs from C4 in one place: the reward is "a reward people will talk about at a
reachable milestone, announced at launch and handed over in person (paid time off, a
meal with a senior leader, a leader's specific public thanks). Name it in the launch
message." instead of "a real, modest reward … (paid time, a team meal, a leader's
specific thanks, a small gift card)". d-batches carry the corrected defaults claim
("Defaults change behaviour without extra pay"), and matched the earlier batches.

Every variant's text: `research/eval/skill-*.md`. Judge notes for B0, C2 and C4:
`research/council/judge-notes.md`, `judge-notes-C4.md`; raw scores and holistic reasons
for every batch: `research/eval/scores/<label>/`, `research/eval/holistic/<label>/`.
Round history, every reviewer's earlier blocking issues and what was done about each:
`research/council/LOG.md`. Read it first and don't re-raise an item already resolved
there unless the numbers show it still hurts. Evidence: `references/evidence.md`.

**Target:** a SKILL.md that clearly beats B0 where the intervals allow it and is not
worse on any axis, without going back to the long workflow that collapsed launch and
lasting. An edit counts as a gain only if it survives a second batch.

## Status after round 4

Round 4 scores: Hy4 9, Opus 8, Sol 8, DeepSeek 8, GLM 8 (Neon out of quota). Every
8 named launch (point estimate below B0) as the blocker and proposed one edit aimed at
it. Each was tested alone over two batches (C13, C14, C15). None moved launch without
costing rubric or lasting; C13's tie on launch came with a lower rubric and a lower c4,
the criterion it aimed at. Launch has now been aimed at by nine short variants (C6–C15);
its pooled range is −0.3 to −5.2 and every interval includes zero except C10's. Both
claim nits ("defaults persist", "people produce whatever is cheapest") are fixed. The
"hour a week" line was deleted because it measured neutral and is one line fewer.

For your score, say whether the remaining launch gap is a fault in this text that a
specific, testable edit would fix, or a tie the harness cannot separate. If you propose
an edit, it must target something not already tried in the table and LOG.

## Decision log (do not re-propose reversed items without new reasoning)

- Long step-by-step workflow with an output template and checklist (V1, ~150 lines):
  rubric up, but launch −14, lasting −17. Reversed: length made designs heavy and
  invisible.
- Telling the designer to cut checks and lower goals (C3): every score fell. Reversed.
- Round 4 single edits C13 (checked outcome), C14 (sample in existing meetings), C15
  (delete the hour line): no launch gain without a cost; don't re-propose.
- Round 3 edits bundled (C12): lasting fell. Don't re-propose them as a bundle; a single
  edit must show a gain over two batches.
- Kept: co-design and paid learning time; fix the work first and show the fix; credit
  verified work once; team progress plus a modest real reward; no surveillance; easy
  re-entry; make the new way the default before prizes stop; check after the end
  against a comparison.

## What to return

1. **Score out of 10**: how ready this SKILL.md is to ship. 9 or more means "ship it".
   Base it on the measured numbers and the evidence, not on taste.
2. **Blocking issues**: things that would stop you giving 9. A blocking issue is
   (a) a measured axis still at or below B0, with your diagnosis of which text causes
   it; (b) a claim not supported by `references/evidence.md`; or (c) an instruction
   that makes designs longer or harder to run without a measured gain.
3. **One concrete edit**: the exact replacement text for SKILL.md (old → new), at most
   about 10 added lines in total. Say which number you expect it to move and why,
   citing the judge notes.

Keep it under 500 words.
