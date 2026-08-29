---
name: babysit-pr
description: Monitor, watch, or babysit a PR until checks are green and reviews approve. Use when the user asks to monitor, watch, or babysit a PR, or to handle its review and CI feedback.
---

# Babysit PR

These repos run AI review bots. The bots are useful even when they're wrong, which is often. Your job is to loop until the PR is green and everyone has approved.

Poll the PR for new comments and checks, or use harness tools that watch it if they exist. Rebase when the base branch moves. Only act on comments and checks newer than the latest push; old feedback is already answered.

## Review feedback

Check every bot finding against the source before touching code. Fix the real ones and the real CI failures. A flaky runner is not a code problem, don't chase it. When you dismiss a false positive, write why in the reply and resolve the comment. If feedback isn't worth addressing, say so plainly and resolve it instead of quietly ignoring it.

If another PR lands that makes this one obsolete, stop, tell the user, and ask before closing. Closing someone's PR unasked is not your call.

## Ground rules

Comments you post on the user's behalf say so: model slug, "responding on behalf of <user>", then the reply.

The rule that matters most: review feedback does not grow the PR. Fix what's actually broken, and leave scope creep out. A PR that tripled in size addressing every nit is worse than one that addressed the real findings.
