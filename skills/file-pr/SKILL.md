---
name: file-pr
description: File a pull request. Use when the user asks to file, open, or create a PR.
---

# File PR

Check first whether a PR for this branch already exists. Then read the diff against the default branch and confirm it actually does what was asked. PRs that quietly do something else get found in review, not before.

## Title

The title usually becomes the commit message, so follow the repo's conventions. Look at recently merged PRs and `git log` for what that looks like here. Write a title a human can read, one that says why the change matters.

- Bad: `perf(server): negotiate per-message deflate on the websocket`
- Good: `perf(server): cut websocket frame size by 70% with gzipping`

## Description

Start with the problem, in plain language, the way the user described it when they asked for the work. Then the fix, briefly. Not a list of files touched. Nobody reads a list of files touched.

- Bad: "Removed implicit workspace carryover from every new thread entry point. New threads inherit only the project from context, branch worktree, …"
- Good: "My new worktree default was ignored when starting new threads on existing worktrees. Super unintuitive — now your preferences always apply."

The test: someone who has never seen this code should finish the description knowing what was broken and why it works now.

Open a real PR, not a draft, unless the user asks. Drafts don't get review bots.

Screenshots for UI changes. Short video for anything that moves. End the description with the model and harness that did the work. If you don't know the model, say so instead of guessing.

After filing, the babysit-pr skill keeps it green.
