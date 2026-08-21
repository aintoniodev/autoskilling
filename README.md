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
| [linkedin-profile-archive](linkedin-plugin/) (**plugin**) | Archive a LinkedIn profile's full posting history (text + images + metrics) into a local folder. Drives a logged-in Chromium session over CDP to capture LinkedIn's internal voyager API, paginates to the last post, and downloads images through the browser.
| [scientific-synthesis](scientific-synthesis/) | Produce a rigorous multi-source synthesis with confidence grading, thematic integration, and conflict reconciliation. |
| [delegate](delegate/) | Multi-model orchestration: the main session (GLM 5.2) plans and delegates contracts to a fast executor subagent (DeepSeek V4 Flash) in parallel. |
| [swarmforge](swarmforge/) | SwarmForge (Uncle Bob's tmux-based multi-agent orchestration) as an Agent Plugin 1.0.0: bootstrap two-pack/four-pack/six-pack workflows, configure roles + layered constitution, run handoffs, clean shutdown. Ships a native-Windows stack (bash + psmux + bb.exe, no WSL). |
| [agent-plugin-authoring](agent-plugin-authoring/) | Author Agent Skills and package them as Agent Plugins 1.0.0: SKILL.md frontmatter rules, directory layout, plugin.json manifest, validation with the bundled spec validator. |
| [video-to-text](video-to-text/) | Extract transcript text from videos (TikTok, YouTube, any URL, local files) — yt-dlp + ffmpeg + faster-whisper, fully local, no API keys. Ships executable code in `scripts/` (vxtract.py): .txt/.md/.srt output, es/en/auto, CPU or CUDA. |
| [autoresearch](autoresearch/) | Autonomous experiment loop, agent-native (no extension): pick an idea, implement, measure against a baseline, keep wins / revert regressions, log every run in `.auto/log.jsonl`, resume from disk alone. Distilled from davebcn87/pi-autoresearch. |
| [fusion-models](fusion-models/) | Fuse models instead of racing them — cast subagents as ARCHITECT, BUILDER, VALIDATOR, JUDGE, ATTACKER, COORDINATOR: opinion, fusion merge, gate-first validation, debate, council (Borda), redteam, coordinate, and the full gauntlet pipeline. Distilled from disler/fusion-harness. |

## Install

```bash
npx skills add aintoniodev/autoskilling --skill value-capture
npx skills add aintoniodev/autoskilling --skill md-to-x-thread
npx skills add aintoniodev/autoskilling --skill launch-video-kit
npx skills add aintoniodev/autoskilling --skill linkedin-post-format
npx skills add aintoniodev/autoskilling --skill scientific-synthesis
npx skills add aintoniodev/autoskilling --skill autoresearch
npx skills add aintoniodev/autoskilling --skill fusion-models
npx skills add aintoniodev/autoskilling --skill delegate
```

`swarmforge/` is an **Agent Plugin 1.0.0** package (not a plain skill): install it
with an Agent Plugins compatible client from `swarmforge/plugin.json`, or copy the
skill directory directly into your agent's skills folder:

```bash
cp -r swarmforge/skills/swarmforge ~/.pi/agent/skills/swarmforge
```

See `swarmforge/README.md` for details.

The `delegate` skill also ships an agent: copy `delegate/agents/executor.md`
to `~/.pi/agent/agents/` (or your agent dir) so the subagent tool can find it.

## Testing

The `delegate` skill ships a test suite (static + mutation + real-API
integration):

```bash
cd delegate
python -m pytest tests/ -q          # static suite, free
python scripts/mutate.py            # mutation testing, 27 mutants, free
RUN_INTEGRATION=1 python -m pytest tests/test_integration.py -q   # ~$0.0008, real API
```

`tests/` and `scripts/` only depend on pytest — no other setup.

Works with Claude Code, Cursor, Windsurf, pi, or any agent that reads `.agents/skills/`.

## License

MIT
