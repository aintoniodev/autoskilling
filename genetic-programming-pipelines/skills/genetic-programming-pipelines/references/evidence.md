# Evidence Base — Evolutionary Autoresearch for DL Pipelines

Claim-to-source mapping for the `genetic-programming-pipelines` skill. Confidence tiers: C1 = 3+ independent sources incl. high-quality; C2 = 2+ sources or 1 high-quality; C3 = single source / uncorroborated; C0 = conflict unresolved. Full synthesis: "Genetic Programming para AI Agents y Autoresearch - Sintesis Cientifica.md" (PKM vault, 2026-08-09).

## 1. Evolution is a mainstream paradigm for DL pipeline optimization [C1]

- ACM Computing Surveys, *Survey on Evolutionary Deep Learning* (2023).
- *National Science Review*, Advances in neural architecture search (2024).
- *Artificial Intelligence Review*, AutoML: past, present and future (2024).
- Springer, *Evolutionary Deep Neural Architecture Search* (book, 2023).
- TPOT (PMLR 2016) + JAIR AutoML benchmark (2022) + KAIS *Eight years of AutoML* (2023) → GP pipelines competitive for classical ML [C2].

## 2. GP holds the program-structured niches [C2/C3]

- GP for CNN design end-to-end — *Genetic Programming and Evolvable Machines* (2024) [C2]; same paper notes GP under-researched vs GAs for NAS.
- GP feature construction for DNNs — Heaton dissertation (NSU) [C3].
- GeneticAugment, sim-to-real augmentation policy search (arXiv 2403.06786) [C3].
- EZNAS, evolved zero-cost proxies (NeurIPS 2022) [C2].
- AutoML-Zero, full algorithms from scratch (ICML 2020) [C2].

## 3. Neuroevolution ≈ gradient estimation — reconciled division of labor [C1/C2]

- ES analytically equivalent to gradient estimation on smoothed objective — *Nature Communications* (2021) [C1].
- Simple evolutionary optimization rivals SGD (GECCO 2016); OpenAI ES rivals policy-gradient RL (2017) [C2].
- PBT: evolve hyperparameters while SGD trains weights (DeepMind 2017) [C2].
- PGA-MAP-Elites / descriptor-conditioned RL beat pure PPO and pure MAP-Elites (GECCO 2021, arXiv 2401.08632) [C2].
- PES / ES-Single for unrolled computation graphs (ICML 2021/2023) [C2].

## 4. LLM-as-operator ("LLM-GP") [C1/C2]

- FunSearch: first new results on open math problems from LLM-based system; evaluator gates hallucinations (Nature 2023) [C1].
- EvoPrompt: up to ~25% over human prompts on BIG-Bench Hard, 31 datasets (ICLR 2024) [C1].
- Survey consensus (arXiv 2401.10034; arXiv 2505.15741): LLM operators ≈ hand-designed operators in efficiency; scale with model quality; temperature = exploration dial; context limits + narrow benchmarks remain barriers [C2].

## 5. HPO method selection [C1/C3]

- Bayesian optimization reliably beats random search for ML hyperparameter tuning (NeurIPS 2020 BBO challenge, PMLR 133) [C1].
- GAs competitive on some DL tuning tasks (CEC 2021) [C3].
- Reconciliation: BO for low-dim continuous; evolution for discrete/structural/multi-objective/non-stationary.

## 6. Fitness bottleneck & cost engineering [C1/C0]

- LargeEvo ~3,150 GPU-days per search (cited in surrogate-assisted NAS literature) [C3].
- Weight sharing cuts cost orders of magnitude (ENAS, ICML 2018) [C1] but ranking validity contested: TuNAS (CVPR 2020) vs NAS-Bench-101 appraisal (Neurocomputing 2022) [C0].
- NeuroEvoBench (NeurIPS 2023): most published EA results use poorly-tuned EA hyperparameters [C1].
- GPU-aware evaluation changes population/wall-clock calculus (arXiv 2601.18446) [C3].

## 7. Autoresearch systems are genetic loops [C2/C3]

- The AI Scientist (Nature 2026): automated reviewer on par with humans; one paper passed average human workshop acceptance threshold; quality scales with compute + base model [C1-as-reported/C2].
- Robin, multi-agent automated biology research (Nature 2026) [C2].
- Agentic evolutionary frameworks (arXiv 2025-2026, each C3): CliffSearch, OR-Agent, ResearchEVO, CORAL, SAGA (objective evolution as unmet requirement).
- EvoAgent (NAACL 2025), ADAS (ICLR 2025), Eureka (ICLR 2024), Darwin Gödel Machine (ICLR 2026) [C2 theme / C3 per system].

## 8. Evaluation circularity & objective drift [C0]

- Self-referential loops (AI generates → AI reviews) unresolved; AI Scientist validates reviewer against human ground truth, circularity critique remains open [C0].
- SAGA: automating objective-function design is the unmet requirement [C3].

## 9. Field validation — live GP benchmark (2026-08-10) [C1-empirical]

Full run on native Windows: 3 generations, 18 CNN-MNIST candidates trained on an RTX 2060 (cheap tier 3ep/8k ≈ 20-90 s/candidate; full tier 12ep/60k ≈ 5-11 min). Claims from the skill reproduced in production:

- **Rank inversion real**: cheap multi-seed crowned `g2_llm_002` (0.9799 mean, 5 seeds), full fidelity crowned `cand_004` (0.9948) — top-3 overlap 3/3 yet the top-1 flipped; champion selection must use full fidelity.
- **Fidelity-tier blind spot**: a step scheduler (`step_size=3`) never fired in 3-epoch cheap runs → two genomes with different schedulers produced byte-identical fitness across 5 seeds (degeneracy signal).
- **Gate mandatory**: a 6.5 M-param candidate was rejected by the deterministic budget gate before evaluation.
- **Significance floor**: champion vs MLP baseline Δ=+3.7 pp cheap, P=0.0316 (multi-seed paired permutation, n=5 — the achievable floor); GP-vs-GP deltas not significant (P=0.12).
- **LLM operators effective**: 6/6 LLM proposals gated clean; best offspring `g2_llm_002` reached 0.9944 full vs champion 0.9948 — converged plateau, honest non-claim.
