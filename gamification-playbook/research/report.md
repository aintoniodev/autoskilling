# Report: gamification playbook

## Question

Can a skill built from field evidence help an agent design a workplace incentive
programme that people adopt, notice and keep using after it ends, better than the agent's
own defaults, and better than the principles of a real programme it came from?

## Answer

Yes on three of four measures, with launch tied. The shipped skill (C15) is a short set of
rules. Pooled over two batches and compared with no skill pooled over three (bootstrap 95%
interval of the difference in brackets):

| | No skill (n=36) | Skill C15 (n=24) | Difference |
|---|---|---|---|
| Rubric | 65.6 | 70.2 | +4.6 [+2.7, +6.5] |
| Launch | 76.5 | 74.6 | −1.9 [−4.7, +0.9] |
| Noticed | 56.9 | 62.3 | +5.4 [+2.4, +8.5] |
| Lasting | 48.1 | 55.8 | +7.6 [+2.8, +12.3] |

Launch is a tie the harness cannot separate: the interval crosses zero and the gap is
smaller than the no-skill arm's own batch-to-batch spread.

On one anonymised real case (the renewal programme in `../references/case-study.md`), a
design from the original principles scored 44.3 rubric and 22.0 lasting; no skill 62.4 and
40.0; the skill 68.4 and 51.7.

A six-member model council reviewed the skill over five rounds until every member who
returned a review scored it 9/10 (see `council/LOG.md`).

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
- Launch is tied, not better. A user who only needs a quick, approvable launch plan may
  do as well without the skill.
- Batch-to-batch noise is 4–6 rubric points. Early single-batch rows in `loop.tsv`
  (including the first B0 at 69.9) are less reliable than the pooled rows.
- Most underlying evidence is from exercise, sales, schools and public services.

## Process

Research (`findings.md`) → four-debater, two-round debate (`debate.md`, `debate/`) →
measured variants and a six-iteration loop (`experiments.md`, `loop.tsv`, `eval/`).
