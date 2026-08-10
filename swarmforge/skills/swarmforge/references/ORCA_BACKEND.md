# orca backend — full integration guide

How to run a SwarmForge swarm with **orca** as the agent backend, verified
end-to-end on native Windows (Git Bash + psmux) on 2026-08-10 with a live
four-pack swarm (4 roles, 4 real handoffs, 3 generations of a GP benchmark).

The stock backends (`codex`, `claude`, `copilot`, `grok`) are agent TUIs that
run directly inside the SwarmForge tmux window. **orca is a control CLI**: it
creates terminals, sends keystrokes and reads output, but is not itself an
agent. The bridge is `scripts/orca-agent-driver.sh` — it runs in the role
window, owns one orca terminal bound to the role worktree, drives a headless
agent (`pi -p` by default) per task, streams output into the window, and
mediates the handoff queue between tasks.

## Wiring

1. **Patch `swarmforge.bb`** (project copy):
   - `parse-config` whitelist: add `"orca"` to
     `#{"claude" "codex" "copilot" "grok"}`.
   - `launch-command`: add a case
     `"orca" (str "bash " (sq (str (fs/path (:script-dir ctx) "orca-agent-driver.sh"))) " " (sq role) " " (sq (str role-worktree)) " " (sq (:receive-mode row)) " " (sq (str prompt-file)))))`
     — mind the paren balance: the last case value closes its own `str`, the
     `case`, and the outer `(str base ...)` (5 closing parens after
     `(sq (str prompt-file))` when orca is the last case).
   - `check-backend-dependencies!` requires `orca` on PATH (it is, if
     `command -v orca` works).
2. **Register the repo in orca**: `orca repo add --path <project> --json`.
   Get the repo id from `orca repo list --json`.
3. **Export `ORCA_REPO_ID` and `ORCA_MAIN`** before launching the swarm
   (the driver requires them; `ORCA_MAIN` = main worktree path, forward
   slashes). Optional: `SWARMFORGE_ORCA_AGENT` to change the agent CLI.
4. **`swarmforge.conf`**: `window <role> orca <worktree> [task|batch]`.
5. Launch normally (`./swarm` / `swarmforge.bb`). The role window shows the
   driver log + streamed agent output; the agent itself lives in an orca
   terminal (visible in the Orca app).

## Handoff flow (verified)

- Agents push work downstream with `swarm_handoff.sh` (git_handoff) and end
  their final message with `<<<AGENT_DONE>>>` (put that rule in the role
  prompts / local constitution articles).
- The driver detects the marker, then polls the queue with
  `ready_for_next.sh` (task mode) or `ready_for_next_batch.sh` (batch mode).
- On a task it rebuilds the prompt as *role instruction + handoff payload*
  and relaunches the agent in the same terminal. Batch items are directories
  of `.handoff` files (see pitfalls).

## Pitfalls (all hit in production)

- **`path:` selectors do not resolve unregistered worktrees.** orca only
  resolves worktrees it knows (`id:<repoId>::<path>` with forward slashes).
  Role worktrees (`.worktrees/<role>`) are not registered — anchor the
  terminal on the main worktree id and `cd` into the role worktree via the
  startup command (`cd /d "C:\..."`, cmd syntax).
- **orca terminal shells are cmd.exe, not bash.** `$(...)` is not expanded by
  the shell. It works anyway because the default agent (`pi -p`) expands
  `$(cat <file>)` itself — keep using `pi -p "$(cat <abs-path>)"` and do not
  switch to shell-dependent commands.
- **`ready_for_next.sh` prints multi-line output**: `TASK: <path>` followed by
  the whole handoff payload, and `<path>` is Windows-style
  (`C:\...`). Parse the first line only and convert with `cygpath -u`.
  Never pipe through `xargs` (it eats backslashes).
- **Batch mode delivers a directory**, not a file:
  `inbox/in_process/batch_<ts>_<n>/` containing the `.handoff` files. Test
  with `-d`, build the prompt with `cat <dir>/*.handoff`.
- **`$0`-based helper resolution breaks outside the stock launch.** The
  stock launch exports the role script dir on PATH; manual driver restarts
  lose it, and `bash ready_for_next.sh` then resolves `$0` to the cwd. The
  driver calls helpers by absolute path (`$WORKTREE/swarmforge/scripts/...`)
  and exports that dir itself.
- **Driver restarts re-run the role instruction.** Touch
  `.swarmforge/skip-initial` in the role worktree to go straight to queue
  polling. Restart a driver with `tmux send-keys C-c` then the launch command.
- **psmux (native Windows tmux) starts PowerShell by default.** `set-option
  default-shell` and `$SHELL` are ignored; only
  `~/.config/psmux/psmux.conf` with
  `set -g default-shell "C:\\Program Files\\Git\\usr\\bin\\bash.exe"`
  works — and note psmux parses escape sequences, so the backslashes MUST be
  doubled in the config file.
- **Long-lived swarm, short-lived patience.** Give drivers an idle budget that
  covers the whole handoff chain (default now ~3.5 h) or they exit before the
  next handoff lands.
- **Orphaned agent processes.** If a driver dies mid-task, the agent keeps
  running in its orca terminal and the training/agent process may linger —
  check `Get-CimInstance Win32_Process` and kill only your own PIDs.

## Verification

- `orca terminal list --json` shows one `SwarmForge <Role>` terminal per role,
  cwd = the role worktree.
- A handoff draft → `swarm_handoff.sh` → the file appears in the recipient's
  `inbox/new`, the driver logs `new task from queue`, and the agent's final
  message reaches the window.
- Close cleanly: `close-swarm.sh` stops the daemon + tmux sessions; close the
  orca terminals via `orca terminal close --terminal <handle>`.
