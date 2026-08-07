---
name: delegate
description: >-
  Multi-model orchestration in pi: the main session (expensive model, e.g.
  GLM 5.2) plans, decomposes work into self-contained contracts, and delegates
  execution to a fast cheap executor subagent (DeepSeek V4 Flash) via parallel
  subagent tasks. Triggers: "delegate", "orchestrate", "multi-model",
  "split into tasks", "parallel subtasks", "executor agent", "run this in
  parallel", "hand out tasks".
version: 1
created: "2026-08-07"
updated: "2026-08-07"
---

## When to Use

Use when work decomposes into several well-specified, independent subtasks
that can run in parallel: batch migrations (unittest→pytest), test
generation, per-file refactors, document/batch processing, data transforms,
multi-file analysis.

The architecture reserves expensive reasoning (the **orchestrator**) for
decisions where a wrong choice is costly — understanding the objective,
designing the plan, reviewing results — and pushes high-volume execution to a
fast, cheap model (the **executor**).

Do NOT use when:

- The task is small (one operation): delegation overhead costs more than it saves.
- Every step needs global context (each executor would re-read everything).
- Latency is critical (each delegation adds a subprocess + model call).
- Request volume is low: coordination cost can exceed the savings.

## Architecture

| Role | Where | Model | Responsibilities |
|---|---|---|---|
| Orchestrator | Main pi session | `glm-5.2` (launch `pi -m glm-5.2`) | Understand goal, plan, decompose into contracts, review results, keep direction |
| Executor | `subagent` tool → `executor` agent | `deepseek-v4-flash` (pinned in agent frontmatter) | Receive ONE self-contained contract, complete it, return a 3-line summary |

The frontier between them is the **work contract** — never the conversation.
The orchestrator transforms its context into a spec the executor can run
without knowing the history. "El orquestador no pasa conversaciones. Pasa
contratos de trabajo."

## Setup

1. Install the executor agent (once):
   ```bash
   cp delegate/agents/executor.md ~/.pi/agent/agents/executor.md
   ```
2. Launch orchestrator sessions with the expensive model:
   ```bash
   pi -m zai/glm-5.2
   ```
   Use the provider-prefixed id (`provider/model`): bare ids can resolve to a
   different provider in a spawned process and fail with "No API key found".
3. Verify: ask the orchestrator "list available subagents" — `executor` must
   appear. The frontmatter `model:` field is passed to the spawned process
   (`--model`), so the executor always runs on the cheap model regardless of
   the orchestrator's.

## Procedure

### 1. Analyze and plan (orchestrator only)

Understand the goal; inventory the work (files, conventions, dependencies).
Decide the decomposition BEFORE spawning executors. This is the expensive
reasoning — do it here, once.

### 2. Decompose into contracts

Each subtask must be expressible as a self-contained contract. If it can't,
it's not ready to delegate. Template (embed in the task text):

```yaml
objetivo: <what must exist when done>
entradas: <files/data/resources needed — ABSOLUTE Windows paths (C:/...), never /tmp>
restricciones: <rules that must not be broken: conventions, decisions, no-delete>
criterio_de_exito: <how to verify the task is done correctly>
```

Every contract must also carry an explicit **no-delete clause** ("NO borrar
ni modificar NINGÚN otro archivo"): a cheap executor will "clean up" sibling
files if nothing forbids it.

### 3. Warm up the cache (parallel bursts)

The executor's static prefix (agent system prompt + conventions) only enters
cache after one full call finishes. For N parallel tasks: send ONE task first,
then the rest in parallel — the burst then hits the cached prefix. At scale
this is the difference between N full-priced calls and 1 + (N−1) cached-prefix
calls.

### 4. Delegate

Parallel mode: "Run N tasks in parallel with the executor agent: [contracts]".
Each task = contract + pointer to the shared workspace. Executors write
artifacts to the shared filesystem (Pattern 1). NEVER pass the orchestrator's
conversation — only the contract.

### 5. Validate deterministically

Do not trust the executor's word: run the success criteria yourself —
`pytest`, `git diff`, linters. On failure, re-delegate ONLY the failed
contract with the error attached, without restarting the process or dragging
history.

### 6. Review and consolidate (orchestrator only)

Read the 3-line summaries, spot-check artifacts, detect cross-task
inconsistencies, decide on rework. The orchestrator reads artifacts only when
a review needs them.

### 7. Log observability

Record per task: model, prompt (hash), cost, result, duration. The subagent
tool reports turns/tokens/cost per task — collect them into the session log.
This is how you detect degradation when a model changes and improve the
contracts.

## Return-value design

The executor returns exactly:

```
## Resumen operativo
1. Hecho: <artifacts created/modified + what was done>
2. Estado: ✅/⚠️/❌ <verification actually run>
3. Riesgos: <anything the orchestrator must check> | ninguno
```

The artifact stays in the shared workspace; only a later review retrieves it.
This keeps the orchestrator's context flat no matter how many tasks run.

## Other patterns

- **Pattern 2 (executor as tool):** for adaptive flows (debugging), call the
  executor iteratively from the orchestrator — each call a new contract, each
  result informing the next decision. The contract design matters most here:
  too much irrelevant output grows the orchestrator's context and worsens
  decisions.
- **Pattern 3 (shared state):** for project-scale work, multiple pi sessions
  (or worktrees) share the filesystem/repo; pi-intercom coordinates between
  them. State lives outside conversations; design who may modify what.

## Pitfalls

- **Passing the orchestrator's conversation to the executor**: noise, token
  cost, and retries that drag accumulated errors. Always transform into a
  contract.
- **Executor returning full diffs/content**: inflates orchestrator context and
  bill. Enforce the 3-line summary.
- **Orchestrator doing executor work**: if it writes every file itself, the
  architecture is pointless — and expensive.
- **Re-delegating without the error attached**: a failed task must be retried
  with the concrete failure output.
- **Underspecified contracts**: executors will guess. If you can't write the
  contract, plan more first.
- **Skipping deterministic validation**: the model decides, tools confirm.
  No test run, no "done".
- **Parallel-first bursts**: all miss the cache (it materializes when a call
  finishes). Warm-up call first.
- **`/tmp`-style paths in contracts**: on Windows the write tool resolves
  `/tmp` to `C:\tmp` while bash resolves it to `C:\WINDOWS\TEMP` — executors
  see two different "projects" and may destroy one. Always absolute `C:/...`
  paths, stated once, used verbatim.
- **No no-delete clause**: executors with delete freedom destroy sibling
  files (observed: an executor deleted and best-effort-recreated two sibling
  test files it never read, dropping a test). Forbid deletion explicitly.
- **Bare model ids in agent frontmatter**: `deepseek-v4-flash` resolved to a
  provider `deepseek` without a key in the spawned process. Use the
  provider-prefixed id (`opencode-go/deepseek-v4-flash`).

## Verification

- `pi -m zai/glm-5.2` session lists the `executor` subagent.
- Static suite passes: `python -m pytest tests/ -q` (from this directory).
- Mutation score is 100%: `python scripts/mutate.py`.
- A demo run: 3+ parallel executor tasks complete, deterministic checks pass,
  per-task cost logged.

## Testing

The skill ships its own test suite — behavior is testable, not just documented.

```bash
cd delegate
python -m pytest tests/ -q            # static suite (free, fast)
python scripts/mutate.py              # mutation testing (free)
RUN_INTEGRATION=1 python -m pytest tests/test_integration.py -q   # real API call
```

- `tests/test_skill.py` — locks in SKILL.md's required behaviors: contract
  template (objetivo/entradas/restricciones/criterio_de_exito, absolute paths,
  no-delete clause), provider-prefixed setup ids, warm-up + deterministic
  validation steps, 3-line return design, and every live-failure pitfall.
- `tests/test_executor_agent.py` — locks in the agent's rules: pinned
  provider-prefixed model, restricted tools (no web, no recursion), no-delete,
  exact paths, verify-before-reporting, 3-line output format.
- `tests/test_integration.py` — spawns the real executor agent (same
  invocation as the subagent extension) on a fixture migration contract and
  validates the result deterministically. Gated by `RUN_INTEGRATION=1`
  because it costs real API money (measured: ~$0.0008 per run, and the
  report includes the exact per-run cost, tokens and cache reads).
- `scripts/mutate.py` — applies 24 single-behavior mutations to a copy of the
  skill and re-runs the static suite. Every mutation must be killed: a
  survivor means either a coverage gap or a behavior the skill no longer
  documents. If you edit the skill, run it; if you add a rule, add both a
  test and a mutation that deletes it.
