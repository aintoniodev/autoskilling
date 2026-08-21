---
name: fusion-models
description: >-
  Fuse models instead of racing them: cast models into roles (ARCHITECT,
  BUILDER, VALIDATOR, JUDGE, ATTACKER, COORDINATOR) as clean-room
  subagents and merge what they produce — AND, not OR. Patterns: opinion,
  fusion, gate-first validation, debate, council, redteam, coordinate, and the
  full gauntlet pipeline. Triggers: "fusion", "model council", "second
  opinion", "redteam this", "gate-first", "multi-model", "debate models",
  "gauntlet", "which model should I use".
---

# Fusion Models — AND, not OR

> Don't ask which model is best. Assign different models to different roles
> and fuse their outputs. You don't have to pick a winner when you can hire
> both.

You are the orchestrator. Each role runs as a **clean-room subagent**: its own
context, its contract as the full prompt, a tool permission level, and its own
scratch space. If you can only spawn one model, run the roles as separate
subagents of that model — the contracts do the work, not the logos.

**Tool levels**: read-only (`read/grep/find/ls`) · read+execute (add `bash`) ·
full (add `edit/write`). Validators get `write` scoped to the gate file only.

**Artifacts never land in the repo.** Everything goes to `.scratch/fusion/` or
the system temp dir: `prompt.md`, `plan.md`, `gate.py`, `gate-round-N.txt`,
`subtasks.json`, `worker-<id>.md`, `state.json`. The repo only ever receives
final, verified changes.

## Pick a pattern

| You need | Pattern |
|---|---|
| Second opinions before deciding | **opinion** |
| Two answers merged into one definitive answer | **fusion** |
| Proof the work is done, not vibes | **gate-first validation** |
| Plan or decision de-risked by dissent | **debate** or **council** |
| Hardening against adversarial use | **redteam** |
| Parallel build of independent slices | **coordinate** |
| All of it, in order | **gauntlet** |

## Patterns

### opinion

Two models answer the same prompt independently, read-only tools, no merging.
Present side by side: latency, tokens, the answer. The user reads both.

### fusion

ARCHITECT and BUILDER answer in parallel with full tools. A third FUSION
subagent then merges:

- Critically merge into ONE definitive answer. Discard anything incorrect or
  hallucinated, keep the strongest elements of each, combine complementary
  insights — never simply concatenate.
- Attribute inline: `[ARCHITECT]` / `[BUILDER]` on each carried claim.
- Close with a **Consensus & divergence** section.

### gate-first validation (the core discipline)

1. **The gate is written BEFORE any work.** A VALIDATOR subagent (read-only +
   write-to-gate) designs `gate.py` (or `gate.sh`): a script that exits 0 if
   and only if the request is genuinely, verifiably complete.
2. Checks are **concrete and objective — never vibes**. Nothing asked for may
   go unchecked; nothing unasked-for may be required. Each check prints
   `PASS: <what>` or `FAIL: expected X, found Y, at <path> — exactly what to
   do to fix it`.
3. **Baseline must fail RED** against the current state. A gate that passes
   before the work exists is worthless — rewrite it.
4. BUILDER builds with full tools, but the gate lives outside its control: it
   cannot read-edit the gate or its verdict. Satisfy it by genuinely
   completing the request, never by gaming individual checks.
5. Loop: run gate → feed every FAIL line back to the builder **verbatim** as
   its next instructions → rebuild. After N failures (default 3), VALIDATOR
   triages: root cause (not symptom), then "Do exactly this / Do NOT".
   Repair a defective gate **once** — never weaken, remove, or reinterpret a
   legitimate check. Halt after max validations (default 5).

### debate

DEBATER_A and DEBATER_B argue opposite sides for N rounds. An anonymized JUDGE
ends it: winner, strongest argument per side, and *what would change the
verdict*. Check after each round for CONVERGED / DIVERGED and stop early if
converged.

### council

For high-stakes plans and decisions. ≥2 panelists answer the same prompt
**anonymously** — each is instructed never to reveal its model or identity.
Then each panelist strictly ranks ALL anonymized answers by letter, no ties.
Tally by Borda count. A CHAIRMAN synthesizes: the consensus view, the areas of
disagreement, the strongest arguments from the top-ranked answer, and a
balanced final answer.

### redteam

BUILDER builds. An ATTACKER subagent probes the result with read + execute
only — it must NOT write, edit, or create files. The attacker's reply MUST end
with a strict final line:

```
VERDICT: BREACH — <summary>
VERDICT: CONCEDE — <summary>
```

BREACH feedback drives the next patch; loop (cap 3 rounds) until CONCEDE.

### coordinate

A COORDINATOR subagent decomposes the request into a `subtasks.json` manifest:

```json
{"subtasks": [{"id": "s1", "title": "...", "prompt": "...", "paths": ["src/db/**"], "dependsOn": []}]}
```

`paths` are gitignore-style **write domains**: each worker may only write
inside its globs, so concurrent writers never collide. Workers run by
dependency level, each embeds its role and identity in every filename it
creates, and writes a `worker-<id>.md` report. COORDINATOR verifies the
results and gets one fix-up pass.

## gauntlet — the full pipeline

```
deliberate → gate → decompose → build → verify → harden → integrate
```

1. **DELIBERATE** — council (default) or debate produces `plan.md`.
2. **GATE** — gate-first as above; baseline must fail RED.
3. **DECOMPOSE** — coordinator writes the manifest, topologically sorted into
   levels.
4. **BUILD** — workers run per level, writing `worker-<id>.md` reports.
5. **VERIFY** — the gate correction loop (FAIL lines → builder → triage).
6. **HARDEN** — redteam, up to 3 rounds.
7. **INTEGRATE** — COORDINATOR writes `integration-report.md`, plus one
   fix-up pass if needed.

Persist per-stage status, artifacts, and cost to `state.json` so an
interrupted gauntlet can resume. End with a verdict panel: what was built, gate
state, redteam verdict, total cost.

## Hard rules

- **The gate is designed before the work, and its baseline must fail.**
- **FAIL lines are the builder's next instructions — passed verbatim.**
- **Never move the goalposts**: one gate repair for a defective gate; zero
  tolerance for weakening real checks.
- **Attribute everything** merged from roles: `[ARCHITECT]`, `[BUILDER]`.
- **Anonymize where bias matters**: council answers and rankings.
- **Write domains prevent collisions**: no worker writes outside its globs.
- **Artifacts stay out of the repo**; only verified work lands.

## Source

Distilled from [fusion-models](https://github.com/oteroantoniogom/fusion-models)
(MIT), a fork of disler/fusion-harness. The original is a pi extension with
file-backed prompt templates; this skill is the agent-native version of its
methodology.
