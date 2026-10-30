---
name: file-pr
description: File a concise pull request. Use when the user asks to file, open, or create a PR.
metadata:
  credits:
    - skill: file-pr
      author: Theo Browne (T3)
      url: "https://github.com/t3dotgg/tstack/blob/main/skills/file-pr/SKILL.md"
    - skill: pr
      author: Matt Pocock
      url: "https://github.com/mattpocock/skills/tree/main/skills/engineering/pr"
---

# File PR

Before filing, check whether a PR for this branch already exists. Review the
diff locally against the base branch (usually `origin/main`) to make sure its
contents match the goal.

## Title

PR titles usually become commit messages, so follow the repository's title
conventions. Look at recently merged PRs and Git history for examples. Prefer a
concise, human-readable title that explains why the change matters:

BAD

> ❌ perf(server): negotiate permessage-deflate on the websocket

GOOD

> ✅ perf(server): cut websocket frame size by 70%+ with gzipping

## Body

When the repository has a PR template (`.github/pull_request_template.md` or
similar), build the body from it: keep its headings and follow its guidance.
`gh pr create --body` skips the template, so apply it yourself. If the repo has
a PR-body check (e.g. `scripts/check-pr-body.mjs`, `scripts/guardrails/pr.py`),
run it on the body before filing.

With no template, use this shape:

```markdown
<one sentence: the problem>

## Summary

<diagram, diff-sketch, or tree>

## Evidence

- **Before:** <screenshot/output/failing test run>
  **After:** <screenshot/output/passing test run>

## Merge Danger

**Door:** <one-way or two-way>

**Blast Radius:** <one word>

<optional: what could break>
```

Skip preambles beyond that first sentence and keep prose brief. Use the repo's
domain words from its glossary (e.g. `docs/internals/glossary.md`,
`spec/glossary.md`, `GLOSSARY.md`).

### Opening sentence

State the problem simply, in the user's words from their original prompt. Do
not lead with an implementation inventory:

BAD

> ❌ Removed implicit workspace carry-over from every "new thread" entry point (cmd+n / cmd+shift+o, sidebar v1/v2 buttons, command palette). Deleted buildContextualThreadOptions and the v1 sidebar's seed-context machinery.

GOOD

> ✅ My "new worktree" default was ignored when starting new threads on existing worktrees. Super unintuitive.

### Summary

Pick the smallest view that makes the key point clear: pseudocode, a call tree,
a component tree, a file tree, Mermaid, or a `diff` of one of those. One or two
views, not all. Keep only the calls, files, props, states and boundaries a
reviewer needs. See [references/summary-visuals.md](references/summary-visuals.md)
for examples of each.

### Evidence

Concrete proof the change works, before and after. Screenshots are best when
the change is visual and the environment can take them. Otherwise show the
exact test or command that failed before and passes after, with its output.

### Merge Danger

Two-way doors are cheap to roll back; destructive or hard-to-reverse changes
(migrations, deleted data, public API removals) are one-way. Blast radius is
who or what this can break: layout shift, consumers, mobile, deployments.

## Before submitting

Do not credit agents, models, harnesses, or review loops in the title or
description: no "Created with", "Generated with", "Made by", or "Reviewed with"
lines, and no robot badges. Keep verification evidence that stands on its own.

Check the title, description, quotes, and attachments for secrets and private
details.

Open a real PR rather than a draft so review bots run. If `gh pr create` fails
because the GraphQL rate limit is used up, open it through REST with
`gh api repos/<owner>/<repo>/pulls -f title=... -f head=... -f base=... -F body=@<file>`. If the user also asked
to babysit it, continue with the `babysit-pr` skill.

Do not post a follow-up PR comment unless it serves the user's request. When a
comment is needed, use the `leaving-pr-comments` skill.
