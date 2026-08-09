# SwarmForge Workflow Branches — `two-pack`, `four-pack`, `six-pack`

> Guide to the three runnable SwarmForge workflows. Each branch carries the project-facing configuration
> (`swarmforge/swarmforge.conf`), local constitution articles, and role prompts for one workflow. At startup,
> its `./swarm` wrapper copies the shared operational scripts and shared constitution articles from `main`
> when they are not already present, then launches that branch's local configuration.
>
> Sources: the branch descriptions in the `main` README, the literal `swarmforge/swarmforge.conf` of each
> branch clone, and the role prompts in `swarmforge/roles/` of each branch clone.

---

## 1. Comparison table

| | **two-pack** | **four-pack** | **six-pack** |
|---|---|---|---|
| **Number of roles** | 2 (`coder`, `cleaner`) | 4 (`specifier`, `coder`, `refactorer`, `architect`) | 6 (`specifier`, `coder`, `cleaner`, `architect`, `hardender`, `QA`) |
| **Nickname** | Quick backend workflow | Compact specification workflow | Full workflow |
| **Choose it when** | Small tasks that benefit from fast coding without the overhead of Gherkin and acceptance testing, while still preserving backend refactoring and hardening | Moderate projects that require Gherkin specification and some architectural consideration, without splitting every quality gate into its own agent | Major projects that require full specification, up-front QA, backend verification, and significant architectural consideration |
| **Normal handoff flow** | `coder` -> `cleaner` -> `coder` | `specifier` -> `coder` -> `refactorer` -> `architect` -> `specifier` | `specifier` -> `coder` -> `cleaner` -> `architect` -> `hardender` -> `QA` -> completion |
| **Gherkin / acceptance testing** | No — deliberately absent | Yes — Gherkin specs + generated acceptance tests + soft Gherkin mutation | Yes — Gherkin specs, end-to-end QA suite, acceptance tests, Gherkin mutation |
| **Batch receive modes** | `cleaner` (batch) | `architect` (batch) | `cleaner`, `architect`, `hardender`, `QA` (batch) |
| **Fit** | Tight implementation/refinement loop without specification, QA, property-test, or acceptance-test roles | Disciplined development without splitting cleanup, architecture, hardening, and QA into separate agents | Each review and verification concern owned by a separate agent |

> **Do not use `main` for `./swarm`.** `main` is documentary and stores the shared operational scripts; the
> runnable branches provide the configurations and prompts intended for projects.

---

## 2. `two-pack` — the quick backend workflow

### When to use it

Use `two-pack` for **small tasks** that benefit from fast coding without the overhead of Gherkin and
acceptance testing, while still preserving backend refactoring and hardening. Choose it when you want a tight
implementation/refinement loop without specification, QA, property-test, or acceptance-test roles.

### Roles

- **`coder`** — implements requested behavior with TDD and unit tests; owns focused behavior slices, keeps
  production code testable, and puts IO/environment details behind small adapter boundaries.
- **`cleaner`** — consumes batches of coder handoffs as one cleanup pass; owns cleanup, duplication
  reduction, architectural structure, encapsulation, separation of concerns, and mutation hardening
  (coverage, CRAP ≤ 6, DRY, mutation over uncovered changed behavior).

### Normal flow

`coder` -> `cleaner` -> `coder`. The `coder` sends a `git_handoff` to `cleaner` at priority `50`; the
`cleaner` processes the batch, cleans and hardens, commits, and sends a `git_handoff` back to `coder` at
priority `00`. Per the handoff protocol, the intermediate role (`cleaner`) always forwards down the chain;
the return handoff to `coder` is a terminal merge.

### `swarmforge.conf` (literal)

```conf
# Format: window <role> <agent> <worktree> [task|batch] [extra-cli-args...]
# The optional receive mode defaults to task. Use batch for roles that should
# consume all currently queued equal-priority handoffs as one batch.
# Any fields after the receive mode are passed to the agent CLI, e.g. --yolo.
window coder codex master
window cleaner codex cleaner batch
```

The `coder` runs in the main working directory on `master` (no `.worktrees/coder`); the `cleaner` runs in
`.worktrees/cleaner` with `batch` receive mode. The first window (`coder`) is the cleanup window.

### Gherkin / acceptance testing

**No.** The `coder` prompt explicitly lists acceptance tests, Gherkin, IR, Gherkin mutation, property tests,
CRAP, DRY, and language mutation as things it does *not* own; the `cleaner` does not create, run, or maintain
acceptance tests, Gherkin, IR, Gherkin mutation, or property tests either. Quality work is unit-test driven
plus cleanup/CRAP/DRY/mutation hardening.

---

## 3. `four-pack` — the compact specification workflow

### When to use it

Use `four-pack` for **moderate projects** that require Gherkin specification and some architectural
consideration without splitting every quality gate into its own agent. Choose it when you want disciplined
development without splitting cleanup, architecture, hardening, and QA into separate agents.

### Roles

- **`specifier`** — turns user intent into precise Gherkin acceptance specifications and **asks for approval
  before handoff**; writes concise deterministic specs in the Gherkin format defined by
  `github.com/unclebob/Acceptance-Pipeline-Specification` (five-phase feature workflow, including
  `ir-dry-checker` pruning and `Background` extraction).
- **`coder`** — implements approved behavior slices with TDD, unit tests, and generated acceptance tests;
  installs the acceptance pipeline (`gherkin-parser`) and keeps generated acceptance tests separate from unit
  tests.
- **`refactorer`** — performs behavior-preserving cleanup, coverage improvement, CRAP and DRY review,
  mutation-site scans (splitting files above 100 mutation sites), and property-test support.
- **`architect`** — owns high-level structure, dependency direction, mutation hardening, DRY review, soft
  Gherkin mutation (`--level soft`), and final completion notification (sends `git_handoff` to coder and
  refactorer at priority `00` when they have follow-up work; only sends to specifier when there is a
  functional commit, and never sends `note` handoffs to the specifier). It processes refactorer work in the
  shape delivered by `ready_for_next.sh` — a `BATCH` is processed item by item as one architectural review
  batch, a `TASK` as a single task.

### Normal flow

`specifier` -> `coder` -> `refactorer` -> `architect` -> `specifier`. The `specifier` commits the approved
specification with a short stable task name and hands off to `coder`; `coder` hands off to `refactorer`;
`refactorer` hands off to `architect`; when the job is complete, `architect` notifies `specifier`, who merges
the changes and asks the user for the next feature.

### `swarmforge.conf` (literal)

```conf
# Format: window <role> <agent> <worktree> [task|batch] [extra-cli-args...]
# The optional receive mode defaults to task. Use batch for roles that should
# consume all currently queued equal-priority handoffs as one batch.
# Any fields after the receive mode are passed to the agent CLI, e.g. --yolo.
window specifier codex master
window coder codex coder
window refactorer codex refactorer
window architect codex architect batch
```

The `specifier` runs in the main working directory on `master` and is the cleanup window; `coder` and
`refactorer` run in their own worktrees; `architect` runs in `.worktrees/architect` with `batch` receive mode
(the handoff protocol names four-pack `architect` as a batch-mode role).

### Gherkin / acceptance testing

**Yes.** Gherkin is central: the specifier writes Gherkin acceptance specifications, the coder generates and
runs acceptance tests via the APS pipeline, and the architect performs soft Gherkin acceptance mutation as
part of the final verification sequence. Property tests are supported by the refactorer.

---

## 4. `six-pack` — the full workflow

### When to use it

Use `six-pack` for **major projects** that require full specification, up-front QA, backend verification, and
significant architectural consideration. Choose it when you want each review and verification concern owned
by a separate agent.

### Roles

- **`specifier`** — turns user intent into accepted Gherkin specifications **and end-to-end QA procedures**
  (six-phase feature workflow: Gherkin, pruning, `ir-dry-checker`, `Background`, end-to-end QA suite at the
  user-interface level, then user approval before handoff).
- **`coder`** — implements approved behavior slices with TDD, unit tests, and generated acceptance tests;
  ignores the specifier's end-to-end QA suite (does not implement, run, or maintain QA-suite checks).
- **`cleaner`** — performs local behavior-preserving cleanup, coverage improvement, CRAP and DRY review, and
  mutation-site scans (name clarity, cohesion, duplication, dead code, local error paths, splitting files
  above 100 mutation sites); processes each `BATCH_ITEM` delivered by `ready_for_next.sh` in order.
- **`architect`** — reviews module structure, boundaries, dependency direction, and property-test coverage;
  adds lightweight automated architecture checks (dependency-direction, forbidden-import, import-cycle,
  adapter-boundary) when practical; processes cleaner work in the shape delivered by `ready_for_next.sh`.
- **`hardender`** — performs mutation hardening (language mutation one file at a time, differential mutation
  against the manifest, `--max-workers 8`), language mutation, CRAP and DRY verification, and soft Gherkin
  mutation; keeps hardening tests separate from unit and acceptance tests; processes architect work in the
  shape delivered by `ready_for_next.sh`.
- **`QA`** — converts the specifier's QA procedures into executable scripts, runs final user-interface
  verification (never through a project API), checks handoff consistency (handoff commits, manifests, and
  audit files), fixes bugs found, and sends completion notifications to the specifier, coder, cleaner,
  architect, and hardender with `priority: 00`; processes hardender work in the shape delivered by
  `ready_for_next.sh`.

### Normal flow

`specifier` -> `coder` -> `cleaner` -> `architect` -> `hardender` -> `QA` -> completion. Each intermediate
role always forwards a `git_handoff` to the next role in the chain; when `QA` is complete it notifies all the
other roles, and each recipient merges only (terminal broadcast, not re-forwarded). The specifier merges the
changes when `QA` notifies it that the job is complete and asks the user for the next feature.

### `swarmforge.conf` (literal)

```conf
# Format: window <role> <agent> <worktree> [task|batch] [extra-cli-args...]
# The optional receive mode defaults to task. Use batch for roles that should
# consume all currently queued equal-priority handoffs as one batch.
# Any fields after the receive mode are passed to the agent CLI, e.g. --yolo.
window specifier codex master
window coder codex coder
window cleaner codex cleaner batch
window architect codex architect batch
window hardender codex hardender batch
window QA codex QA batch
```

The `specifier` runs in the main working directory on `master` and is the cleanup window; every other role
runs in its own worktree, and the four downstream review roles (`cleaner`, `architect`, `hardender`, `QA`)
use `batch` receive mode (the handoff protocol explicitly names all four as batch-mode roles).

### Gherkin / acceptance testing

**Yes, fullest form.** Gherkin specification, generated acceptance tests, soft Gherkin acceptance mutation,
and an end-to-end QA suite specified by the specifier and executed by `QA` through the user interface only.
Property tests are owned by the architect. If the QA suite contradicts the Gherkin or unit tests, `QA` stops
and asks for clarification before changing behavior.

---

## 5. Getting started (all branches)

```sh
BRANCH=four-pack
curl -L "https://github.com/unclebob/swarm-forge/archive/refs/heads/${BRANCH}.tar.gz" | tar -xz --strip-components=1
```

Use `BRANCH=two-pack`, `BRANCH=four-pack`, or `BRANCH=six-pack`. Then start the swarm from the target
project with `./swarm` (the wrapper downloads the shared scripts from `main` on first use). To stop the
swarm, close the first window listed in `swarmforge/swarmforge.conf`.
