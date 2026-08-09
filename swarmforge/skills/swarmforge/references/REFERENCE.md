# SwarmForge — Technical Reference

> **A disciplined tmux-based agent orchestration platform that turns swarms of AI agents into reliable, professional software engineers.**

This reference is a faithful technical summary of the SwarmForge project as documented in the `main` branch
(`README.md`) and in `swarmforge/handoff-protocol.md` (the canonical handoff protocol document). It does not
invent features: everything below is sourced from those two documents, plus the runnable branch layouts
(`two-pack`, `four-pack`, `six-pack`).

---

## 1. Architecture & Rationale

SwarmForge is an agent coordination system that facilitates communication between agents working in **different
git worktrees**. It provides a shared structure for role-specific prompts, worktree assignment, tmux sessions,
and message passing so multiple agents can collaborate on the same project **without stepping on each other**.

### Why it exists

- Multiple AI agents working on one project conflict unless they are isolated from each other. SwarmForge gives
  each role its own git worktree and its own tmux session.
- Agents communicate through **handoff files**, not by typing at each other in a shared terminal.
- A dedicated daemon owns the tmux socket, so agents never need tmux permissions and never send raw tmux
  commands.

### Branch model

- **`main` is documentary.** It explains the system and carries the **shared operational scripts**
  (`swarmforge/scripts/`) and the **default constitution articles**
  (`swarmforge/constitution/articles/`).
- **Runnable workflow branches** (`two-pack`, `four-pack`, `six-pack`) carry the project-facing configuration:
  `swarmforge/swarmforge.conf`, local constitution articles, and role prompts for one workflow.
- At startup, the branch's `./swarm` wrapper copies the shared operational scripts and shared constitution
  articles from `main` when they are not already present, then launches that branch's local configuration.

### What SwarmForge does (feature summary)

- Launches a **config-driven swarm** from a project-local `swarmforge/swarmforge.conf`.
- Creates one tmux session per configured role and opens a terminal surface for each role when the selected
  backend supports it.
- Reads behavior from project-local `swarmforge/roles/<role>.prompt` files plus a layered
  `swarmforge/constitution.prompt`.
- Supports per-role backends such as `claude`, `codex`, `copilot`, or `grok`.
- Puts the shared `swarmforge/scripts/` directory on each agent's `PATH`, including the handoff helpers.
- Creates git worktrees under `.worktrees/` for roles assigned to dedicated worktree names.
- Initializes a git repository in a new working directory when needed.
- Keeps all swarm state local to the working directory in `.swarmforge/`.

### Prerequisites

The target machine needs: `zsh`, `git`, `tmux`, Babashka (`bb`), and at least one configured agent backend
such as `codex`, `claude`, `copilot`, or `grok`.

---

## 2. The Handoff Protocol

> Source: `swarmforge/handoff-protocol.md` (the canonical protocol document) and the "Handoff Protocol"
> section of `README.md`.

### 2.1 Goal

Replace direct agent access to the tmux socket with a **daemon-owned file transport**. Agents should not send
tmux commands, manage socket permissions, or maintain a separate logbook. Agents create small, **validated**
handoff requests; the daemon delivers them through durable inbox files and sends only wake-up notifications
through tmux.

### 2.2 Core principle: what agents never do

The helper scripts generate the delivered payload. **Agents do not write long handoff bodies, branch names,
queue filenames, or tmux commands.** Agents should not hand-edit, merge, stage, or commit handoff runtime
state, and they should not manually move inbox files.

### 2.3 Directory layout

Each agent worktree owns this structure under `.swarmforge/handoffs/`:

```text
.swarmforge/handoffs/
  outbox/
    tmp/
  sent/
  failed/
  inbox/
    new/
    in_process/
    completed/
```

- The daemon consumes `outbox/` (only final `.handoff` files directly under `outbox/`; it ignores
  `outbox/tmp/`).
- Agents consume `inbox/new/` through helper scripts.
- `sent`, `failed`, `in_process`, and `completed` provide the audit trail and restart state.

### 2.4 The two message types

Agents may request only two message types. The helper generates the delivered payload.

#### `git_handoff`

Used when a role has committed work for another role to merge and process. Draft format:

```text
type: git_handoff
to: <role>[,<role>...]
priority: NN
task: <short-stable-task-name>
commit: <10-character-commit-abbrev>
```

The `task` name is a short, stable human-readable name that follows the work through downstream git handoffs
for the same task. The commit abbreviation must be **exactly 10 hexadecimal characters**; `swarm_handoff.sh`
validates that it resolves to a single commit and canonicalizes it before queuing the handoff.

#### `note`

One short freeform message. Draft format:

```text
type: note
to: <role>[,<role>...]
priority: NN
message: <one line, max 80 chars>
```

The `message` value must be a single line no longer than 80 characters. Agents should not send `note`
handoffs unless the user, role prompt, or constitution explicitly directs them to send one; when blocked by
ambiguity, contradiction, or test/specification conflict, an agent should stop and ask for clarification.

#### Delivered handoff example

```text
id: 20260615T140531Z_000042_from_coder
from: coder
to: cleaner
recipient: cleaner
priority: 50
type: git_handoff
role: coder
task: task-1-cave-setup
commit: a1b2c3d9
created_at: 2026-06-15T14:05:31Z
enqueued_at: 2026-06-15T14:05:32Z

Re-read your role and constitution.

merge_and_process coder a1b2c3d9
```

For broadcast handoffs, `to` preserves the full recipient list and `recipient` identifies the specific
recipient copy.

### 2.5 Filename format

Handoff filenames sort by priority, timestamp, and sequence:

```text
<priority>_<timestamp>_<sequence>_from_<sender>_to_<recipient-list>.handoff
```

Example:

```text
00_20260615T140531Z_000042_from_architect_to_coder_cleaner_QA.handoff
```

Rules: lower priority numbers are processed first; `priority` is two digits `00`–`99`; `timestamp` is UTC in
`YYYYMMDDTHHMMSSZ` format; `sequence` is a per-worktree counter that breaks ties within the same second;
recipients remain in the filename for audit. Scripts parse authoritative metadata from file **headers**, not
from the filename. Startup validation rejects role names containing underscores so recipient lists stay
readable in audit filenames.

### 2.6 The three helpers (agent-facing surface)

Agents interact with handoffs through exactly three helper scripts, synced into every role worktree under
`swarmforge/scripts/` and placed on `PATH`:

| Helper | Purpose |
|---|---|
| `swarm_handoff.sh <draft-file>` | The strict outbound protocol gate: validates and queues outbound handoffs. |
| `ready_for_next.sh` | Accepts work using the role's configured receive mode. |
| `done_with_current.sh` | Completes the current task or batch using the role's configured receive mode. |

Internal dispatchers/queue-state owners (also part of the protocol): `ready_for_next_task.sh`,
`ready_for_next_batch.sh`, `done_with_current_task.sh`, `done_with_current_batch.sh`, and the daemon
`handoffd` itself.

#### `swarm_handoff.sh` responsibilities

- Read a draft handoff file and validate all fields; emit detailed repair guidance for malformed drafts.
- Reject reserved headers supplied by agents: `id`, `from`, `role`, `recipient`, `created_at`, `enqueued_at`,
  `dequeued_at`, `completed_at`.
- Infer `from` from the current agent/worktree; validate `to` against configured agents.
- Generate `id`, `created_at`, filename timestamp, and sequence; serialize sequence updates with an atomic
  lock so concurrent handoff creation in one worktree cannot reuse the same sequence.
- Validate `priority` as `00` through `99`; validate `type` as `git_handoff` or `note`.
- Validate `git_handoff` commits as real, unambiguous commits and canonicalize valid abbreviations.
- Generate `role` from the current sender role and preserve `task` from the draft for `git_handoff`.
- Generate the canonical body and atomically install the file into `outbox/` (write to
  `outbox/tmp/<filename>.tmp`, flush and close, then rename to `outbox/<filename>.handoff`).

Validation errors are explicit enough for an agent to repair the draft, e.g.:

```text
HANDOFF INVALID: ./tmp/handoff.txt

Errors:
- Line 3: `priority` must be two digits from 00 to 99; got `urgent`.
- Header `completed_at` is reserved and must not be written by agents.
- message: commit `a1b2c3` is ambiguous; use at least 9 characters.
```

#### Commit validation rules

For `git_handoff`, `swarm_handoff.sh` validates the commit abbreviation with Git. The abbreviation must be
hexadecimal, exactly 10 characters, resolve to exactly one object, and that object must be a commit. The
script writes a canonical abbreviation into the queued handoff. This prevents agents from sending corrupted or
ambiguous SHA abbreviations.

### 2.7 The handoff daemon (`handoffd.bb`)

- Implemented in **Babashka** (mostly filesystem traversal, parsing, sorting, renaming, and subprocess calls).
- Started by the swarm launcher alongside the tmux session; it has **direct access to the tmux socket**.
- Responsibilities:
  - Discover configured agents and worktrees; poll each agent `outbox/`.
  - Process only complete `.handoff` files, never files in `outbox/tmp/`.
  - Copy each handoff to every recipient `inbox/new/`, adding `recipient` and `enqueued_at` to each copy.
  - Send a **generic tmux wake-up message** to each recipient — the message never names the delivered file,
    to avoid biasing the recipient toward one file and to force queue-order processing.
  - Move the original outbox file to `sent/` after successful delivery; move malformed or undeliverable files
    to `failed/` with useful diagnostics; avoid duplicate delivery when retrying after interruption.

Example tmux wake-up:

```text
You have new handoff mail. If idle, run ready_for_next.sh.
```

### 2.8 Receive modes: `task` and `batch`

`swarmforge.conf` window lines may include an optional receive mode (`task` or `batch`); when omitted it
defaults to `task`. The launcher writes the normalized mode into `.swarmforge/roles.tsv`, and the receive
helpers read that runtime file rather than reparsing `swarmforge.conf`. `batch` is for roles that should
consume all currently queued equal-priority handoffs as one unit — e.g. six-pack `cleaner`, `architect`,
`hardender`, and `QA`, and four-pack `architect`.

### 2.9 Queue helper behavior and printed responses

- **`ready_for_next.sh`** reads the current role from `SWARMFORGE_ROLE`, reads that role's receive mode from
  `.swarmforge/roles.tsv`, and dispatches to `ready_for_next_task.sh` (task mode) or
  `ready_for_next_batch.sh` (batch mode). The task/batch helpers are the single owners of queue-selection
  logic: check `inbox/in_process/` first (refusing ambiguous states such as multiple in-process items unless
  an explicit repair is made outside the helper), then select the first file in `inbox/new/` by sorted
  filename order, atomically move it (task) or the full equal-priority set (batch) into `inbox/in_process/`,
  add/update `dequeued_at`, and print the result.
- **`done_with_current.sh`** dispatches to the matching done helper, which requires exactly one in-process
  item of the matching kind, adds/updates `completed_at`, moves the file(s) to `inbox/completed/`, prints the
  completed path(s), then calls the corresponding ready helper and passes through its output.
- **Printed responses** the agent must understand:
  - `NO_TASK` — no work available; stop waiting for work.
  - `TASK: <path>` — treat the printed `TASK_NAME` and `PAYLOAD` as the task.
  - `BATCH: <path>` — process the printed `BATCH_ITEM` entries in helper-delivered order.

Example `ready_for_next_task.sh` success:

```text
TASK: .swarmforge/handoffs/inbox/in_process/00_20260615T140531Z_000042_from_architect_to_coder.handoff
FROM: architect
TYPE: git_handoff
PRIORITY: 00
TASK_NAME: task-1-cave-setup
PAYLOAD:
Re-read your role and constitution.

merge_and_process architect a1b2c3d9
```

### 2.10 Agent queue rules (prompt-level loop)

1. When notified, run `ready_for_next.sh`.
2. Let it dispatch according to the receive mode configured for your role.
3. If it prints `NO_TASK`, stop waiting for work.
4. If it prints `TASK: <path>`, treat the printed `PAYLOAD` as the task.
5. If it prints `BATCH: <path>`, treat each printed `BATCH_ITEM` as part of the current batch in
   helper-delivered order.
6. Use only the task information printed by the helper scripts.
7. If a tmux wake-up arrives while already working on a task, ignore it.
8. When the task or batch is fully complete, run `done_with_current.sh`.
9. Treat `note` handoffs as tasks too; after reading or acting on a note, run `done_with_current.sh` before
   accepting any other handoff.
10. If a done helper prints `TASK:`/`BATCH:`, treat it as the next task/batch; if it prints `NO_TASK`, stop
    waiting for work.

On restart, an agent runs `ready_for_next.sh` and follows its output. Tmux wake-ups are intentionally
lossy — they only prompt an idle agent to check its durable inbox; a busy agent can ignore them because task
completion also checks the queue and accepts the next task in priority order.

### 2.11 Audit trail and lifecycle header ownership

The file system state and handoff headers replace the old logbook and resend queue. Important headers:
`id`, `from`, `to`, `recipient`, `priority`, `type`, `created_at`, `enqueued_at`, `dequeued_at`,
`completed_at`. Ownership:

- `swarm_handoff.sh` writes `id`, `from`, `to`, `priority`, `type`, `created_at`.
- `handoffd` writes `recipient` and `enqueued_at` into each recipient copy.
- `ready_for_next_task.sh` / `ready_for_next_batch.sh` write `dequeued_at`.
- `done_with_current_task.sh` / `done_with_current_batch.sh` write `completed_at`.

### 2.12 Chain forwarding and terminal broadcast

Intermediate roles in a pack pipeline **must always forward** a `git_handoff` to the next role in the chain
after completing the inbound task, regardless of what changed — manifest-only, audit-only, generated metadata,
formatting-only, and other non-functional churn still require a forward:

- `two-pack`: `coder` -> `cleaner` -> `coder`; `cleaner` always forwards to `coder`.
- `four-pack`: `specifier` -> `coder` -> `refactorer` -> `architect` -> `specifier`; each intermediate role
  always forwards to the next.
- `six-pack`: `specifier` -> `coder` -> `cleaner` -> `architect` -> `hardender` -> `QA`; each intermediate
  role always forwards to the next.

Only the **end-of-chain handoff sent to multiple recipients** is not forwarded further. Each recipient merges
that commit (`merge_and_process`) and stops; recipients do not re-forward that handoff down the chain
(two-pack: `cleaner`'s return handoff to `coder`; four-pack: `architect`'s return handoff to `specifier`;
six-pack: `QA`'s completion handoff to the other roles).

### 2.13 Daemon shutdown

The swarm launcher owns the daemon lifecycle. Startup starts the daemon after creating or discovering the
tmux session and writes runtime files under `.swarmforge/daemon/`:

```text
.swarmforge/daemon/
  handoffd.pid
  handoffd.log
  stop
```

Shutdown: the launcher sends `TERM`; the daemon traps `TERM`, finishes any current delivery transaction,
removes its PID file, logs shutdown, and exits. `stop` is a secondary shutdown mechanism. Delivery is
transaction-like: detect an outbox file, copy it to all recipient inboxes, send wake-up notifications, move
the original to `sent/`; if interrupted before completion, retry without duplicating already delivered
recipient copies.

### 2.14 Finalized decisions

- The handoff daemon is written in Babashka.
- Git handoff commit abbreviations are exactly 10 hexadecimal characters.
- `note` handoffs have no optional classification field.
- Helper scripts do not provide recovery modes for ambiguous queue state.
- The daemon does not perform a second full validation pass on outbox files; `swarm_handoff.sh` is the
  validation boundary.

---

## 3. The `swarmforge.conf` File

`swarmforge/swarmforge.conf` defines the swarm **window-by-window**. Each line has this form:

```conf
window <role> <agent> <worktree> [task|batch] [extra-cli-args...]
```

- The optional receive mode defaults to `task`. Use `batch` for roles that should consume all currently
  queued equal-priority handoffs as one batch.
- Any fields after the receive mode are passed directly to the agent CLI as additional arguments. If you omit
  the receive mode, extra arguments may start at the fifth field:

```conf
window coder copilot wt-coder --yolo
window architect claude wt-arch task --dangerously-skip-permissions
```

- You can define as many windows as your project needs. Each `role` maps to a corresponding prompt file at
  `swarmforge/roles/<role>.prompt` — a config containing `architect`, `coder`, `reviewer`, `research`, and
  `release` windows expects `swarmforge/roles/architect.prompt`, `coder.prompt`, `reviewer.prompt`,
  `research.prompt`, and `release.prompt`. This lets each project choose its own swarm shape.

Example config (from the README):

```conf
window coordinator codex master
window coder codex coder
window refactorer codex refactorer
window architect codex architect
```

In this example: `coordinator` runs in the main working directory on `master` and is the cleanup window
because it is listed first; `coder`, `refactorer`, and `architect` run in `.worktrees/coder`,
`.worktrees/refactorer`, `.worktrees/architect`. If a window uses `master` as its worktree name, SwarmForge
does **not** create `.worktrees/master`; that role runs in the main working directory on the `master` branch.
Roles assigned to `none` likewise get no worktree.

---

## 4. Worktrees and Startup

At startup, in a runnable branch:

1. SwarmForge reads `swarmforge/swarmforge.conf`.
2. The root `./swarm` wrapper copies shared helper scripts, terminal adapters, and shared constitution
   articles from the `main` branch when they are not already present (later runs reuse the existing local
   scripts directory instead of overwriting it).
3. Startup installs missing shared constitution articles into `swarmforge/constitution/articles/`, skipping
   any local article file that already exists.
4. Startup validates the configured role prompts, helper scripts, and terminal adapters.
5. If the target directory is not already a git repository, startup initializes one and creates the first
   commit.
6. Startup creates one git worktree per configured role under `.worktrees/`, unless the role is assigned to
   `master` or `none`.
7. Startup syncs `swarmforge/scripts/` and missing shared constitution articles into each role worktree and
   puts that local scripts directory on each agent's `PATH`, so agents use local handoff helpers without
   reaching back into the master checkout.
8. SwarmForge creates tmux sessions, opens terminal windows, and launches each configured backend in its
   assigned worktree.
9. Startup starts an OS-specific sleep inhibitor when one is available; cleanup stops it with the swarm.
10. Roles communicate through daemon-delivered handoff files (see Section 2).

Runtime state lives under `.swarmforge/` in the working directory and inside each worktree:

- `.swarmforge/tmux-socket` — the project-specific tmux socket path (each project swarm is isolated from
  other tmux sessions).
- `.swarmforge/roles.tsv` — normalized role/receive-mode table written by the launcher; receive helpers read
  this instead of reparsing `swarmforge.conf`.
- `.swarmforge/sessions.tsv` and `.swarmforge/window-ids` — used by the cleanup/close machinery to track
  tmux sessions and terminal window ids.
- `.swarmforge/daemon/` — daemon PID, log, and stop file.
- `.swarmforge/handoffs/` — the durable queue state described in Section 2.3.

---

## 5. tmux Behavior

- SwarmForge uses a **project-specific tmux socket** recorded in `.swarmforge/tmux-socket`, isolating each
  project swarm from other tmux sessions.
- It honors tmux `base-index` and `pane-base-index` settings when launching agents and sending notifications,
  so configurations that number windows or panes from `1` work without requiring users to change their tmux
  preferences.
- Each visible agent window is attached to a tmux session: terminal selection, copy, and paste may follow
  tmux and terminal-emulator rules rather than ordinary text-field behavior.

### Window lifecycle

- **The first window in `swarmforge.conf` is the cleanup window.** Closing that top configured window is the
  intentional shutdown path: SwarmForge tears down the tmux sessions, closes the remaining tracked windows,
  and shuts down the swarm (including the daemon and the sleep inhibitor).
- **Closing any other tracked window is non-destructive.** The watchdog (`swarm-window-watchdog.bb`) reopens
  that window and attaches it back to the same tmux session, so agent state and terminal history remain
  intact. This is often the simplest way to recover a window that has landed in an unfamiliar tmux mode or
  otherwise feels stuck.

---

## 6. Terminal Behavior and the Backend Adapter Contract

SwarmForge opens trackable terminal windows or tabs through a small terminal backend adapter
(`swarmforge/scripts/swarm-terminal-adapter.sh` plus per-backend files under
`swarmforge/scripts/terminal-adapters/`).

### Default detection

1. If AppleScript is available → open macOS **Terminal.app** windows.
2. Otherwise, if `wt.exe` is available → open **Windows Terminal** windows.
3. Otherwise → attach the cleanup tmux session in the current shell.

### Override

Set `SWARMFORGE_TERMINAL` before `./swarm`:

```sh
SWARMFORGE_TERMINAL=ghostty ./swarm
SWARMFORGE_TERMINAL=terminal-app ./swarm
SWARMFORGE_TERMINAL=windows-terminal ./swarm
SWARMFORGE_TERMINAL=none ./swarm
```

`ghostty` opens Ghostty tabs instead of the default Terminal.app windows; `windows-terminal` opens Windows
Terminal windows from WSL; `none` skips terminal automation and attaches the cleanup tmux session in the
current shell.

### Adding a terminal backend

Shared terminal backends are carried on `main` under `swarmforge/scripts/terminal-adapters/` and copied by
runnable branches at startup. To add a backend, create one file named after the backend, e.g.
`swarmforge/scripts/terminal-adapters/wezterm.sh`, defining this contract:

```sh
terminal_backend_label() {
  echo "WezTerm"
}

terminal_backend_can_open_sessions() {
  return 0
}

terminal_backend_tracks_windows() {
  return 0
}

terminal_open_session() {
  local session="$1"
  local title="$2"
  local sibling_id="${3:-}"

  # Open a terminal surface that runs:
  # cd "$WORKING_DIR" && exec tmux -S "$TMUX_SOCKET" attach-session -t "$session"
  #
  # Print a stable window/tab id to stdout.
}

terminal_window_exists() {
  local window_id="$1"

  # Return 0 if the id from terminal_open_session still exists.
  # Return nonzero otherwise.
}

terminal_close_window() {
  local window_id="$1"

  # Close the id from terminal_open_session.
}
```

Capability combinations:

- **Open + track** (`can_open_sessions` = 0, `tracks_windows` = 0): full open/check/close cycle with the
  watchdog.
- **Launch-only** (`can_open_sessions` = 0, `tracks_windows` = 1): the terminal can open sessions but cannot
  return stable ids; SwarmForge opens one surface per session and **skips the watchdog** for that backend.
  `swarmforge/scripts/terminal-adapters/windows-terminal.sh` is the example of this style.
- **Cannot open sessions** (both `return 1`): SwarmForge attaches the cleanup tmux session in the current
  shell.

Only edit `swarmforge/scripts/swarm-terminal-adapter.sh` when adding aliases or changing default
auto-detection.

---

## 7. Layered Constitution

Each runnable branch contains a `swarmforge/` directory with this general layout:

```text
swarmforge/
  swarmforge.conf
  constitution.prompt
  constitution/
    articles/
      project.prompt
      local-engineering.prompt
      local-workflow.prompt
      ...
  roles/
    <role>.prompt
    ...
```

- **`constitution.prompt` is the entry point.** Runnable branches normally use it to tell agents to read every
  file in `swarmforge/constitution/articles/` (e.g. two-pack's file reads: "This file takes precedence over
  article files. Read and obey every file in `swarmforge/constitution/articles/`.").
- **Shared default articles** live on `main` under `swarmforge/constitution/articles/`:
  `engineering.prompt`, `handoffs.prompt`, `workflow.prompt`.
- At startup, SwarmForge installs missing shared articles into the runnable branch's articles directory
  before creating role worktrees, and also installs missing shared articles into each role worktree during
  script synchronization. Existing local files are skipped, so a runnable branch can **override** a shared
  article by committing an article with the same filename.
- Pack-specific additions and exceptions should use explicit local filenames rather than editing shared
  articles. Current conventions:
  - `project.prompt` — the workflow's project shape and local topology.
  - `local-engineering.prompt` — workflow-specific engineering rules.
  - `local-workflow.prompt` — workflow-specific flow rules.
- The `local-*.prompt` naming convention means "add to or specialize the shared default article for this
  runnable branch" — use it when the shared article remains valid and the branch only needs extra
  requirements, exceptions, or narrower instructions. Do **not** use `local-*.prompt` for a full replacement;
  use the shared filename instead when the branch intentionally overrides the shared article.

Example: `main` provides a shared `workflow.prompt`, while `six-pack` adds `local-workflow.prompt` for
QA-specific handoff behavior. If a branch needs to replace the shared workflow article completely, it can
commit its own `workflow.prompt`; startup treats that local file as an override and does not copy the shared
one over it.

---

## 8. Sleep Prevention

While a swarm is active, SwarmForge tries to prevent the host from sleeping:

- On macOS it uses `caffeinate`.
- On Linux it uses `systemd-inhibit` when available.
- Display lock or manual sleep can still interrupt agents depending on the OS.
- Set `SWARMFORGE_PREVENT_SLEEP=0` before `./swarm` to disable this behavior. Cleanup stops the inhibitor
  with the swarm.

---

## 9. Troubleshooting

### A window feels stuck

Each visible agent window is attached to a tmux session, so terminal selection, copy, and paste may follow
tmux and terminal-emulator rules rather than ordinary text-field behavior. If copy or paste feels unusual,
**check whether tmux copy mode is active before assuming the agent is stuck.**

### Recover a stuck (non-cleanup) window

Closing any tracked window other than the first is **non-destructive**: the watchdog reopens the window and
attaches it back to the same tmux session, preserving agent state and terminal history. This is often the
simplest recovery path for a window that has landed in an unfamiliar tmux mode or otherwise feels stuck.

### Shut the swarm down cleanly

Close the **first window** listed in `swarmforge/swarmforge.conf` — that cleanup window shuts down the tmux
sessions and closes the remaining tracked windows (the cleanup machinery uses `.swarmforge/sessions.tsv` and
`.swarmforge/window-ids`). The daemon and sleep inhibitor are torn down with the swarm.

### An agent is not receiving handoffs

Work through, in order:

1. **Is the daemon running?** Check `.swarmforge/daemon/handoffd.pid` and `.swarmforge/daemon/handoffd.log`
   under the project root. The daemon (`handoffd.bb`) is started by the launcher after the tmux session is
   created and must own all inbox delivery.
2. **Is the outbound handoff stuck?** Check the sender's `.swarmforge/handoffs/outbox/` (a final `.handoff`
   file should be consumed quickly) and `.swarmforge/handoffs/failed/` (malformed or undeliverable files land
   there with diagnostics). `swarm_handoff.sh` is the validation boundary, so a failed file usually indicates
   a bad draft — the validation error output tells the agent how to repair it.
3. **Queue state on the recipient side.** Check `.swarmforge/handoffs/inbox/` in the recipient worktree:
   `new/` for undelivered mail, `in_process/` for a task/batch that was accepted but never completed
   (helpers refuse ambiguous in-process state; the agent must resume or complete it before accepting new
   work), and `completed/` for the audit trail.
4. **Runtime role/mode files.** Confirm `.swarmforge/roles.tsv` exists with the role's normalized receive
   mode; `ready_for_next.sh` reads it rather than `swarmforge.conf`.

### Agent-side startup hygiene

Agents work only in their assigned branch/worktree, use `./tmp/` (never `/tmp`) for temporary files, and must
not run `./swarm` from an agent worktree to repair helper scripts — if handoff helper scripts are missing
from `PATH`, the agent should stop and report the startup failure.

---

## 10. Native Windows Stack (no WSL)

The bundled scripts are bash-compatible and ship an alternative to the zsh/tmux/bb stack
that runs on native Windows with Git Bash:

- **bash** replaces zsh. All `.sh` helpers use `#!/usr/bin/env bash` and avoid zsh-only
  syntax (the one numeric-glob `[[ x == <-> ]]` was replaced with a POSIX regex).
- **psmux** replaces tmux. psmux is a native Windows terminal multiplexer (Rust, ConPTY)
  that speaks the tmux command language and ships `psmux`, `pmux` and `tmux` binaries
  (`winget install psmux`). All commands used by the swarm (`new-session -d -s`,
  `send-keys -l/-N`, `show-options -gqv`, `display-message -p`, `rename-window`,
  `kill-session`, `list-sessions -F`, `-S <socket>`) are supported.
- **bb.exe** replaces bb. Babashka ships official native Windows builds; download the
  `windows-amd64.zip` from GitHub releases. `scripts/setup-windows.sh` automates this.

Windows adaptations in the bundled scripts:

- `run-helper!` in `ready_for_next.bb` / `done_with_current.bb` and the follow-on dispatch
  in `done_with_current_task.bb` / `done_with_current_batch.bb` detect Windows and exec the
  sibling `.bb` via `bb` instead of the `.sh` (bb cannot exec shebang scripts on Windows).
- `start-handoff-daemon!` in `swarmforge.bb` runs `bb handoffd.bb` on Windows.
- The terminal-adapter dispatcher runs `bash -c` instead of `zsh -c`.
- `scripts/terminal-adapters/windows-native.sh` opens Windows Terminal windows that attach
  to the psmux session directly (no `wsl.exe`); select with
  `SWARMFORGE_TERMINAL=windows-native`.
- `.bat` wrappers (e.g. `ready_for_next.bat`) allow invoking helpers from cmd/PowerShell.

The full handoff pipeline (validate → queue → daemon delivery → recipient inbox) was
verified end-to-end on Windows 11 with psmux + bb.exe + Git Bash. The upstream test suite
(`bb test`) targets POSIX exec semantics and cannot run unmodified on Windows; validate
with the manual E2E flow instead.

## Appendix: sources

- `README.md` on `main` — architecture, branches, `swarmforge.conf`, tmux/terminal/window behavior,
  constitution layering, sleep prevention.
- `swarmforge/handoff-protocol.md` — the canonical handoff protocol: message types, helpers, daemon, queue
  rules, audit trail, finalized decisions.
- Runnable branch clones: `swarmforge/swarmforge.conf` and `swarmforge/roles/*.prompt` per branch (see
  `BRANCHES.md`).
