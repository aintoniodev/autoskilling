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

See `loop.tsv` for every row. The main ones:

| Variant | Rubric | Launch | Noticed | Lasting | Words |
|---|---|---|---|---|---|
| B0 no skill | 69.9 | 79.7 | 56.0 | 52.4 | 722 |
| B1 original case principles | 62.6 | 71.2 | 52.8 | 40.3 | 725 |
| V1 full evidence workflow | **74.5** | 65.6 | 46.9 | 35.3 | 896 |
| C2 shipped skill | 68.3 | 77.0 | **60.0** | **56.0** | 675 |

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
