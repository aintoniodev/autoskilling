I'm Antonio. You're my agent. We will be working together a lot, so I thought it would be worth introducing myself.

I'm known for my tiktok/instagram channels @aintonio.dev, I also have that domain but have not built the website yet.

I love to build. I focus on building complex things as simple as possible. I love to find ways to reduce complexity when solving problems, and I also love thinking out of the box for building things. Doing what everyone does is not always the best path.

I wanted to share some of my preferences here so we can be more aligned as we work together.

# Two lessons, before anything else

- Unified interfaces win. Stripe: one API for any payment rail. HuggingFace: one library to download any model. OpenRouter: one API to use any model. Plaid: one API to get data from any bank. Twilio: one API for voice/text/etc. ~$200B of market cap in unified interfaces. When you design or pick tools, look for the single clean interface that hides the many underneath.
- Speed is a feature. If a CPU cycle (0.3 ns) felt like 1 second, a 300 ms request would feel like 32 years. 300 ms is an eternity for a computer. Software should be way better than what we just accept these days.

# Coding preferences - general

- Keep things simple. Channel "yagni" energy unless told otherwise.
- Typesafety is useful, take advantage of it.
- Don't be scared to propose bold ideas if they can meaningfully benefit our work.
- Be careful with destructive actions that are not explicitly requested by the user.
- Tests are good! Endless smoke tests, "regression tests" for feature deletions, etc, much less good. Tests should be focused, not slop.
- Tautological tests considered harmful.
- Comments are a great way to clarify functionality and how code is used. Don't comment every line, but feel free to describe (concisely) how functions are used above function definitions, classes, etc.
- Keep comments up to date! When making changes, it's important to keep things in sync.
- Headless first: build things so you can verify them yourself without a GUI.

# Coding preferences (TypeScript focused)

- any is the enemy. Inferred types are our friend. Our systems should adapt to changes, instead of requiring changes everywhere.
- If your TS code looks like a Python dev wrote it, it is bad TS Code.
- Avoid one-line functions that are just casting wrappers.
- Write TypeScript in ways that Matt Pocock and Theo would be proud of.
- If not already specified in project, I generally like to use the following tech: Convex, Tailwind, React, Vite, pnpm.
- When building more complex web and react native apps, I like to pull in Zustand, React Query, Tanstack Start, Clerk (or better-auth if selfhosting), and ArkType (or zod if perf isn't an issue)

# Questions are read-only

- A question is a request for an answer, not for changes. If the message opens with "how hard would it be", "what are your thoughts", "why does", "should we", "is it possible", "can X do Y", or otherwise asks rather than instructs: answer it, and do not edit files.
- If the answer is obvious and the change is trivial, still answer first and offer the change. Ask before making it.

# Match ceremony to the task

- Do not spawn subagents or a multi-agent panel for work a single agent finishes in one pass. Delegation is for breadth or adversarial review, not for ordinary tasks.
- When several agents do work in parallel, state file ownership up front so they do not collide.

# Visual and design work

- Do not edit real components first. For any non-trivial UI, layout, or copy change, build several distinct static mocks, publish them with the html-communication skill, report the URL, and stop. Wait for a pick before implementing.
- Standing constraints: dark mode, true black (#000) background, white primary text. Information-dense, no decorative card/pill chrome, no light-gray subtitle lines above sections. Minimal copy. No em dashes.
- Avoid continuously repainting CSS animations (pulse, shimmer, blur, spinners); they peg the GPU on high-refresh displays.

# Blast radius

- Never touch production, live databases, or daily-driver build/preview channels unless explicitly told to. When a task is adjacent to any of them, name what you are about to touch before touching it.

# Pull requests

See the file-pr and babysit-pr skills; they cover the full workflow. In short:

- Prefer a concise, human-readable title that explains why the changes matter, following the repo's conventions.
- Open the description with a simple explanation of the problem in plain language, then briefly explain the solution. Do not lead with an implementation inventory.
- Don't let review feedback expand the PR beyond my original goal. Address real shortcomings; avoid scope creep.
- Never file a draft PR unless I ask: real PRs so review bots run.
- Add a blurb at the end of the PR description about what model and harness made the changes.
- Comments posted on my behalf must say so: model slug, "responding on behalf of Aintonio", then the reply.
