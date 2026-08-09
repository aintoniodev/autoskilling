# SwarmForge Agent Plugin

**SwarmForge** — Uncle Bob's tmux-based multi-agent orchestration for git worktrees —
packaged as an **Agent Plugin 1.0.0** (see <https://agent-plugins.org>).

With this plugin, an agent knows how to bootstrap and operate a SwarmForge swarm
directly from a conversation: choose a workflow branch (two-pack / four-pack / six-pack),
install it in a project, configure `swarmforge.conf`, roles and the layered constitution,
launch with `./swarm`, and drive the swarm with the handoff helpers
(`swarm_handoff.sh`, `ready_for_next.sh`, `done_with_current.sh`).

## What Is Inside

```
swarmforge/
├── plugin.json                      # Agent Plugin 1.0.0 manifest
├── README.md                        # this file
└── skills/
    └── swarmforge/                  # the skill (Agent Skills, agentskills.io)
        ├── SKILL.md                 # operating manual (When to Use, Quick Start, ...)
        ├── scripts/                 # operational scripts (swarm, handoff helpers,
        │                            # daemon, watchdog, cleanup, bootstrap, adapters)
        ├── references/              # BRANCHES.md, REFERENCE.md (protocol details)
        └── assets/                  # templates: constitution/, roles/<branch>/, examples/
```

## Installation

### With an Agent Plugins compatible client

Install the plugin from this repository (or a local checkout of `plugin.json`) following
your client's Agent Plugins installation flow. The client resolves the `skills/`
directory and makes the `swarmforge` skill available to the agent.

### Manual / skill-only install

The plugin is self-contained in the skill directory — copy `skills/swarmforge/` into
your agent's skills folder and the `swarmforge` skill becomes available:

```sh
cp -r skills/swarmforge /path/to/your/skills/swarmforge
```

No runtime dependencies are installed by the plugin itself; the swarm still requires
zsh, git, tmux, Babashka and an agent backend (codex, claude, copilot or grok) on the
target machine — see the skill's Prerequisites section.

### Native Windows (no WSL)

The bundled scripts are bash-compatible and ship a Windows-native alternative stack:
**bash (Git Bash) + psmux (native Windows tmux) + bb.exe (native babashka)**.
`scripts/setup-windows.sh` installs everything; `SWARMFORGE_TERMINAL=windows-native`
opens Windows Terminal windows against the psmux sessions. Verified end-to-end on
Windows 11 (see the skill's "Native Windows" section).

## Usage

1. Ask your agent to use the `swarmforge` skill.
2. Point it at a project and pick a workflow branch (two-pack / four-pack / six-pack).
3. Follow the skill's Quick Start: install, configure `swarmforge.conf`, `./swarm`,
   hand off work, stop cleanly.

## Credits and Attribution

SwarmForge is the work of **Robert C. Martin (Uncle Bob)** — upstream repository:
<https://github.com/unclebob/swarm-forge>.

This plugin bundles the operational scripts, workflow branches and prompt templates from
that repository, and adds the skill layer, references and packaging. Note: the upstream
project does **not** declare a license; this plugin is distributed under the **MIT
License** and makes no claim over upstream code's status.

## Links

- Agent Plugins specification: <https://agent-plugins.org>
- Agent Skills specification: <https://agentskills.io/specification>
- Upstream SwarmForge: <https://github.com/unclebob/swarm-forge>
