---
name: genetic-programming-pipelines
description: >-
  Genetic programming (GP) / programación genética applied to neural-network
  and deep-learning pipelines: evolutionary search in program space (code,
  trees, configs, architectures, augmentations, prompts, agents) and
  fitness/evaluation design for GP loops. Covers search-space framing (what
  evolves vs what gradients handle), fitness ladders with rank-inversion
  validation, LLM-driven genetic operators with deterministic gates, champion
  selection, diversity pressure, objective audits, lineage logging. Activates
  ONLY when the topic is genetic programming — ES: 'programación genética',
  EN: 'genetic programming'/'GP' — NOT for generic autoresearch, HPO, or NAS
  without a genetic-programming framing.
license: MIT
metadata:
  author: otero
  version: "1.0.0"
  evidence-base: scientific-synthesis-2026-08-09
  evidence-path: references/evidence.md
---

# Genetic Programming for DL Pipelines

Design, run, and audit genetic-programming (GP) / evolutionary autonomous experiment loops that optimize neural network and deep learning pipelines. This skill operationalizes the evidence-grounded consensus from a 41-source scientific synthesis (2026-08-09): evolution for structural/discrete decisions, gradients for weights, LLMs as variation operators, automated evaluation as fitness — with evaluation fidelity as the binding constraint.

## When to Use

Se activa **solo** cuando el tema es programación genética (ES: *programación genética* / EN: *genetic programming*, *GP*) aplicada a pipelines ML/DL:

- Evolución de programas/código/árboles que representan componentes de pipeline (arquitecturas, aumentaciones, features, configs, prompts, agentes).
- GP-NAS o síntesis de pipelines en espacio de programas (program-space search, no GA sobre hiperparámetros).
- Program search evolutivo en loops autónomos (estilo FunSearch: código como genoma, LLM como operador).
- Auditoría del fitness/evaluación de un loop GP.

NO se activa para:

- Autoresearch o experiment loops genéricos sin framing de programación genética.
- Tuning de hiperparámetros con GA/ES/Bayesiano, ni NAS sin evolución de programas.
- Experimentos de un solo run.

**Antes de empezar, pregunta qué modelo/provider LLM implementará los operadores evolutivos.**

## Procedure

### 1. Frame the search space

Decide **what evolves** and **what stays gradient-trained**:

- Evolve: pipeline structure, architecture graphs, augmentation policies, feature construction, loss/reward functions, hyperparameter schedules, prompts, agent programs.
- Gradients: weights inside a fixed candidate structure.

GP/evolution is for discrete, structural, multi-objective, or non-differentiable layers of the problem. If the space is low-dimensional and continuous, stop and recommend Bayesian optimization instead.

### 2. Design the fitness ladder

Define:

- **High-fidelity metric** — used only for champions and final verification (full training, held-out evaluation).
- **Cheap surrogates** — reduced epochs, cached features, weight sharing, zero-cost proxies.

**Before trusting selection**, validate on a held-out subset that cheap-fidelity rankings reproduce full-fidelity top-k. Rank inversion is the #1 silent failure mode: cheap evaluation reorders candidates differently than full training.

### 3. Seed the population with diversity

Mix LLM-prior proposals (FunSearch/EvoPrompt style) with random or structured baselines. Mono-culture initialization collapses the search. A diverse archive is cheap insurance.

### 4. Implement variation operators

- Use the LLM as mutation/crossover over human-meaningful representations (code, configs, prompts).
- Sampling temperature is the exploration/exploitation dial: higher = more exploration.
- **Gate every candidate with deterministic validators** (correctness, syntax, resource bounds) before evaluation. LLM output must never reach the fitness function ungated — the evaluator is what guards against hallucination.
- Fall back to classical operators where the LLM adds cost without benefit.

### 5. Selection and diversity

- Elitism with **explicit champion tracking** (champion separate from the population).
- Maintain archives/islands or quality-diversity pressure (MAP-Elites style) to prevent mode collapse.
- Track lineage for every candidate (parents, operator, fitness).

### 6. Run the evaluation loop in parallel

- Size the population by **GPU wall-clock budget**, not by function-evaluation count alone.
- Evaluate cheap candidates at low fidelity tiers; escalate only promising lineages to higher tiers.
- Never let a cheap evaluation crown a final champion.

### 7. Audit the objective every N generations

- Re-measure proxy-to-true-objective correlation.
- Check for fitness hacking.
- Require **bootstrap/permutation significance** on any claimed champion improvement over the previous champion before accepting it. When the harness logs only final metrics (no per-epoch curves), use a **multi-seed paired permutation**: run champion vs previous champion at n seeds and permute the paired deltas. n=5 gives a minimum achievable P of 1/33 ≈ 0.031 — enough to reject chance for large deltas, and honestly reported as a floor.
- Watch for **sibling degeneracy**: two genomes with identical fitness across all seeds mean a mutation dimension is inert at the current tier — audit tier coverage before spending more evaluations on that dimension.

### 8. Log everything

Population, fitness per fidelity tier, parents, operator used, timestamps, rejected hypotheses. A complete lineage log is what makes the loop reproducible and the results trustworthy.

## Pitfalls

- **Rank inversion**: weight sharing, reduced epochs, and surrogates reorder candidates differently than full training — validate cheap vs full rankings on a held-out subset. **Top-1 flips even when top-k overlap passes**: observed 2026-08-10 (MNIST CNN, cheap=3ep/8k, full=12ep/60k) — cheap multi-seed crowned `g2_llm_002` (0.9799 mean), full crowned `cand_004` (0.9948), with top-3 overlap 3/3. Consequence: cheap fidelity **prunes**, full fidelity **selects the champion** — never accept a cheap-crowned champion, even with rank-inversion validation green.
- **Fidelity-tier blind spots**: mechanisms that never fire at the cheap tier are invisible to selection, so mutations on them are neutral drift. Observed: a step scheduler (`step_size=3`) never fired in 3-epoch runs, producing byte-identical fitness across 5 seeds for two different genomes (`g1_llm_001` ≡ `g2_llm_002`). Detect via sibling degeneracy (identical fitness across seeds) and either lengthen the tier or drop the dimension from the search space at that tier.
- **Val-selected ≠ test-selected**: selectors tuned on reduced-epoch or validation runs frequently fail to transfer to full training — never accept a champion without a full-fidelity confirmation run.
- **Mode collapse**: without diversity pressure (archives, islands, QD), the population converges to one lineage and exploration stops.
- **Ungated LLM candidates**: hallucinated or subtly incorrect code/configs evaluated as if valid — deterministic validation gates are mandatory.
- **Untuned EA hyperparameters**: population size, mutation rate, temperature are often left at defaults; most published EA gaps are configuration gaps, not method gaps.
- **Evaluation circularity**: if the same model family that generates research also reviews it, external ground-truth anchors are required to avoid self-referential loops.
- **Fitness hacking**: proxies get gamed — audit the objective, not just the score.
- **Context limits**: LLM operators degrade on high-dimensional/constrained spaces that exceed context — split the space or fall back to classical operators.
- **BO-vs-EA confusion**: Bayesian optimization wins on low-dim continuous spaces with cheap evaluations; evolution wins on discrete/structural/multi-objective spaces.

## Verification

1. Cheap-fidelity selection reproduces full-fidelity top-k on a held-out sample (e.g., top-3 overlap ≥ 2/3) before the loop is trusted.
2. Every accepted champion improvement is significant under bootstrap/permutation against the previous champion (e.g., P < 0.05 on a shuffle test); with multi-seed paired permutation, report the seed count and the achievable P floor.
3. **The final champion is the best candidate under full fidelity**, not the cheap-fidelity leader — rank-inversion green (top-3 overlap) does not protect the top-1 position.
4. No sibling degeneracy: two genomes with different mutation targets must not produce identical fitness across all seeds — if they do, a mutation dimension is inert at the selected tier.
3. Population diversity metrics (archive occupancy, genotypic distance, lineage share) stay healthy — no single lineage exceeds a pre-set share of the population.
4. Lineage log is complete: every candidate has parents, operator, fitness per tier, and timestamp; a reproduction run matches the logged champion.
5. Objective audit passes: proxy-to-true correlation above threshold and drift alarms fired correctly when the proxy degraded.
6. Final champion confirmed with a full-fidelity run and, where applicable, an external ground-truth check (held-out set, independent evaluator).

## Evidence Base

See `references/evidence.md` for the claim-to-source mapping with confidence tiers (C1–C3). Full synthesis: "Genetic Programming para AI Agents y Autoresearch - Sintesis Cientifica.md" (2026-08-09).
