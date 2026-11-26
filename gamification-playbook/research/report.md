# Report: gamification playbook

## Question

Can a skill built from field evidence help an agent design a workplace incentive
programme that people adopt, notice and keep using after it ends, better than the agent's
own defaults, and better than the principles of a real programme it came from?

## Answer

Partly. The shipped skill (C2) is a 30-line set of seven rules. Against no skill on four
held-out scenarios:

- **Noticed: 60.0 vs 56.0** and **lasting: 56.0 vs 52.4** on the holistic judge. Both are
  above the re-judging noise (about 1 point).
- **Launch: 77.0 vs 79.7.** It does not meet the declared guard on this axis.
- **Rubric: 68.3 vs 69.9.** Slightly lower, about two run-to-run sds.

Against the real programme's original principles (B1) it is better on every measure:
+5.7 rubric, +5.8 launch, +7.2 noticed, +15.7 lasting.

The longer evidence workflow (V1) scored highest on the rubric (74.5) but lowest on
everything a practitioner would care about. That score was mostly the skill echoing the
rubric it shares a source with. It was rejected.

## What the evidence killed

Named leaderboards as a default, blanket manager visibility, streaks that break, badge
catalogues, instant unverified prizes, loss framing and clawbacks, fixed bracket and
threshold formulas, habit clocks ("8 weeks"), and mandatory celebrations. See
`../references/evidence.md`.

## Limits

- These are scores of written designs by model judges, not employee outcomes. Nothing
  here shows a programme built with this skill changes behaviour at work.
- One designer model, four scenarios, three runs. Judges share model families with the
  designer.
- The guard was not fully met: launch is about 3 points below no skill. A user who only
  needs a quick, approvable launch plan may do as well without the skill.
- Most underlying evidence is from exercise, sales, schools and public services.

## Process

Research (`findings.md`) → four-debater, two-round debate (`debate.md`, `debate/`) →
measured variants and a six-iteration loop (`experiments.md`, `loop.tsv`, `eval/`).
