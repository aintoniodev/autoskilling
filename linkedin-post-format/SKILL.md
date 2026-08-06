---
name: linkedin-post-format
description: >-
  Convert a value-capture note (or any session note) into a LinkedIn-optimized
  text post. Restructures into Hook → Story → Proof → CTA, strips all
  markdown/Obsidian syntax, optimizes for mobile-first readability and
  engagement. Triggers: "format for LinkedIn", "linkedin post", "turn into
  a LinkedIn post", "linkedin-ify", "make it LinkedIn ready", "/linkedin-post-format".
version: 2
created: "2026-08-06"
updated: "2026-08-06"
---
## When to Use

Use when the user wants to turn a value-capture note, session write-up, or
any markdown document into a LinkedIn-ready text post. Also use when the user
wants to LinkedIn-optimize something they've already written.

This skill is the LinkedIn counterpart to `md-to-x-thread`. That skill strips
formatting and preserves every word for X. This one *restructures* for LinkedIn's
specific format — different platform, different shape, different rules.

## Procedure

### 1. Read the source

Read the source markdown. If the user pasted it inline, use it directly.

### 2. Caption or standalone?

Before structuring, decide what the post *accompanies* — this overrides the
length model and the structure:

- **Standalone text post:** the text IS the post. Use the full Hook → Story →
  Proof → CTA structure and the 1,300–2,500 character target (step 5).
- **Caption for media (video / image / carousel):** the media carries the
  story; the caption only makes someone watch and comment. Keep it to 1–4 short
  lines. Do NOT retell the story in text — you'll compete with the media and
  bury the asset. Lead with the one-line outcome, defer to the media ("this
  happened"), end with the CTA. The verbatim prompt or the literal input is
  often the whole caption's proof.

When in doubt, ask the user which it is. Don't guess and produce 1,800
characters of caption for a video — the character target only applies to
standalone text.

### 3. Identify the core arc

Scan the note and identify the single strongest arc — not everything in the
note belongs in one LinkedIn post. The arc is usually one of:

- **Failure → Insight**: What went wrong, what you learned
- **Process → Outcome**: How you did something and the specific result
- **Confession → Lesson**: What you got wrong, the real takeaway
- **Discovery → Implication**: What you found, why it matters to others

If the note has multiple strong arcs, pick the one most likely to make someone
stop scrolling. When in doubt, **the failure or confession is almost always the
stronger hook** — not the success.

### 4. Restructure into Hook → Story → Proof → CTA

Map the note sections to the LinkedIn structure:

| Note Section | LinkedIn Part | Strategy |
|---|---|---|
| Key Insight | **Hook** | Lead with the insight or failure, not the activity |
| Challenges + What Didn't Work | **Story** | The detour IS the content. Specific failures beat generic advice |
| What I Did + The Process | **Proof** | Concrete numbers, commands, decisions build credibility |
| TL;DR | **CTA / Closer** | Ask a specific question that connects to the reader's experience |

**Hook (1–3 short lines):**
- Open with the outcome, not the activity: "The build went from 14s to 2s"
  beats "I worked on build optimization"
- Lead with what came out — not why you decided to do it. "I built a video in
  90 minutes" lands; "I wanted to give a tool credit" is your motivation and
  belongs in line two, not line one
- Name a specific situation the reader recognises, or a number/result
- The hook must work in ~140 characters — that's all mobile shows before "see more"
- One short sentence per line (5–12 words). No commas in line 1 if possible.
- Create tension: a gap between what they know and what they're about to learn

**Story (3–6 short paragraphs):**
- Walk through what actually happened — the real sequence with real detours
- Include the specific error, command, decision, or moment
- One idea per paragraph, one paragraph per idea
- Keep paragraphs to 1–3 sentences
- The challenges and failures are the most valuable part — lead with them

**Proof (1–2 paragraphs):**
- Concrete numbers: "8 weeks", "12 accounts", "3x improvement"
- Named constraints: "this works when X, breaks when Y"
- A before/after or a specific example
- If the source note doesn't have hard numbers, use specific details instead
  — named tools, exact error messages, precise situations
- When the value is leverage (small input → big output), show the verbatim
  input. "Here's exactly what I typed" is stronger proof than any description
  of what you did — the reader sees the tiny cause and the large effect at once

**CTA (1–2 lines):**
- Ask a *specific* question tied to the post's topic, not a generic "what do
  you think?"
- Or: a direct invitation ("drop your setup in the comments", "DM me if you're
  dealing with this")
- Or: a soft tease ("next week I'll cover the flip side")
- Never: "Like and share if you found this useful"
- Never: nothing (a post with no CTA leaves momentum to die)

### 5. Compress to the right length

The ideal LinkedIn post is **1,300–2,500 characters** (roughly 200–400 words).
Posts under 400 characters consistently underperform. Posts over 2,500 are fine
but every paragraph must earn its place — no filler.

This target is for **standalone text posts only**. A media caption should be
far shorter — see step 2. Don't pad a caption to hit 1,300.

Count characters after formatting. If over 2,500, cut the weakest paragraph
or merge two that say similar things. If under 800, you probably haven't given
enough story — expand the middle section with one more specific detail.

### 6. Strip ALL non-LinkedIn formatting

Remove everything that LinkedIn's plain-text editor doesn't render:

**Must remove:**
- Markdown headers (`#`, `##`, `###`)
- Bold (`**text**`, `__text__`)
- Italic (`*text*`, `_text_`)
- Inline code (`` `code` ``)
- Code blocks (`` ``` ``)
- Blockquotes (`>`)
- Obsidian callouts (`> [!tip]`, `> [!takeaway]`, `> [!abstract]`, etc.)
- Frontmatter (the `---` YAML block at the top)
- Horizontal rules (`---`)
- Link syntax (`[text](url)`) — if a link is needed, mention it as plain text and
  say "link in comments"
- Image syntax (`![alt](url)`)

**Must NOT do:**
- Do NOT change, add, remove, or rephrase words to fit the format — restructure
  the order and shape, but preserve the original voice and content
- Do NOT add headers, bullet points, or numbered lists — LinkedIn is plain text
- Do NOT add emojis that weren't in the original
- Do NOT add hashtags unless the user asks
- Do NOT add "I hope this helps!" or other filler closers

**Formatting is whitespace only:**
- One blank line between every paragraph
- Short paragraphs (1–3 sentences max)
- No indentation, no bullets, no dashes as list markers
- Whitespace IS the formatting — it's what makes mobile readers stop and read

### 7. Style pass

Apply these voice rules to the output:

- **First person, always.** "I built", "I hit this error" — never "the user",
  never third person
- **Concrete over abstract.** "X errored with `ECONNREFUSED`" beats
  "had connection issues"
- **Show the detours.** The challenges and failures are the most engaging part
- **Confident, not qualified.** Remove "almost", "very", "really", "basically",
  "kind of"
- **No clinical language.** Never "utilize", "stakeholder", "individual",
  "leverage"
- **No AI tell phrases.** Never "In today's fast-paced landscape",
  "Here are N things you need to know", "Let's dive in"
- **Match intensity to substance.** A quick fix gets a tight post. A deep
  exploration gets a deeper one. Never pad.

### 8. Present and ask where to save

Present the formatted post as plain text (no labels, no "Hook:", no "Story:").
Read it as-is: one continuous text with blank line breaks.

Then ask:
- "Where should I save this?"

Let them specify the full path or a folder. If vague, ask again — never guess.

Name the file: `YYYY-MM-DD - linkedin-<slug>.md` where `<slug>` is a short
phrase (3–5 words). The content inside is plain text with blank-line breaks.
The file extension is `.md`.

### 9. Optional: character count and suggestions

After saving, report:
- Character count (warn if under 800 or over 3,000 — but a media caption is
  expected to be far shorter; see step 2)
- Whether it includes any of the top engagement levers (specificity, emotional
  pull, number in hook, image-worthy moment)
- If no number appears in the first ~140 characters, suggest adding one
- If it reads like a lecture (no personal story, no failure, no detour), suggest
  reframing as a journey/confession

## Pitfalls

- **Do NOT default to a long text post when the post is a caption.** If there's
  a video, image, or carousel attached, the media carries the story. A caption
  is 1–4 lines; its only job is to make someone watch and comment. Retelling the
  story in text buries the asset and competes with it. Decide caption vs
  standalone first (step 2) — it changes the entire output.
- **Do NOT write a summary.** This is not a TL;DR of the note. It's one sharp
  arc, restructured for LinkedIn. Summaries are boring. Arcs are shareable.
- **Do NOT preserve the note structure.** The note has 5–6 sections. The LinkedIn
  post has 4 parts, flowing as narrative. The order will change. The sections
  will merge. That's the point.
- **Do NOT include markdown in the output.** No headers, no bold, no callouts,
  no code blocks, no frontmatter, no link syntax, no horizontal rules. Plain
  text with blank-line breaks only.
- **Do NOT add bullets or numbered lists.** LinkedIn doesn't render them as
  structured lists. They appear as plain text. Use short paragraphs instead.
- **Do NOT put external links in the post body.** LinkedIn deprioritises posts
  with outbound links (~15% fewer impressions). Mention the resource and say
  "link in comments" if needed.
- **Do NOT add emojis unless the source already has them.** Clean text without
  emojis reads as more credible in most professional contexts.
- **Do NOT exceed 3,000 characters.** That's LinkedIn's hard limit. Anything
  over gets truncated on publish. If the content needs more, it should be a
  LinkedIn Article, not a post.
- **Do NOT add hashtags unprompted.** If the user wants hashtags, add 3–5
  specific ones at the end. Never add generic ones like #marketing or
  #leadership. Never add more than 5.
- **Do NOT change the original voice.** The post should sound like the person
  who wrote the note, not like a content marketing template. Restructure the
  shape and order — do not rewrite the words.
- **Do NOT save anywhere without asking.** Always ask where to save first.
- **Do NOT lose the specificity.** If the note says "ECONNREFUSED on port 5432
  because Docker overlay shadowed the env var", keep every detail. Specificity
  is the single strongest engagement lever (68% beat rate in data). Never
  generalise away the detail that makes the post worth reading.

## Verification

After writing the post:

1. No markdown formatting in the output (no `#`, no `**`, no `>`, no `` ` ``,
   no `---`, no `[text](url)`, no callouts, no frontmatter).
2. First line is 5–12 words and creates tension or names a specific outcome.
3. Character count is between 800 and 3,000 (ideal: 1,300–2,500).
4. Structure follows Hook → Story → Proof → CTA (no section headers — just flow).
5. Every paragraph is 1–3 sentences, separated by a single blank line.
6. First person throughout — no "the user" or third-person references.
7. At least one concrete detail (number, named tool, specific error, or exact
   situation) appears in the first ~140 characters.
8. No external links in the post body.
9. No AI tell phrases or generic filler.
10. File saved as `.md`, user chose the path, and the file exists.
