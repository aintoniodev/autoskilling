---
name: value-capture
description: >-
  Turn any session into a structured Obsidian note that captures what was
  done, how it happened, the challenges faced, what didn't work, and the
  key insights — ready to be repurposed into content. Works for coding,
  research, design, planning, writing, or any creative/technical session.
  Triggers: "/value-capture", "capture this session", "save session note",
  "session recap", "value capture", "log this session".
---

# Value Capture — Session → Obsidian Note

Capture the signal from a session and write it as a structured,
content-ready Obsidian note. The note goes to the vault. The exact folder is **asked each time** — never assume a folder structure or hardcode a path.

> [!tip] Why this exists
> Your feed is flooded with recycled slop. The people who stand out are the
> ones who *do the work*, then share what they actually learned — not what others
> said. This skill automates turning raw sessions into notes you can
> refine into posts, threads, or long-form content.

## How It Works

The skill gathers evidence from available sources, then synthesizes one note:

| Source | Method | What it provides |
|---|---|---|
| Git history (if applicable) | `git log`, `git diff --stat`, `git diff` | What files changed, commits made, lines added/removed |
| Session context | Context layer (if available) | Decisions, errors, blockers, rejected approaches captured during the session |
| Live conversation | Agent's own context | The narrative thread — what was hard, what clicked, what was learned |

## Procedure

### 1. Detect the session scope

If working in a git repo, gather the history:

```bash
# Find the session boundary: look for commits from today in the current repo
git log --oneline --since="$(date +%Y-%m-%dT00:00:00)" --format="%h %s (%ar)"

# If no today commits, fall back to last N commits
git log --oneline -20 --format="%h %s (%ar)"

# Get changed files and stats
git diff --stat HEAD~5..HEAD 2>/dev/null || git diff --stat HEAD
```

If not in a git repo, or if there are no commits and no changed files, ask what the session was about and proceed from the description alone.

### 2. Review what happened

Reconstruct the session narrative from:
- The git log and diff (from step 1, if applicable)
- The session context layer (if available) — decisions, errors, dead ends, corrections
- The agent's conversation memory
- Anything notable from the person's own description

If the context layer is unavailable or returns nothing (new session, no indexed events),
fallback to git evidence + conversation memory. The note will be shorter but still honest.

If evidence is thin overall (no git changes, no deliverables, short session), say so — don't fabricate.

### 3. Synthesize the note

Using the gathered evidence, write the note following the **Note Template**
below. Rules:

- **Be specific.** Name the exact tool, decision, or situation that caused the
  friction. Never write "had an issue with X" — write "X errored with
  `ECONNREFUSED` because the env var `PORT` was shadowed by a Docker overlay",
  or "I chose framework A over B because C".
- **Show, don't tell.** Describe the outcome, not the effort. "The build went from
  14s to 2s" not "I worked really hard on optimizing the build". Remove
  qualifiers: "almost", "very", "really".
- **One idea per section.** Each heading advances one argument. Build a logical
  flow from goal → process → challenges → insight.
- **Capture failures honestly.** What didn't work is more valuable than what did.
  Readers learn from your dead ends.
- **Extract the lesson.** Every challenge section should end with a one-line
  takeaway — the thing someone reading this should remember.
- **Write in the language the session was in.** The note structure (headings,
  frontmatter keys) is always English. The prose content auto-detects: if the
  session was in Spanish, write Spanish. If English, write English.
- **Don't inflate.** If the session was short and the outcome was small, the
  note should reflect that. No padding.
- **First person, always.** Write as if the person who did the work is writing the note.
  "I built", "I hit this error", "I tried X but it didn't work". Never write in
  third person. Never use the word "user" — it's clinical and kills the voice.
- **Never leak personal paths.** Anonymize any absolute paths that contain
  usernames or personal directory names before writing to the note. Use
  relative paths or placeholders like `<vault>/Session Notes/`.

### 4. Ask where to save and write the note

**Ask:**
- "Where in your vault should I save this note?"

Let them specify the full path or a folder. If they give no path or say something vague, ask again — never guess.

Name the file: `YYYY-MM-DD - <title>.md` where `<title>` is a short slug (3-6 words).

### 5. Report and optional thread conversion

Tell them:
- Where the note was saved
- A one-line summary of what was captured
- Any content angles that stand out (e.g. "this has a strong thread about X
  that could work as a standalone post")

Then ask:
- "Want me to convert this note into an X-ready thread or a LinkedIn post?"

**X/Twitter thread:**
If they say yes to X, apply the **md-to-x-thread** procedure to the
just-saved note: read it, strip all markdown formatting (headers, callouts,
frontmatter, bold, italic, code, links, horizontal rules), and present the
plain text. Then ask where to save the thread file (always `.md`).

**LinkedIn post:**
If they say yes to LinkedIn, apply the **linkedin-post-format** procedure to
the just-saved note: read it, identify the strongest arc, restructure into
Hook → Story → Proof → CTA, strip all markdown/Obsidian syntax, compress
to 1,300–2,500 characters, and present the plain text. Then ask where to
save the post file (always `.md`).

If they say no or skip both, you're done.

## Note Template

```markdown
---
title: "<descriptive title>"
date: YYYY-MM-DD
type: session-note
tags:
  - session-note
  - <domain/topic tag>
  - <relevant tag if applicable>
project: "<project or topic name>"
duration: "<approximate session duration if detectable>"
---

# <descriptive title>

> [!abstract] TL;DR
> One paragraph that captures the essence: what was done, the main challenge,
> and the key takeaway. Someone should be able to read just this and get value.
> Lead with the outcome, not the activity.

## What I Did / Explored

<What was the goal? What did you actually accomplish or discover? Be specific about
the output — a script, a fix, a design, a decision, a research finding, a piece
of writing, a proof of concept, an insight reached.>

## The Process

<Walk through how it actually happened. Not a sanitized tutorial — the real
sequence with the real detours. Include relevant commands, code snippets, config
fragments, quotes, or decisions that would save someone time.

Open with what triggered the session (a bug, a tweet, an idea, a client need,
a question). Then the real sequence — including wrong turns.>

## Challenges

### <Challenge 1 title>

<What went wrong? What error, misunderstanding, or friction point did you hit?
Name the exact error, the exact command that failed, the exact assumption that
was wrong — or the exact decision that was hard.>

> [!takeaway] Lesson
> <One-line insight someone should remember from this.>

### <Challenge 2 title>

<Same structure. Have as many as the session warrants — could be 0, could be 5.>

## What Didn't Work

<Things you tried that dead-ended. Approaches you rejected and why. This is
the most valuable section for readers — everyone publishes the path that worked,
almost no one publishes the paths that didn't.

Each dead end gets one paragraph: what you tried → why it failed → what you
did instead.>

## Key Insight

<The single most valuable thing you learned this session. The thing that, if
you'd known it beforehand, would have saved you the most time.

This is the peak of the note (Peak-End Rule). Make it specific, not generic.
"When X errors with Y, it means Z" — not "patience is important".
"I realized A is actually B" — not "always double-check".>

---
*[project]: <project or topic name>*
*[tags]: <all tags>*
```

## Pitfalls

- **Context-aware filtering.** Not everything that happened during the session belongs in the note. Agent plumbing (shell errors, tool wrapper quirks, context-mode throttling) is implementation noise — skip it. Ask: "Would someone reading about *this project* find this useful?" If the answer is about how the agent ran commands, not about what was done, cut it.
- **Don't fabricate.** Only capture what actually happened in the session. If
  the evidence is thin (no git changes, no deliverables, short session), say so in the
  note rather than inventing detail.
- **Don't overwrite.** If a note for today already exists, append to it or ask
  whether to create a new one with a different slug.
- **Context layer might be empty.** If the context search returns nothing (new session,
  no indexed events), fall back to conversation context and git
  evidence only. The note will be shorter but still honest.
- **Vault path must exist.** Always `mkdir -p` the target folder before
  writing. Fail clearly if the specified path doesn't exist.

## Narrative & Style Principles

The note is shareable content, not a changelog. Apply these when writing:

**Hook the reader.** The TL;DR is the hook. Lead with the outcome, not the activity.
"I cut my build from 14s to 2s by removing a single dependency" beats
"I worked on build optimization today". But also: "I realized X about Y" or
"I found that Z doesn't work the way everyone assumes" — the hook is the
insight, not just the metric.

**Concrete over abstract.** "X errored with `ECONNREFUSED`" beats "had connection
issues". "I chose A because B, not C" beats "I considered the options".
Numbers, specifics, exact details — never hand-waving.

**Show the detours.** The most engaging content shows what went wrong before it
went right. Readers don't connect with flawless execution — they connect with
real problems. This is why the Challenges and What Didn't Work sections matter.

**Specific takeaway, not fortune cookie.** "When PowerShell routes your commands,
it silently drops `&&` chains" beats "always check your environment". If you can
swap the lesson into another note and it still reads true, it's too generic.

**Filter out noise.** Not everything that happened is worth including. Agent plumbing, shell quirks, and tool wrapper errors are implementation noise — skip them. Ask: "If someone is reading about *this project*, does this help them?" If the answer is only about how the agent ran commands, cut it.

**Match intensity to substance.** A quick fix gets a tight note. A deep exploration
gets a deeper one. Never pad short sessions with generic wisdom to hit a word count.

**Confident, not qualified.** Remove "almost", "very", "really", "basically",
"kind of". They weaken every sentence they touch.

**No clinical language.** Never use words like "user", "individual", "stakeholder",
"utilize". If it sounds like a Jira ticket, rewrite it. The note should read like
a conversation with a peer, not a bug report.

**The note is an atom.** Each section (challenge, failure, insight) should be able
to stand alone as a tweet, a thread point, or a slide. Write with that in mind.

## Verification

After writing the note:
1. Confirm the file exists at the expected path.
2. Verify frontmatter is valid YAML (no unescaped colons, proper string quoting).
3. Confirm no absolute personal paths leaked into the note content.
4. Confirm the note reads as first-person throughout — no "the user" references.
5. Confirm the note is agent/runtime agnostic — no tool-specific names leaked.
6. Check that the TL;DR actually summarizes the full note — not a generic cliché.
