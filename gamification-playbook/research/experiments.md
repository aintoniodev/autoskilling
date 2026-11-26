# Experiments

## Setup

- **Designer:** gpt-6.2-sol at medium effort designs an incentive programme for four
  held-out scenarios (`scenarios.md`): a field-service safety checklist in a unionised
  workforce, code reviews within one day for sceptical engineers, nurses using a
  hand-hygiene kiosk, and a support knowledge-base article per ticket. Three runs each,
  so 12 designs per variant. The skill under test is pasted into the prompt.
- **Rubric judges:** gpt-6.2-sol (high) and Claude Opus, blind, score each design against
  the frozen ten-criterion rubric in `rubric.md` (sha1 in `rubric.sha`). Reported score is
  the mean of both judges over 12 designs. Run-to-run sd was 0.3 to 1.9 points.
- **Holistic judge:** Claude Sonnet, no rubric, plays an experienced operations leader
  and scores 0–100 how well the design would launch, be noticed, and last. Re-judging the
  same baseline designs moved the scores by at most 1.1 points.
- **Acceptance guard**, declared before the variant results: the rubric is primary, but no
  variant is accepted if it falls below the no-skill baseline on the holistic judge.

Scripts: `eval/design.sh`, `eval/judge.sh`, `eval/holistic.sh`, `eval/score.py`. Every
variant tested is in `eval/skill-*.md`; per-design scores are in `eval/scores/` and
`eval/holistic/`.

## Why a holistic judge

The skill and the rubric were both written from `findings.md`, so a skill can score well
on the rubric by echoing it. V1 did exactly that: +4.6 rubric points over no skill, but
−14 on launch, −9 on noticed and −17 on lasting. The holistic judge's reasons were
consistent: rigorous but invisible (private messages only), heavy to operate, and credit
rules too complex to explain. The no-skill designs were praised for co-design with the
workforce, protected or paid time, and simplicity.

## Results

See `loop.tsv` for every row. The first rows used single batches; the later rows are pooled.

| Variant | Rubric | Launch | Noticed | Lasting |
|---|---|---|---|---|
| B0 no skill, pooled n=36 | 65.6 | **76.5** | 56.9 | 48.1 |
| B1 original case principles | 62.6 | 71.2 | 52.8 | 40.3 |
| V1 full evidence workflow | **74.5** | 65.6 | 46.9 | 35.3 |
| C4, pooled n=60 | 70.4 | 76.0 | 59.0 | **58.0** |
| C15 shipped, pooled n=24 | 70.2 | 74.6 | **62.3** | 55.8 |

## What each change taught

- **Length is the main lever on the holistic judge.** Every ~150-line variant (V1, V2a,
  V2b, L1–L3) stayed 6–17 points under B0 on lasting. Cutting to ~30 lines (C1) recovered
  launch by 6 points and lasting by 14 at once.
- **A felt motivator helps noticing** (V2a vs V1: +5 noticed).
- **Making the new way the default before prizes stop helps lasting** (L2 vs V2a: +3.8),
  matching the default-effect evidence.
- **Co-design and the minimum checks** (C2 vs C1) raised the rubric by 3 points and noticed
  by 3 without lengthening designs much.
- **Telling the designer to cut checks and lower goals** (C3) made every score worse.
- **One batch lies.** C4 and C5 each looked like large wins on their first batch and shrank
  on re-runs. From C4 on, every candidate ran twice and was compared with three pooled
  no-skill batches using a bootstrap interval (`eval/pool.py`).
- **Bundles hide regressions** (C12). Test one edit at a time.
- **An earned, talked-about reward lifts noticing** (C4 → C5: +2.6 noticed pooled).
- **Most launch-aimed edits cost rubric or lasting** (C6–C11, C13, C14). None moved launch
  outside the noise.
