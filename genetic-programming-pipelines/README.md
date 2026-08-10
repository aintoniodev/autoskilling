# genetic-programming-pipelines

![social preview](assets/social-preview.png)

Genetic programming (GP) applied to neural-network and deep-learning pipelines:
evolutionary search in program space (architectures, augmentations, configs,
prompts, agents) with LLM variation operators, fitness ladders, deterministic
gates, champion selection, diversity pressure and objective audits.

- **Activates only on genetic-programming topics** (ES: *programación genética*),
  not generic autoresearch, HPO or NAS without a GP framing.
- **Evidence base:** 41-source scientific synthesis (2026-08-09) + field
  validation on a live benchmark (2026-08-10: 18 CNN-MNIST candidates, 3
  generations, RTX 2060, rank-inversion and tier-blind-spot findings logged in
  `skills/genetic-programming-pipelines/references/evidence.md`).
- **Plugin format:** Agent Plugin 1.0.0 (agent-plugins.org) — `plugin.json` +
  `skills/` directory.

## Install

Point your agent at `plugin.json` (Agent Plugins compatible client), or copy
`skills/genetic-programming-pipelines/` into your agent's skills folder
(e.g. `~/.pi/agent/skills/` for pi, `~/.agents/skills/` for Claude Code).

## Use

Ask your agent for genetic-programming-based optimization of a DL/ML pipeline.
The skill guides the loop: search-space framing → fitness ladder (cheap
surrogates + full fidelity) → diverse seeding → LLM operators with
deterministic gates → champion selection → objective audit → lineage logging.
