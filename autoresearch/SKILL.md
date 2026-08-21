---
name: autoresearch
description: >-
  Run an autonomous experiment loop on a codebase or benchmark: pick an idea,
  implement it, measure against a baseline, keep what improves, revert what
  doesn't, log every run, repeat until the metric moves or the budget runs out.
  Domain-agnostic: test speed, build time, bundle size, training loss,
  Lighthouse scores. Triggers: "autoresearch", "experiment loop", "optimize
  this metric", "keep what works, revert what doesn't", "hill-climb this
  benchmark", "run experiments on this".
---

# Autoresearch — try, measure, keep or revert

> Try an idea. Measure it. Keep what works. Revert what doesn't. Repeat forever.
> An agent doesn't get bored.

You are the experimenter. The metric — not your confidence in the idea — is the
only advocate. Everything you need to resume lives on disk, so the loop survives
context resets and restarts.

## Process

### 1. Set up the session (once)

Agree with the user on five things: **goal** (one sentence), **metric** (name,
unit, direction — minimize or maximize), **measure command** (how to get a
number), **iteration cap**, and **budget** (time or money).

Then:

- Create a branch: `autoresearch/<session-name>`.
- Write the session files under `.auto/`:

| File | Purpose |
|---|---|
| `.auto/prompt.md` | Living session doc: goal, metric, rules, current best. A fresh agent resumes from this file alone. |
| `.auto/measure.sh` | The benchmark. Prints `METRIC name=<number>` lines and nothing else that pollutes the metric. |
| `.auto/ideas.md` | Idea backlog. Add ideas as you discover them; cross out the tried ones. |
| `.auto/log.jsonl` | Append-only log, one JSON line per experiment. |
| `.auto/checks.sh` | Optional correctness gate (tests, types, lint). |

- **Baseline first.** Run the measure command ≥3 times. Record the median as
  the baseline and the median absolute deviation (MAD) as the session's noise
  floor. No experiment is judged without a baseline.

### 2. Run the loop

One iteration:

1. **Pick** the smallest idea from `ideas.md` with plausible upside. Prefer
   small, reversible, measurable changes.
2. **Implement** the smallest version that could work.
3. **Commit** — one idea per commit, so keep and revert are always clean.
4. **Measure**: run `measure.sh` ≥3 times, take the median.
5. **Backpressure**: if the metric improved, run `checks.sh`. Checks failing is
   treated like a crash: no commit, revert.
6. **Judge** — confidence = `|improvement| / MAD` against the noise floor:
   - **Green ≥2.0×** → likely real. **Keep.**
   - **Yellow 1.0–2.0×** → marginal. Re-run once; keep only if it holds.
   - **Red <1.0×** → within noise. **Revert.**
   Confidence is advisory, you keep final authority — but never keep an
   unmeasured win.
7. **Keep** = the commit stays, recorded in the log. **Revert** = the
   experiment commit is undone: `git reset --hard HEAD~1` on the session
   branch — or `git revert` if the commit was already pushed. Code gone,
   `.auto/` always survives.
8. **Log** one line:

```json
{"i":7,"idea":"cache transitive deps","metric":"build_s","before":19.1,"after":6.7,"delta":-12.4,"confidence":4.2,"verdict":"keep","commit":"a1b2c3"}
```

9. Update `.auto/prompt.md` when the best result or the scope changes. Next idea.

Stop when: iteration cap reached, budget spent, or no ideas left with plausible
upside. Say which.

### 3. Finalize

Group kept experiments into clean, independent branches from the merge-base.
Groups must not share files, so each can be reviewed and merged separately;
if two kept experiments touched the same file, they belong in the same group.
Report: kept vs reverted, best improvement with its confidence, where the log
lives.

## Hard rules

- **Never keep an experiment you didn't measure.**
- **Never weaken the measure or the checks to make a result pass** — that is
  moving the goalposts, not optimizing.
- **One idea per commit.**
- **Revert means gone**: the experiment commit is undone and no dead code
  stays behind — no "I'll clean it up later".
- **The session must be resumable from disk alone**: `prompt.md` + log tail +
  `git log` are enough for a fresh context to continue.

## Source

Distilled from [pi-autoresearch](https://github.com/davebcn87/pi-autoresearch)
(davebcn87; upstream license not stated). The original is a pi extension with
dedicated tools (`init_experiment`, `run_experiment`, `log_experiment`); this
skill is the agent-native version of its loop.
