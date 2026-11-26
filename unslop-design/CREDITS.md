# Credits

`unslop-design` merges and empirically refines two upstream UI skills:

- **`unslop-ui` (`v1.0.2`, MIT)**: Surgical UI copy, chart, micro-chrome, layout, alignment, real-state, and guardrail checks (`U1`–`U25`) plus taste-memory integration (`references/taste.md`), authored by [Felipe Basurto](https://github.com/felipebasurto/unslop-ui), drawing from Lauren Tan's [`unslop`](https://github.com/elle/unslop) and [Unslop.it](https://unslop.it).
- **`gemini-frontend-design` (`v1.0.0`, Apache-2.0)**: Composition-first web build principles, palette tokens, typographic hierarchy, restraint, and self-critique workflow from [Google Gemini DemoLab](https://github.com/google-gemini/demolab/blob/main/skills/gemini-frontend-design/SKILL.md).

## What the `$deepify` synthesis added

Validated across 53 clean-room evaluations against a frozen 100-point rubric covering Build/Redesign, Surgical Audit, Trust Boundaries/Prompt-Injection Guardrails, Bilingual Locale Fidelity, and Headless Chromium Rendering:

1. **Edit Authority & Mode Permissions Matrix** in `SKILL.md`: cleanly separates Build/Redesign, Audit, and read-only `--plan` scope so clean siblings and domain content are never overwritten on an audit request.
2. **Active Trust Boundary & Pre-Write Per-Target Gate**: enforces `No-op` / `Edit` / `Report-only` per target and actively strips leaked AI-directed prompt-injection comments without inventing unverified claims or deleting functional state controls.
3. **Zero-Bloat One-Level Progressive Disclosure**: keeps `SKILL.md` focused (655 words) while routing mode-specific workflows into `references/build.md` (including Bounded Rendered Verification) and `references/audit.md` (including Boundary Pairs & Locale Fidelity).

| Skill / Stage | Total (`0–100`) | Replicates | Bilingual (`0–5`) |
|---|---|---|---|
| `unslop-ui` v1.0.2 | `63.67 ± 2.08` | `[62, 66, 63]` | — |
| `gemini-frontend-design` v1.0.0 | `81.33 ± 1.53` | `[81, 80, 83]` | — |
| Stage 0 naive merge | `94.67 ± 6.81` | `[87, 97, 100]` | — |
| `unslop-design` Iter 4 (winner) | **`99.33 ± 0.58`** | `[99, 100, 99]` | **`5.00 ± 0.00`** |
| Cross-model check (`claude-opus-5-5`) | `92` | `[92]` | `5` |
