# Autoskilling

My agent skills.

Portable, runtime-agnostic `SKILL.md` files — no dependencies, no lock-in. Drop them into any agent that supports the [Agent Skills spec](https://agentskills.io/) and they work.

## Skills

| Skill | Description |
|---|---|
| [value-capture](value-capture/) | Turn any session into a structured Obsidian note — real process, dead ends, failures, and one sharp insight. |
| [md-to-x-thread](md-to-x-thread/) | Convert any markdown document to plain text formatted for X/Twitter — strip formatting only, change zero words. |
| [linkedin-post-format](linkedin-post-format/) | Convert a value-capture note into a LinkedIn-optimized text post — Hook → Story → Proof → CTA, stripped and restructured for the feed. |

## Install

```bash
npx skills add oteroantoniogom/autoskilling --skill value-capture
```

Works with Claude Code, Cursor, Windsurf, pi, or any agent that reads `.agents/skills/`.

## License

MIT
