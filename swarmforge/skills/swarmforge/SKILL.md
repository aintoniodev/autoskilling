---
name: swarmforge
description: >-
  Bootstrap and operate SwarmForge swarms (Uncle Bob's tmux-based multi-agent orchestration
  for git worktrees). Choose a workflow branch (two-pack / four-pack / six-pack), install it
  in a project, configure swarmforge.conf, roles and the layered constitution, launch with
  ./swarm, drive handoffs with swarm_handoff.sh, ready_for_next.sh and done_with_current.sh,
  and shut down cleanly. Keywords: swarmforge, swarm, multi-agent, tmux, worktree, handoff,
  babashka, codex, claude, gherkin, TDD, mutation testing, orchestration.
license: MIT
compatibility: zsh, git, tmux, babashka (bb), agent backend (codex, claude, copilot or grok); macOS, Linux or WSL (Windows Terminal adapter included)
metadata:
  source-repo: https://github.com/unclebob/swarm-forge
  version: 1.0.0
---

# SwarmForge

SwarmForge is a tmux-based orchestration system for running disciplined multi-agent
development on git worktrees. A swarm is a set of terminal windows, one per agent role,
each pointed at its own worktree, each running a configured agent backend (codex, claude,
copilot or grok). Agents coordinate through a small handoff protocol — no shared
terminals, no chat channels — and the human watches the whole swarm and steers it.

This skill is the operating manual: it bootstraps a swarm into a project, explains the
configuration, and drives the handoff helpers.

## When to Use

Use SwarmForge when:

- **Several agents collaborate on the same repository**, each working in its own git
  worktree, and you want discipline: spec → code → refactor → architect (or a variant of
  that cycle).
- **You want to watch the swarm, not drive it.** Each agent runs in its own terminal
  window; you observe and intervene when a handoff stalls or a design decision needs you.
- **You need a repeatable pipeline** for a codebase: features are specified first (Gherkin
  scenarios), implemented by a coder, hardened by refactoring/QA passes, and cleaned up
  before merging.
- **Your agents support terminal CLIs** (codex, claude, copilot or grok) and you have
  tmux + Babashka available.

Do NOT use SwarmForge when:

- **A single agent can do the job.** The overhead of worktrees, roles and handoffs is not
  worth it for one-shot or solo tasks.
- **You need interactive, real-time collaboration** between agents — handoffs are
  asynchronous and file/commit based, not a chat.
- **The project cannot tolerate multiple worktrees or background daemons** (locked
  checkouts, exotic build layouts, restricted environments).
- **You work in a plain shell without tmux** or another supported terminal backend.

## Prerequisites

- **zsh** (the scripts are zsh-first; macOS and Linux ship it, WSL needs it installed)
- **git** with worktree support (2.5+)
- **tmux** (unless you supply a custom terminal backend)
- **Babashka** (`bb`) — used by the handoff daemon and helpers
- **An agent backend**: codex, claude, copilot or grok (whatever the roles in your config
  invoke)

The skill bundles everything else you need at runtime: the operational scripts live in
`scripts/`, ready-made templates in `assets/`, and full protocol/branch documentation in
`references/`. Nothing is downloaded at bootstrap time except the workflow branch tarball
(the offline bootstrap path below avoids even that).

## Native Windows (alternative stack)

This plugin ships a Windows-native alternative to the zsh/tmux/bb stack — no WSL, no
MSYS2. Verified end-to-end on Windows 11 with Git Bash:

| Upstream | Windows alternative | Install |
| --- | --- | --- |
| zsh | **bash** (Git Bash) — all `.sh` helpers are bash-compatible | Git for Windows |
| tmux | **psmux** — native Windows tmux in Rust, speaks the tmux command language, ships a `tmux` alias | `winget install psmux` |
| babashka | **bb.exe** — official native Windows build | `scripts/setup-windows.sh` (direct download) |

One command sets it up:

```sh
bash scripts/setup-windows.sh
```

Then bootstrap and launch with the native terminal backend:

```sh
bash scripts/bootstrap.sh <project-dir> four-pack
SWARMFORGE_TERMINAL=windows-native bash <project-dir>/swarmforge/scripts/swarmforge.sh
```

Notes:

- `scripts/terminal-adapters/windows-native.sh` opens Windows Terminal windows that
  attach to the psmux sessions (no `wsl.exe`).
- On Windows, bb.exe cannot `exec` a `.sh` helper directly (no shebang support in
  CreateProcess). The bundled `.bb` helpers auto-detect Windows and run their sibling
  `.bb` via `bb` instead; `scripts/` also ships `.bat` wrappers for cmd/PowerShell.
- The full handoff pipeline (validate → queue → daemon delivery → inbox) was verified
  with psmux + bb.exe on native Windows.

## Quick Start

1. **Choose a workflow** — two-pack, four-pack or six-pack. See `references/BRANCHES.md`
   for the trade-offs; the short version is in Choosing a Workflow below.
2. **Install the branch into your project** (from the project root):

   ```sh
   BRANCH=four-pack
   curl -L "https://github.com/unclebob/swarm-forge/archive/refs/heads/${BRANCH}.tar.gz" | tar -xz --strip-components=1
   ```

   This drops the `swarm`, `swarmforge/` layout, helper scripts and templates for that
   workflow into your project.
3. **Configure** — edit `swarmforge/swarmforge.conf` to point each window at an agent
   backend, worktree and initial task (see Configuration below).
4. **Launch**:

   ```sh
   ./swarm
   ```

   A tmux session opens with one window per role; each agent picks up its first task.
5. **Stop** — closing the first window tears the swarm down cleanly, or run
   `scripts/close-swarm.sh` explicitly.

**Offline bootstrap:** if the machine has no network (or you already have this skill),
install from the bundled assets instead:

```sh
scripts/bootstrap.sh <project-dir> [branch]
```

`bootstrap.sh` installs the workflow files from `assets/` and `scripts/` locally — no
curl, no network. Branch defaults to `four-pack`.

## Choosing a Workflow

| Branch | Roles | Best for |
| --- | --- | --- |
| **two-pack** | coder + cleaner | Fast iteration: code, then clean up. Minimal ceremony. |
| **four-pack** | specifier + coder + refactorer + architect | Compact full cycle with Gherkin specs: spec → code → refactor → architect review. |
| **six-pack** | specifier + coder + refactorer + architect + cleaner + hardender + QA | Complete swarm: full pipeline with cleanup, hardening and QA passes. |

The two-pack is for speed; the four-pack is the balanced default; the six-pack adds a
cleaner, a hardender and QA for production-grade output. The exact prompts, handoff
sequence and per-role artifacts for each branch are documented in `references/BRANCHES.md`.

## Configuration

Everything the swarm reads lives under `swarmforge/` in the project (installed by the
bootstrap or by the tarball).

### swarmforge.conf

One line per role window:

```
window <role> <agent> <worktree> [task|batch] [extra-cli-args...]
```

- `<role>` — the role name; a matching prompt is loaded from `swarmforge/roles/<role>.prompt`
- `<agent>` — the agent backend command (codex, claude, copilot, grok, ...)
- `<worktree>` — the worktree to run in; `master` (or `none`) means the main checkout
- `[task|batch]` — optional initial unit of work for that window
- `[extra-cli-args...]` — optional extra CLI arguments passed to the agent

### Roles

The prompt for each role lives in `swarmforge/roles/<role>.prompt`. Role prompts are
plain text; SwarmForge does not interpret them, it just passes them to the agent. Swap a
role's behavior by editing its prompt, or by overriding the file (see Local Overrides
below).

### The Layered Constitution

The swarm's behavior is governed by a constitution assembled in layers:

- `swarmforge/constitution.prompt` — the top-level constitution, which includes the
  articles below.
- `swarmforge/constitution/articles/` — one `.prompt` per article: workflow,
  engineering, project, handoffs, and so on.

Templates ship with the skill in `assets/constitution/` (the top-level `constitution.prompt`
plus a ready-made `articles/` set). At bootstrap, missing articles are installed
automatically from the templates, so a fresh project always gets the full layered set.

### Local Overrides

- **Same filename:** commit a file with the same name as a shared article into the
  project's `swarmforge/constitution/articles/`; startup skips installing the shared
  article and the local file replaces it.
- **`local-*.prompt`:** a file named `local-anything.prompt` adds to or specializes the
  matching shared article without replacing it (the `local-*` prefix means "extension,
  not full replacement"). The `assets/constitution/articles/` set ships
  `local-workflow.prompt` and `local-engineering.prompt` examples.

### Templates and Examples

- Constitution: `assets/constitution/` (base + articles)
- Role prompts per workflow: `assets/roles/<branch>/` — one `<role>.prompt` per role in
  that branch (two-pack: coder, cleaner; four-pack: specifier, coder, refactorer,
  architect; six-pack adds cleaner, hardender, QA)
- Example configs: `assets/examples/` ships `swarmforge.conf.two-pack`, `swarmforge.conf.four-pack` and `swarmforge.conf.six-pack`

## Handoff Protocol

Agents pass work to each other with three helpers in `scripts/` — they never write tmux
commands or long messages by hand:

- **`swarm_handoff.sh <draft-file>`** — validate and enqueue an outbound handoff from a
  draft file. The draft holds only headers; the helper generates the delivered payload:

  ```text
  type: git_handoff
  to: <role>[,<role>...]
  priority: NN
  task: <short-stable-task-name>
  commit: <10-char-commit-abbrev>

  # or

  type: note
  to: <role>[,<role>...]
  priority: NN
  message: <one line, max 80 chars>
  ```

  `commit` must be exactly 10 hex characters and resolve to a single commit; the helper
  canonicalizes it. Invalid drafts are rejected with the line that failed.
- **`ready_for_next.sh`** — accept the next unit of work (no arguments). Prints one of:
  - `NO_TASK` — nothing queued
  - `TASK: <path>` — a single task
  - `BATCH: <path>` — a batch of tasks
- **`done_with_current.sh`** — complete the current task or batch and move on to the next
  queued one (no arguments).

Message types:

- **`git_handoff`** — points the recipient at a committed state (commit abbreviation,
  exactly 10 hex chars).
- **`note`** — a short freeform message, max 80 characters.

Handoffs are queued under `.swarmforge/handoffs/` (outbox/sent/failed/inbox) and delivered
by the `handoffd.bb` daemon, which owns tmux socket access and sends only generic wake-up
notifications; the full wire protocol, queuing rules and validation details are in
`references/REFERENCE.md`.

## Lifecycle

- **Startup** — `./swarm` creates the worktrees under `.worktrees/`, copies the helper
  scripts into every worktree and onto the PATH, initializes state under `.swarmforge/`
  (config, handoff outbox, tmux socket name), then opens the tmux session.
- **Observation** — one terminal window per role, each running its agent inside its own
  worktree. Watch them all; the swarm is designed to be visible.
- **Stop** — close the first window: the cleanup hook runs `scripts/swarm-cleanup.sh`,
  stopping the handoff daemon and closing the session. `scripts/close-swarm.sh` does the
  same thing explicitly.
- **Resilience** — `scripts/swarm-window-watchdog.sh` (`swarm-window-watchdog.bb`) and
  `scripts/swarmforge.sh` (`swarmforge.bb`) keep the session healthy; closing a role
  window does not lose state.
- **Sleep inhibitor** — the swarm keeps the machine awake while running, so agents are
  not suspended mid-task (machines that sleep kill long agent runs).

## Custom Terminal Backends

By default the swarm drives tmux. Set `SWARMFORGE_TERMINAL` to override:

- `ghostty` — Ghostty backend
- `terminal-app` — macOS Terminal.app backend
- `windows-terminal` — Windows Terminal backend (for WSL)
- `none` — no terminal backend (headless/manual)

Adapters live in `scripts/terminal-adapters/`. A custom backend must implement the
adapter contract — the six functions the swarm calls to create, list, focus and close
windows/panes. Read an existing adapter in `scripts/terminal-adapters/` to see the
signatures; `scripts/swarm-terminal-adapter.sh` is the entry point that dispatches to
them. On native Windows, use `SWARMFORGE_TERMINAL=windows-native` (Windows Terminal +
psmux, no WSL).

## Troubleshooting

- **A window is stuck** — close that window. The watchdog reopens it and the role's state
  (worktree, config, queued handoffs) survives; nothing is lost.
- **tmux navigation** — you are inside tmux; the copy-mode (`prefix + [`) is available
  for scrolling through agent output. If the session seems frozen, check whether you are
  in copy-mode before killing anything.
- **Handoffs that never arrive** — the daemon `scripts/handoffd.bb` may have stopped.
  Check the outbox `.swarmforge/handoffs/`: if handoffs sit there undelivered, restart the
  daemon (`scripts/stop_handoff_daemon.sh` then relaunch, or restart the swarm). Messages
  are only lost if the outbox itself is removed.
- **Agents missing the helpers** — after bootstrap, scripts are synced into each worktree
  and placed on the PATH; if an agent cannot find `swarm_handoff.sh` etc., re-run the
  bootstrap for that project.

## Verification

After bootstrapping a project, confirm the swarm is healthy:

```sh
# state directory exists with config and outbox
ls .swarmforge/

# tmux session is alive (socket name comes from state)
tmux -S "$(cat .swarmforge/tmux-socket)" list-sessions

# helpers respond (they run from a role worktree; wrong args print usage/errors)
./swarmforge/scripts/swarm_handoff.sh
./swarmforge/scripts/ready_for_next.sh
./swarmforge/scripts/done_with_current.sh
```

For the helper scripts themselves, the upstream repository ships tests that run under
Babashka:

```sh
bb -cp test
```

(from the repo checkout — see `references/REFERENCE.md` for the full test and protocol
reference).
