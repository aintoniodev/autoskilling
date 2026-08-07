---
name: "synthesis-video-script"
description: "Transform a scientific synthesis into a timed 60–90s video script + visual storyboard using the ABT framework, 3MT arc, Mayer's multimedia principles, and dual-coding strategy. Bridges /scientific-synthesis → /make-product-video."
version: 2
created: "2026-08-07"
updated: "2026-08-07"
---
## When to Use
Use when the user has a completed scientific-synthesis (DEEP or BRIEFING) and wants to turn it into a video-ready script and visual storyboard before producing the actual video. Triggers: "make a video from this synthesis", "turn this into a script", "video script from research", "scientific video script", "research to video", "/synthesis-video-script". Not for raw topic brainstorming (use scientific-synthesis first). Downstream: /make-product-video handles the full production (voice, Remotion, render).

## Procedure
1. Verify the synthesis exists: ask the user for the synthesis file path or check the current session for recent scientific-synthesis output. If no synthesis exists, redirect to /scientific-synthesis first.
2. Extract the four pillars from the synthesis: (a) the organizing question, (b) the top 2–3 themes with their confidence tiers, (c) the primary conflict/contradiction, (d) the conclusion or takeaway.
3. Write the ABT Script (target: ~150 words, ~75 seconds at natural pace): AND — set up the scope and what the synthesis established. BUT — introduce the key contradiction, divergence, or gap the synthesis found. THEREFORE — deliver the reconciled takeaway and implied action. Read it aloud to verify it fits ~75 seconds.
4. Apply Mayer's Coherence Principle: cut every adjective, clause, or technical term that does not directly advance the ABT narrative. If removing a word doesn't change the meaning, remove it. Re-read and re-timer after cuts.
5. Map the script to the 4-stage 3MT arc with timecodes: [00–15s] HOOK & SCOPE (the organizing question + why it matters), [15–45s] SYNTHESIS (the dominant theme and consensus), [45–75s] RESOLUTION (the contradiction, divergence, or nuance), [75–90s] IMPACT (the takeaway or call to action). Adjust word counts per section to fit these windows.
6. Build the Visual Storyboard using dual-coding: for every sentence in the script, assign one explicit visual that mirrors the verbal content simultaneously. Visual types: keyword rótulo, split-path diagram, data chart, icon, color shift, progress bar. No sentence goes without a paired visual. Format as a table: [Time] | [Script line] | [Visual description].
7. Apply Mayer's Signaling Principle: define 2–4 on-screen text headers that mark the arc transitions (e.g., 'The Consensus', 'The Conflict', 'The Takeaway'). These become persistent rótulos in the storyboard.
8. Apply Mayer's Modality Principle: verify that the screen shows visuals/keywords while the voiceover carries the complex content. Flag any script lines where both audio and visual would carry the same long text — move the detail to one channel only.
9. Output the final deliverables: (1) the timed ABT script with timecodes, (2) the visual storyboard table, (3) a production brief for /make-product-video — the brief fixes: tone, forbidden words, accent color (reserve for the BUT/conflict section), energy arc profile, and the storyboard as the 'scene list'.

## Pitfalls
- Don't start without a synthesis — this skill transforms structured research, it doesn't generate it. If the input is a raw topic or a list of URLs, redirect to /scientific-synthesis first.
- Don't write the script by source/author ('Paper A found X, Paper B found Y'). The synthesis already resolved that. Script by theme and narrative tension, same as the synthesis itself.
- Don't exceed 150 words or ~90 seconds. The 3MT arc collapses above this window. If the synthesis is too rich, pick the strongest single thread — this is a hook, not a lecture.
- Don't put paragraph text on screen. The voiceover carries complex content; the screen carries visuals and minimalist keywords. Violating the modality principle halves comprehension.
- Don't skip the storyboard table. Every sentence needs a paired visual before handing off to /make-product-video. An unpaired sentence means the production agent has to guess the visual later — it won't guess well.
- Don't forget confidence tiers in the script. The synthesis graded every claim (C1–C0). Preserve at least the strongest and most conflicted grades verbally — 'Five independent studies confirm...' (C1) vs. 'Industry reports suggest...' (C3).
- Don't assign visuals after writing the script. Dual-coding means they're designed together. If a sentence has no natural visual partner, rewrite the sentence.

## Verification
1. The script is ≤ 150 words and reads aloud in 60–90 seconds.
2. The ABT structure is present: AND (setup), BUT (conflict), THEREFORE (resolution).
3. The 4-stage arc timecodes are assigned: Hook [0–15s], Synthesis [15–45s], Resolution [45–75s], Impact [75–90s].
4. Every script sentence has a paired visual in the storyboard table (dual-coding check).
5. No on-screen text duplicates long voiceover content (modality principle check).
6. At least one confidence tier from the synthesis is preserved in the spoken script.
7. The storyboard includes 2–4 signaling headers for arc transitions.
8. Production brief for /make-product-video is present (tone, forbidden words, accent color, energy arc, storyboard as scene list).