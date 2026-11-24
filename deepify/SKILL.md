---
name: deepify
description: Research an idea or optimization to the best answer in four stages - wide first-principles web research by one strong model, four PhD-level debaters who attack each other, small measured experiments for every surviving hypothesis, then an autoresearch loop on the winner. Use for "deepify", "deep research", "investiga a fondo", "find the best way to", hard optimization or ideation problems where the first idea is rarely the best.
---

# Deepify

Four stages. Each stage feeds the next; do not skip one because the
previous output looks convincing. Tell the user up front that this starts
five delegates plus experiments, and keep the scope to the one question
they asked.

Write everything to a working folder (`research/<slug>/` in the repo, or
the scratchpad outside a repo): `brief.md`, `findings.md`, `debate.md`,
`experiments.md`, `loop.tsv`, `report.md`.

## 0. Brief

Write `brief.md`: the question, what "better" means as a number (latency,
cost, accuracy, conversion, a score), the baseline today, hard constraints,
and the budget (time, money, iterations). If there is no metric, agree one
with the user before starting. Without a number, stages 3 and 4 cannot work.

## Model choice

The skill does not fix a model. Use the model the user names; otherwise
pick the strongest available model with web search, at high reasoning
effort. Call it the research model. Stages 1 and 2 use the research model
for all five delegates, so the debaters share its knowledge and differ only
in stance. If the user asks for mixed models in the debate, use one per
debater instead.

Start delegates with whatever the harness offers: in T3 Code,
`orchestrator_capabilities` then `delegate_task`; in Claude Code, the
`Agent` tool with an explicit `model`; elsewhere, the provider's CLI in
read-only mode. If a model the user named is unavailable, say so and ask;
do not substitute silently. The research delegate must have web search; if
it does not, pick another model or run the searches yourself.

## 1. Research (one delegate, research model)

Prompt it to:

- Run a very large number of web searches: papers, failed attempts,
  postmortems, engineering blogs, benchmarks, old literature. Cover the
  last 50 to 100 years, not just recent work.
- Reason from first principles: what physical, mathematical or economic
  limits bound the answer, and how far the baseline is from them.
- Return 5 to 12 distinct hypotheses. For each: the mechanism, the
  evidence with links, known failures of the idea, expected gain, cost to
  test, and how it would be measured.

Save the result to `findings.md`. Spot-check a few cited sources yourself;
drop any hypothesis whose key source does not say what was claimed.

## 2. Debate (four delegates, research model)

Start four research-model delegates in parallel, read-only, each with
`brief.md` and `findings.md` and one fixed stance so they do not converge:

1. **Theorist**: attacks mechanisms and first-principles reasoning.
2. **Empiricist**: attacks evidence quality, benchmarks, confounders.
3. **Engineer**: attacks feasibility, cost, operational risk, hidden
   complexity.
4. **Contrarian**: argues the strongest case for ideas the others dismiss
   and proposes at least one hypothesis missing from the list.

Round 1: each ranks the hypotheses, zooms into the smallest details that
could break each one, and names the experiment that would settle it.
Round 2: give each delegate the other three's round-1 output (a fresh
delegate) and ask them to rebut point by point and update their
ranking. Stop after round 2 unless a disagreement would change which
hypotheses get tested; then run one more round on that point only.

Write `debate.md`: surviving hypotheses (usually 2 to 5), killed ones with
the reason, and open disagreements. Do not average opinions; keep the
argument that survived rebuttal.

## 3. Verify (small measured experiments)

For every surviving hypothesis, run the cheapest experiment that gives a
number against the baseline. Do this yourself or with code delegates on
any capable coding model, one hypothesis per delegate, each in its own
worktree or copy when they touch code.

- Same harness, same inputs, same machine for baseline and candidate.
- Profile, do not guess: record the metric, variance across at least 3
  runs, and where time or cost goes.
- A result inside the noise is "no effect", not a win.

Log each in `experiments.md`: hypothesis, setup, command, raw numbers,
verdict. Pick the path with the best measured gain per unit of cost. If
nothing beats baseline, report that and stop; do not run stage 4 on a loser.

## 4. Autoresearch loop (on the chosen path)

Iterate on the winner to squeeze it:

1. Propose one small change, informed by the debate and earlier iterations.
2. Apply it, run the same measurement.
3. Keep it if it beats the best so far beyond noise; otherwise revert.
4. Append a row to `loop.tsv`: iteration, change, metric, kept or reverted.

Stop when the budget runs out, or after 5 iterations in a row with no kept
change, or when the metric is within a few percent of the first-principles
limit from stage 1. Never let the loop change the metric, the harness or
the inputs to look better.

## Report

Write `report.md` and give the user a short version: the answer, baseline
vs final number, what was tried and killed and why, the experiments that
decided it, and open risks. Link the working files by absolute path.
