---
name: "md-to-x-thread"
description: >-
  Convert any markdown document to plain text formatted for X/Twitter — strip formatting only,
  change zero words. Then ask where to save it.
version: 3
created: "2026-08-06"
updated: "2026-08-06"
---
## When to Use
Use when the user wants to turn a markdown note, session write-up, blog post, or any long-form text into X/Twitter-ready plain text. Triggers: "make it X oriented", "format for X", "turn into a thread", "tweet thread", "parse text for X", "md to X".

## Procedure
1. Read the source markdown. If the user pasted it inline, use it directly.
2. Strip ALL markdown formatting: headers (#), bold (**), italic (*), blockquotes (>), callouts (> [!...]), inline code (`), code blocks (```), horizontal rules (---), frontmatter (---), links ([text](url) → text).
3. Do NOT change, add, remove, or rephrase a single word of the original content. The output must contain the exact same words as the input, only without formatting markers.
4. Preserve the original structure and order. Keep paragraphs where they are. Keep bullet points as plain bullets (• or -). Do not reorder, merge, split, or restructure sections.
5. If the original has a 🧵 emoji, keep it. If it doesn't, don't add one.
6. Present the result to the user as plain text, no labels (no 'Tweet 1', 'Tweet 2').
7. Ask the user where to save it. Always save as `.md` — the content inside is plain text (no markdown syntax), but the file extension is .md.
8. Write it to the path they provide.

## Pitfalls
- Do NOT number tweets or label them — just the text, separated by blank lines.
- Do NOT include markdown formatting in the output — no headers, no bold, no blockquotes, no callouts, no inline code, no code blocks, no frontmatter, no link syntax. Plain text only.
- Do NOT change a single word. Not grammar, not voice, not structure. The content is sacred — only the formatting is stripped.
- Do NOT add, remove, or merge paragraphs. Keep the exact same paragraph breaks as the original.
- Do NOT add emojis that weren't in the original. Do not remove emojis that were.
- Always save as .md (plain text content, .md extension) — never .txt.
- Do NOT save anywhere without asking — always ask where to save first.

## Verification
1. No markdown formatting in the output (no #, no >, no **, no callout syntax, no `, no ```, no ---, no frontmatter, no [text](url)).
2. No tweet labels or numbers.
3. Every word in the output exists in the input. Zero words added, removed, or changed.
4. Paragraph order and count matches the original (modulo frontmatter removal).
5. File saved as .md, not .txt.
6. User chose where to save and the file exists at that path.
