---
name: agent-plugin-authoring
description: >-
  Author Agent Skills and package them as Agent Plugins (1.0.0). Covers the Agent Skills
  format (SKILL.md frontmatter rules, scripts/, references/, assets/, progressive
  disclosure) and the Agent Plugins package format (plugin.json manifest, skills/ and
  mcp.json components, extension namespaces). Use when creating a new skill, converting an
  existing skill into a portable plugin, or validating a skill/plugin against the official
  specifications. Keywords: agent skills, agent plugins, SKILL.md, plugin.json, agentskills,
  agent-plugins, skill authoring, skills-ref.
license: MIT
compatibility: python 3.8+ for the bundled validator (optional); any agent that reads SKILL.md
metadata:
  skills-spec: https://agentskills.io/specification
  plugins-spec: https://agent-plugins.org
  version: 1.0.0
---

# Authoring Agent Skills and Agent Plugins

This skill guides you through authoring an **Agent Skill** (agentskills.io) and packaging
it as an **Agent Plugin** (agent-plugins.org, v1.0.0). Both are open, vendor-neutral
formats: a skill is a directory with a `SKILL.md`; a plugin is a directory with a
`plugin.json` manifest that can bundle one or more skills plus MCP servers.

## When to Use

- The user asks to "create a skill", "make a plugin", "package this as an agent skill",
  or "convert X into a skill".
- You need to validate an existing `SKILL.md` or `plugin.json` against the specs.
- You are structuring a new skill directory and need the exact frontmatter rules,
  directory layout and naming constraints.

Do NOT use for: pi-specific `.pi` skills with nonstandard frontmatter (this skill targets
the portable Agent Skills/Agent Plugins standards), or for writing the *content* of a
skill about a specific domain (that's the authoring work — use this skill for format and
packaging).

## Procedure

### 1. Determine the deliverable

Ask or decide: a bare **skill** (directory with `SKILL.md`) or a **plugin** (directory
with `plugin.json` + `skills/<name>/SKILL.md`). A plugin is the distributable package:
it can hold several skills, an optional `mcp.json`, and client extensions. If in doubt,
recommend the plugin format — it is the current packaging standard.

### 2. Create the skill directory (Agent Skills format)

```
my-skill/
├── SKILL.md          # required: frontmatter + instructions
├── scripts/          # optional: executable code (python, bash, js...)
├── references/       # optional: docs loaded on demand (REFERENCE.md, FORMS.md...)
└── assets/           # optional: templates, images, data files
```

**SKILL.md frontmatter — exact rules:**

| Field | Required | Constraints |
| --- | --- | --- |
| `name` | yes | 1–64 chars; lowercase letters, numbers, hyphens; no leading/trailing/consecutive hyphens; **must equal the parent directory name** |
| `description` | yes | 1–1024 chars; non-empty; says what the skill does AND when to use it; include search keywords |
| `license` | no | license name or reference to a bundled license file |
| `compatibility` | no | ≤500 chars; environment requirements |
| `metadata` | no | arbitrary string→string map (keys/values as strings) |
| `allowed-tools` | no | space-separated pre-approved tools (experimental) |

**Body rules:**

- Keep `SKILL.md` under **500 lines** (spec recommendation). Progressive disclosure:
  the agent loads `name`+`description` at startup, the full body on activation, and
  `scripts/`/`references/`/`assets/` files only when needed.
- Reference other files with **relative paths from the skill root**, one level deep
  (`scripts/`, `references/REFERENCE.md`, `assets/...`). Avoid deep reference chains.
- Split long material into `references/` files instead of bloating `SKILL.md`.
- `scripts/` files should be self-contained, with helpful error messages and graceful
  edge-case handling.

### 3. Package as an Agent Plugin (if applicable)

```
my-plugin/
├── plugin.json
├── skills/
│   └── my-skill/
│       └── SKILL.md
├── mcp.json          # optional: stdio / Streamable HTTP / HTTP+SSE MCP servers
└── com.example.client/   # optional: client-specific extension namespaces
```

**plugin.json (Agent Plugins 1.0.0)** — validate against
`https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What this plugin does.",
  "author": { "name": "Your Name", "url": "https://example.com" },
  "homepage": "https://example.com/plugin",
  "repository": "https://github.com/you/my-plugin",
  "license": "MIT",
  "keywords": ["skill", "plugin"],
  "extensions": { "com.example.client": { "any": "client-specific data" } }
}
```

Manifest rules: `$schema` (const, required) + `name` (required) + any of the optional
fields above; **no additional top-level keys** (`additionalProperties: false`). Extension
namespaces are reverse-domain keys with client-defined contents.

### 4. Validate

Bundled validator (no dependencies, python 3.8+):

```bash
python scripts/validate-plugin.py <plugin-or-skill-dir>
```

It checks: SKILL.md frontmatter (name format + directory match, description length,
license/compatibility constraints), body length < 500 lines, relative file references
resolve, and (for plugins) the manifest against the official schema. You can also use the
official reference implementation (pip-installable `skills-ref` from
github.com/agentskills/agentskills) for a second opinion.

### 5. Ship

- Test the skill from the consumer side: load `SKILL.md`, follow its instructions once.
- Document install paths for clients (copy `skills/<name>/` into the agent's skills dir,
  or plugin install flow via `plugin.json`).
- Add attribution and license notes; if the source material has no license, say so.

## Pitfalls

- **Name/directory mismatch** — the most common validation failure. The `name` field must
  match the parent directory name exactly (`skills/swarmforge/SKILL.md` → `name: swarmforge`).
- **Non-portable frontmatter** — pi/Claude/Cursor-specific fields are fine in client
  extensions but break the portable spec. Keep the core frontmatter to the allowed fields.
- **Overlong SKILL.md** — >500 lines defeats progressive disclosure. Move detail to
  `references/`.
- **Absolute paths in a portable skill** — skills must work on any machine; use relative
  paths and env vars.
- **`additionalProperties` in plugin.json** — the 1.0.0 schema rejects unknown top-level
  keys. Put client-specific data under `extensions`.
- **Forgetting `$schema` in plugin.json** — required (const) in 1.0.0.

## Verification

- `python scripts/validate-plugin.py <dir>` exits 0 with no errors.
- `name` matches the directory name; `description` ≤ 1024 chars.
- `SKILL.md` body ≤ 500 lines.
- Every relative reference in the body resolves to an existing file.
- `plugin.json` (if present) parses and contains only schema-allowed keys.
