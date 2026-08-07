---
name: "scientific-synthesis"
description: "Produce a rigorous multi-source synthesis with confidence grading, thematic integration, and conflict reconciliation. Use when the user wants to deeply summarize/analyze multiple sources, research a topic across web and academic literature, or produce a structured briefing from diverse materials."
version: 1
created: "2026-08-07"
updated: "2026-08-07"
---
## When to Use

Use when the user wants to synthesize multiple sources into a coherent, scientifically structured summary. Triggers: "summarize these sources", "synthesize this research", "what does the literature say about X", "deep summary", "research synthesis", "briefing on X", "literature review", "what's the consensus on X". Not for single-document summaries or simple Q&amp;A.

## Procedure

1. Determine output mode: DEEP (full 6-section structure) or BRIEFING (abstract + themes + gaps). Ask the user unless the context makes it obvious.
2. Gather sources using available tools (web_search with 2-4 varied queries, fetch_content for specific URLs, ctx_execute_file for local files). Record: exact queries used, number and type of sources found, date ranges covered.
3. Build the Synthesis Matrix: for each source, extract Core Argument, Methodology/Type, Key Findings, Limitations, and Theme Mapping. Include a Confidence Tier column (see Confidence Grading).
4. Write the Structured Abstract (150-250 words): Background/Objective, Methods (source counts and types), Results (primary synthesized themes), Conclusions (core takeaway).
5. Write Introduction: context, the single organizing question, and boundary conditions (inclusion/exclusion criteria, date range, source types).
6. Write Methodology: search strings used, tools queried, source counts by type, and quality/bias assessment criteria. Be reproducible.
7. Write Thematic Results organized by theme (never by author). For each theme: (a) state the synthesized consensus, (b) use integrative verbs (corroborates, contrasts with, extends, diverges from, validates), (c) inline confidence tier per claim, (d) flag single-source claims explicitly.
8. Write Conflicts, Gaps &amp; Limitations: reconcile contradictions (why sources disagree), identify knowledge gaps across all sources, and acknowledge source material constraints.
9. Write Conclusion: answer the organizing question, highlight temporal evolution if relevant, state practical implications or next steps.
10. Self-check against Core Rules (see Pitfalls) before delivering.

## Pitfalls

- Never write author-centric paragraphs (Source A says X. Source B says Y.). Always synthesize by theme.
- Never present single-source claims without flagging them as such. Mark uncorroborated findings clearly.
- Never skip the Synthesis Matrix — it is the engine. Drafting without it produces serial summaries, not synthesis.
- Never conflate gray literature with peer-reviewed sources. Weight blog posts, whitepapers, and trade press explicitly in the methodology.
- Never omit the conflict section even when sources largely agree — noting the absence of contradiction is itself a finding.
- Avoid hedge stacking: 'may possibly suggest' is noise. Pick one hedge level per claim.
- Don't invent findings. If the sources are thin on a theme, say so — gap &gt; fabrication.

## Output Structure

### DEEP Mode (full 6 sections)

```
# [Title]

## 1. Structured Abstract (150–250 words)
- **Background/Objective**: What question do these sources answer?
- **Methods**: How many sources evaluated, how selected, what types.
- **Results**: Primary synthesized themes and findings.
- **Conclusions**: Overall consensus or core takeaway.

## 2. Introduction
- Context & justification for this synthesis.
- Single organizing question (e.g., "What is the consensus on X across current literature?").
- Boundary conditions: inclusion/exclusion criteria, date range, source types, geographical/language scope.

## 3. Methodology
- Search strategy: exact queries used, tools/providers queried.
- Source counts by type (peer-reviewed, whitepapers, blogs, etc.).
- Quality/bias assessment criteria applied.
- Reproducibility: enough detail that someone could replicate the search.

## 4. Thematic Results
- Organized by theme, never by author or URL.
- Each theme subsection includes:
  - Synthesized consensus statement with inline confidence tier.
  - Integrative verbs showing source relationships.
  - Explicit flag on any single-source claims.

## 5. Conflicts, Gaps & Limitations
- Contradictions between sources and why they may disagree.
- Knowledge gaps: what remains unaddressed across all sources.
- Source material constraints (e.g., lack of peer-reviewed data on a subtopic).

## 6. Conclusion
- Direct answer to the organizing question.
- Temporal evolution: how understanding has shifted (if applicable).
- Practical implications or recommended next steps.
```

### BRIEFING Mode (compressed)

```
# [Title]

## Abstract (100–150 words)
## Key Themes (2–4 themes, each 3–5 sentences with confidence tags)
## Gaps & Open Questions (bullet list)
## One-Line Takeaway
```

## Confidence Grading

Tag every substantive claim with a confidence tier:


| Tier   | Label                          | Criteria                                                                                            | Inline format |
| ------ | ------------------------------ | --------------------------------------------------------------------------------------------------- | ------------- |
| **C1** | Strong consensus               | Corroborated by 3+ independent sources, including at least one peer-reviewed or high-quality source | `[C1]`        |
| **C2** | Moderate support               | Corroborated by 2+ sources or 1 high-quality source with indirect support from others               | `[C2]`        |
| **C3** | Single-source / uncorroborated | Comes from only one source or from low-quality/gray literature with no cross-check                  | `[C3]`        |
| **C0** | Conflict / unresolved          | Sources contradict each other with no clear reconciling factor                                      | `[C0]`        |


Example: "Regular resistance training improves insulin sensitivity [C1], though optimal frequency remains debated [C0]."

## Synthesis Matrix Template

Build this BEFORE drafting. One row per source.

```
| Source | Type | Date | Core Argument | Key Findings | Limitations | Themes | Confidence |
|--------|------|------|--------------|--------------|-------------|--------|------------|
| Source 1 | Peer-reviewed paper | 2024 | ... | ... | ... | A, C | C1 |
| Source 2 | Industry whitepaper | 2024 | ... | ... | ... | A, B | C2 |
| Source 3 | Blog / trade press | 2023 | ... | ... | ... | B | C3 |
```

The matrix is NOT included in the final output — it is a working tool. Themes are mapped here so drafting flows by theme.

## Core Writing Rules

1. **Theme-based, never author-based**: Organize by what was found, not who said it.
  - BAD: "Smith (2023) says X. TechCrunch (2024) says Y. Jones (2022) says Z."
  - GOOD: "While initial industry reports emphasize X, empirical studies demonstrate Y under controlled conditions, though historical reviews urge caution regarding Z."
2. **Integrative verbs**: Use analytical verbs to show inter-source relationships — corroborates, contrasts with, extends, diverges from, validates, qualifies, complicates, reframes.
3. **Single-source flagging**: Every claim backed by only one source gets `[C3]`. This does not invalidate it — it signals the reader to weight it accordingly.
4. **Gray literature transparency**: When citing non-peer-reviewed sources (blogs, whitepapers, trade press), note the source type inline. Example: "According to an industry whitepaper [C3]..."
5. **Temporal awareness**: When sources span multiple years, note how understanding has evolved: "Earlier studies emphasized X (2019–2021), but more recent work has shifted toward Y (2023–2024)."
6. **No hedge stacking**: One hedge per claim. "May" or "suggests" — not "may possibly suggest."
7. **Gap &gt; fabrication**: If sources are thin on a theme, declare the gap. Never extrapolate beyond what the sources support.

## Verification

1. Every thematic claim cites multiple sources or is explicitly flagged as single-source.
2. No paragraph is organized around a single author/source — all are theme-based.
3. Integrative verbs are used to show inter-source relationships (not just 'X says... Y says...').
4. Confidence tiers are assigned to every substantive claim.
5. Conflicts and gaps section exists even when consensus is strong.
6. Methodology section is reproducible (exact queries, source counts, inclusion criteria).
7. The organizing question from the introduction is directly answered in the conclusion.

