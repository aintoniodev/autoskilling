---
name: "md-to-x-thread"
description: "Rewrite any markdown document as an X/Twitter thread — hook, dead ends, concrete specifics, no clinical language, no agent plumbing. Then ask where to save it."
version: 1
created: "2026-08-06"
updated: "2026-08-06"
---
## When to Use
Use when the user wants to turn a markdown note, session write-up, blog post, or any long-form text into an X/Twitter thread. Triggers: "make it X oriented", "format for X", "turn into a thread", "tweet thread", "parse text for X", "md to X".

## Procedure
1. Read the source markdown. If the user pasted it inline, use it directly.
2. Identify the core insight — the one thing the reader will remember. This becomes the hook.
3. Strip everything that reads like agent plumbing, changelogs, or setup instructions. Keep process, challenges, dead ends, failures, corrections, and the insight.
4. Rewrite in first person, direct, no clinical language. No 'the user', no third person. Voice-first.
5. Structure as a thread: hook first (with 🧵), then the journey, dead ends, lessons, closer. Each post should stand alone as a tweet — specific, concrete, punchy.
6. Principles: hook with the insight not the activity, concrete over abstract, show the detours, specific takeaways not fortune cookies, filter noise, match intensity to substance, no clinical language.
7. Drop all markdown formatting (headers, callouts, blockquotes). Plain text only. Keep bullet lists if they scan well as a tweet.
8. Present the result to the user as plain text, no labels (no 'Tweet 1', 'Tweet 2').
9. Ask the user where to save it. Write it to the path they provide.

## Pitfalls
- Do NOT number tweets or label them — just the text, separated by blank lines.
- Do NOT include markdown formatting in the output — no headers, no bold, no blockquotes, no callouts. Plain text only.
- Do NOT keep the original markdown structure — restructure for X, not for readability.
- Do NOT include agent-internal details unless they're part of the story (e.g., 'six corrections forced a rewrite' is a story; 'PowerShell ate the && chain' is plumbing).
- Do NOT save anywhere without asking — always ask where to save first.

## Verification
1. No markdown formatting in the output (no #, no >, no **, no callout syntax).
2. No tweet labels or numbers.
3. First line hooks with the insight, ends with 🧵.
4. Last line lands on the sharpest takeaway.
5. User chose where to save and the file exists at that path.
