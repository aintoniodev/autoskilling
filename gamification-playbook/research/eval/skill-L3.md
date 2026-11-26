---
name: gamification-playbook
description: >-
  Design a workplace incentive or gamification programme that gets people to adopt a tool
  or habit without backfiring: rewarding the wrong proxy, surveillance, gaming, or a lift
  that vanishes when prizes stop. Grounded in field experiments and meta-analyses, with
  evidence grades. Use when asked to gamify adoption, design a rally, contest, leaderboard,
  badges, streaks, points or rewards for employees, or to review such a design.
license: MIT
metadata:
  version: 1.0.0
---

# Gamification playbook

The programme is a temporary push to get people to try a better way of working. It is
not the reason they keep doing it. Most designs fail in one of four ways: the new way
isn't actually better for the worker, the reward counts something easier than the real
work, people feel watched, or the effect disappears when the prizes stop. This skill
designs against those four first, then adds the smallest motivating layer that people
will notice.

Evidence grades used below and in `references/evidence.md`: **A** meta-analysis or
several field RCTs, **B** one field RCT or strong natural experiment, **C** lab or
observational, **D** expert judgement or postmortem. Grades describe the source, not
how sure we are it transfers to your workplace.

## Workflow

Do these in order. Each step produces something concrete; write it into the design.

### 1. Diagnose why people don't do it today

Before any game, find out which of these is true for the target behaviour:

- **Blocked**: no access, the tool fails on some cases, approvals or data are missing.
  A game will not fix this. Fix it or exclude those cases openly.
- **Not worth it to the worker**: the new way costs more time, rework or risk than the
  old one. Fix the workflow first. Rewards only shift that balance while they run (A).
- **Not noticed or not tried**: the worker would benefit but hasn't started. This is the
  case a programme helps.

Walk one supported case and one blocked case end to end. Name an owner who fixes
blockers and how fast. If most cases are blocked, stop and say so.

### 2. Define the one thing that earns credit

- Name the role, the work event that triggers it (a cue already in their day, such as
  "a renewal enters your queue"), and the act that counts.
- Count **completed, qualified work**, never logins, clicks or drafts. People produce
  whatever is cheapest to count (Kerr 1975, D; Wells Fargo sales-practices penalty,
  2016, D; GitHub streak removal changed activity patterns, not quality, B).
- At most one credit per unit of work. Say how the target metric and the credit relate
  if they differ.
- Table-test the rule before launch: a normal case, a duplicate, a reversal or recall,
  a late or edited due date, a case done the old way, an omitted case. If you cannot
  get trustworthy history for these, do not attach stakes.
- Pick one independent quality check (a sampled review, recall or rework rate) and a
  pause rule: what number, who decides, what happens.

### 3. Write what the worker sees on their next real case

This is the part people notice. Write the actual copy, not a description of it:

- **The invitation**, delivered in the tool or channel they already use, at the cue:
  what to do now and what they get from it (time saved, fewer errors, a reachable
  milestone).
- **Confirmation** right after the act: specific and prompt ("Quote sent with the
  assistant, 1 of your 6 this week"). Prompt specific feedback beats delayed vague
  feedback (A for feedback and self-monitoring: Harkin et al. 2016, d = 0.40).
- **Progress against an attainable personal goal** sized to their own volume (n of N),
  with the next action. Specific, attainable goals work (A: Locke and Latham; Epton et
  al. 2017, d = 0.34). Handle people with zero or very few opportunities explicitly.
- **Restart after a miss**: a missed week is just the next case, not a broken record.
  If you add a streak, a single break must not wipe progress (Silverman and Barasch
  2023, C; the top arm in a 54-arm megastudy rewarded returning after a miss, Milkman
  et al. 2021, B).

### 4. Decide who sees what

- **Default: each person sees their own progress; everyone sees the team's verified
  progress against its own baseline**, with no individual names. Shared team progress
  is visible enough to be noticed without exposing anyone.
- Managers get aggregates. Individual access only for a named purpose (coaching on
  request, corrections, disputes), logged, time-limited, and never reused for
  discipline. Electronic monitoring shows no performance gain and more stress across
  94 samples (A: Ravid et al. 2023). Telling people at launch is disclosure, not
  consent.
- Hide any group or cell small enough to identify a person.

### 5. Choose the motivator people will feel

A programme nobody notices fails as surely as one that backfires. Private progress
messages alone are too quiet. Every design needs **one motivator people will talk
about**, tied to verified work, chosen or at least tested with a few of the people it
targets:

- **Default**: the team's verified progress shown where people already look, plus a
  real, modest reward when the team or the person crosses a reachable milestone
  (paid time, a team meal, a leader's specific public thanks, a small gift card).
  Recognition and modest tangible rewards both work when they are earned and specific.
- Fund the friction fixes from step 1 visibly, so people see the programme gives back
  ("you reported it, we fixed it").

Then, only if it fits, one of these extras:

| Add-on | When it can help | Conditions |
|---|---|---|
| Recognition (thanks, a note from a leader, a symbolic award) | Low cost, signals the work matters | Specific and earned, not a participation trophy. Non-financial recognition beat pay in one field trial (B: Ashraf et al. 2014). |
| Tangible prize | Trying the new way costs real effort | Paid only on verified work, after the quality check. Never claw back pay already given; never fines. |
| Peer comparison or contest | Comparable people, a goal everyone can still reach | Opt-in, reversible, small top display or team-vs-own-baseline. Rank feedback raised output in some firms and cut it in others (A for mixed effects: Barankay; Bandiera et al. 2013, -14% under rankings). |
| Badges | Marking real milestones of skill | Few and meaningful. A large catalogue adds state and gaming (C: Anderson et al. 2013). |

Do not use by default: loss framing, named leaderboards, blanket manager visibility,
fixed bracket formulas, mandatory celebrations, or a habit clock ("21 days"). Habit
formation took 18 to 254 days in the one real-world study (C: Lally et al. 2010).

### 6. Plan the end and the decision

- Time-box it and write the end date into the launch message.
- Keep the useful parts (workflow fixes, personal feedback) after the prizes stop.
- Measure the behaviour on real opportunities for at least as long again **after**
  rewards end. Gym-incentive trials repeatedly show lifts that fade once payment stops
  (A: Charness and Gneezy 2009; Royer et al. 2015; Carrera et al. 2018). Only 8% of
  megastudy arms still showed an effect after the programme (B).
- Compare against something: the same support without the game for another group, or
  at minimum a predeclared baseline. Without a comparison, call the result feasibility,
  not proof.
- Write the decision rule in advance: scale, change or stop, on which numbers.

## Output

Produce, in this order:

1. **Diagnosis**: blocked, not worth it, or not noticed, with the evidence.
2. **Credit rule** and its table test.
3. **Worker copy**: invitation, confirmation, progress line, restart line.
4. **Visibility**: who sees what, and why.
5. **Add-on**, if any, with its reason and conditions.
6. **Operator card**: data source, quality check and pause rule, correction route,
   owner, weekly time cost.
7. **End and decision plan**: dates, follow-up window, comparison, decision rule.
8. **Risks**: the three most likely ways this design backfires here.

Mark anything you assumed (access, data, approvals). Keep the design short enough for
the sponsor to read in five minutes: aim for 600 words or fewer.

**Keep operations proportionate.** Every check costs someone's time every week. For
under about 100 people, one owner spending under an hour a week should be able to run
it: a small weekly sample instead of full audits, an existing report instead of a new
dashboard, the comparison group only if you have several similar teams (otherwise a
baseline and a follow-up window). Name the cost; cut any control whose cost exceeds
the harm it prevents.

## Minimum viable programme

A design is launchable only if all six hold:

- [ ] One qualified act, triggered by a real work cue, with a safe fallback and a
      blocker owner.
- [ ] Worker copy that says what to do now, why it helps them, and confirms the act.
- [ ] A credit rule table-tested against duplicates, reversals and omissions.
- [ ] An independent quality check with a pause rule and an owner.
- [ ] Private individual progress; team progress without names; purpose-limited
      manager access.
- [ ] An end date, a post-reward follow-up window and a written decision rule.

## References

- `references/evidence.md`: every claim above with its source, grade and transfer limits.
- `references/case-study.md`: an anonymised real design, what this playbook changed and why.
