#!/usr/bin/env python3
"""Validate an Agent Skill and/or Agent Plugin (1.0.0) directory.

Checks, against the official specs (agentskills.io / agent-plugins.org):
  - SKILL.md exists; YAML frontmatter parses; required fields present.
  - name: 1-64 chars, lowercase alnum + hyphens, no edge/consecutive hyphens,
    matches the parent directory name.
  - description: 1-1024 chars.
  - license/compatibility: length constraints when present.
  - Body < 500 lines (spec recommendation).
  - Relative file references in the body resolve.
  - If plugin.json exists: validates against the official 1.0.0 schema
    ($schema const + name required, no additional top-level keys).

Usage: python validate-plugin.py <plugin-or-skill-dir> [<plugin-or-skill-dir>...]
Exit code 0 = all valid, 1 = errors found.
"""
import json
import re
import sys
from pathlib import Path

PLUGIN_SCHEMA_URL = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
PLUGIN_ALLOWED_KEYS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "extensions",
}
NAME_RE = re.compile(r"^[a-z0-9-]+$")
MAX_NAME = 64
MAX_DESC = 1024
MAX_COMPAT = 500
MAX_BODY_LINES = 500


def errors_found(errors):
    return len(errors) > 0


def parse_frontmatter(text):
    """Return (frontmatter_dict, body) or (None, None) if invalid."""
    if not text.startswith("---\n"):
        return None, None
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None, None
    fm_text, body = parts[1], parts[2]
    # Minimal YAML subset parser (scalar lines + block scalars with >- / |)
    fm = {}
    key, acc, folded = None, [], False
    for line in fm_text.splitlines():
        if line.startswith((" ", "\t")) and key is not None:
            acc.append(line.strip())
            continue
        if key is not None:
            fm[key] = " ".join(acc).strip() if folded else "\n".join(acc).strip()
            key, acc, folded = None, [], False
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        if v in (">-", ">", "|"):
            key, acc, folded = k, [], (v in (">-", ">"))
        else:
            fm[k] = v.strip("\"'")
    if key is not None:
        fm[key] = " ".join(acc).strip() if folded else "\n".join(acc).strip()
    return fm, body


def validate_skill(skill_dir, errors):
    sk = Path(skill_dir)
    skill_md = sk / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"[{sk.name}] SKILL.md not found in {sk}")
        return
    text = skill_md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if fm is None:
        errors.append(f"[{sk.name}] SKILL.md frontmatter missing or malformed (must start with '---\\n')")
        return

    name = fm.get("name")
    if not name:
        errors.append(f"[{sk.name}] frontmatter 'name' is required")
    else:
        if len(name) > MAX_NAME:
            errors.append(f"[{sk.name}] name exceeds {MAX_NAME} chars")
        if name != name.lower() or not NAME_RE.match(name):
            errors.append(f"[{sk.name}] name '{name}' must be lowercase alnum + hyphens only")
        if name.startswith("-") or name.endswith("-"):
            errors.append(f"[{sk.name}] name cannot start/end with hyphen")
        if "--" in name:
            errors.append(f"[{sk.name}] name cannot contain consecutive hyphens")
        if name != sk.name:
            errors.append(f"[{sk.name}] frontmatter name '{name}' must match directory name '{sk.name}'")

    desc = fm.get("description")
    if not desc:
        errors.append(f"[{sk.name}] frontmatter 'description' is required")
    elif not (1 <= len(desc) <= MAX_DESC):
        errors.append(f"[{sk.name}] description must be 1-{MAX_DESC} chars (got {len(desc)})")

    if "license" in fm and len(fm["license"]) > 64:
        errors.append(f"[{sk.name}] license field too long")
    if "compatibility" in fm and len(fm["compatibility"]) > MAX_COMPAT:
        errors.append(f"[{sk.name}] compatibility must be <= {MAX_COMPAT} chars")

    if body is not None and body.count("\n") > MAX_BODY_LINES:
        errors.append(f"[{sk.name}] SKILL.md body exceeds {MAX_BODY_LINES} lines (progressive disclosure)")

    if body:
        for ref in re.findall(r"\]\(([^)#]+)\)", body):
            if ref.startswith(("http://", "https://", "#")):
                continue
            if not (sk / ref).exists():
                errors.append(f"[{sk.name}] reference '{ref}' does not resolve")


def validate_plugin(plugin_dir, errors):
    pj = Path(plugin_dir) / "plugin.json"
    if not pj.is_file():
        return  # not a plugin; bare skill
    try:
        data = json.loads(pj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"[{pj.name}] invalid JSON: {e}")
        return
    if not isinstance(data, dict):
        errors.append(f"[{pj.name}] must be a JSON object")
        return
    if data.get("$schema") != PLUGIN_SCHEMA_URL:
        errors.append(f"[{pj.name}] $schema must be '{PLUGIN_SCHEMA_URL}'")
    if not data.get("name"):
        errors.append(f"[{pj.name}] 'name' is required")
    else:
        name = data["name"]
        if not (1 <= len(name) <= 64) or not re.match(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$", name):
            errors.append(f"[{pj.name}] invalid plugin name '{name}'")
    extra = set(data) - PLUGIN_ALLOWED_KEYS
    if extra:
        errors.append(f"[{pj.name}] unknown keys (schema additionalProperties=false): {sorted(extra)}")
    # skills dir must exist with at least one SKILL.md
    skills_dir = Path(plugin_dir) / "skills"
    if skills_dir.is_dir():
        found = list(skills_dir.rglob("SKILL.md"))
        if not found:
            errors.append(f"[{pj.name}] skills/ present but no SKILL.md found under it")
        else:
            for f in found:
                validate_skill(f.parent, errors)
    else:
        errors.append(f"[{pj.name}] plugin must contain a skills/ directory")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    errors = []
    for target in argv:
        p = Path(target)
        if not p.is_dir():
            errors.append(f"[{target}] not a directory")
            continue
        validate_plugin(p, errors)
        if not (p / "plugin.json").is_file():
            validate_skill(p, errors)
    if errors_found(errors):
        for e in errors:
            print(f"ERROR: {e}")
        print(f"\n{len(errors)} problem(s) found.")
        return 1
    print("OK: all targets valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
