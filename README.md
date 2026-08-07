# Autoskilling

My agent skills.

`SKILL.md` files that capture real workflows, rules, and verification steps
so an agent can follow them. Some are fully portable (no dependencies), others
document external tools and scripts with enough detail to replicate them.

## Skills

| Skill | Description |
|---|---|
| [value-capture](value-capture/) | Turn any session into a structured Obsidian note — real process, dead ends, failures, and one sharp insight. |
| [md-to-x-thread](md-to-x-thread/) | Convert any markdown document to plain text formatted for X/Twitter — strip formatting only, change zero words. |
| [launch-video-kit](launch-video-kit/) | End-to-end product/demo video as code (Remotion + AI voice + HTML/CSS UI). Discovery, concept, music, voice, subtitles, camera, render, and build-in-public content. |
| [linkedin-post-format](linkedin-post-format/) | Convert a value-capture note into a LinkedIn-optimized text post — Hook → Story → Proof → CTA, stripped and restructured for the feed. |
| [scientific-synthesis](scientific-synthesis/) | Produce a rigorous multi-source synthesis with confidence grading, thematic integration, and conflict reconciliation. |
| [delegate](delegate/) | Multi-model orchestration: the main session (GLM 5.2) plans and delegates contracts to a fast executor subagent (DeepSeek V4 Flash) in parallel. |

## Install

```bash
npx skills add oteroantoniogom/autoskilling --skill value-capture
npx skills add oteroantoniogom/autoskilling --skill md-to-x-thread
npx skills add oteroantoniogom/autoskilling --skill launch-video-kit
npx skills add oteroantoniogom/autoskilling --skill linkedin-post-format
npx skills add oteroantoniogom/autoskilling --skill scientific-synthesis
npx skills add oteroantoniogom/autoskilling --skill delegate
```

The `delegate` skill also ships an agent: copy `delegate/agents/executor.md`
to `~/.pi/agent/agents/` (or your agent dir) so the subagent tool can find it.

Works with Claude Code, Cursor, Windsurf, pi, or any agent that reads `.agents/skills/`.

## License

MIT
