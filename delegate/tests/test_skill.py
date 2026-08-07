"""Tests estáticos de SKILL.md — el contrato de comportamiento del skill.

Cada test fija un comportamiento que el skill DEBE documentar. El mutation
testing (scripts/mutate.py) borra o altera estos comportamientos uno a uno y
re-ejecuta esta suite: una mutación que sobrevive indica un hueco aquí (o un
comportamiento que el skill no documenta)."""

import re


def test_frontmatter_identity(skill_md):
    m = re.search(r"^name:\s*(\S+)", skill_md, re.M)
    assert m and m.group(1) == "delegate", "frontmatter name must be 'delegate'"
    assert re.search(r"^description:", skill_md, re.M)
    assert re.search(r"^version:\s*\d+(\.\d+)?", skill_md, re.M)
    assert re.search(r"^created:", skill_md, re.M)
    assert re.search(r"^updated:", skill_md, re.M)


def test_required_sections(skill_md):
    for section in [
        "## When to Use",
        "## Architecture",
        "## Setup",
        "## Procedure",
        "## Return-value design",
        "## Other patterns",
        "## Pitfalls",
        "## Verification",
        "## Testing",
    ]:
        assert section in skill_md, f"missing section {section}"


def test_when_to_use_has_boundaries(skill_md):
    """El skill debe decir cuándo NO usarlo."""
    section = skill_md.split("## Architecture")[0]
    assert "Do NOT use" in section, "missing negative-use marker"
    for boundary in ["small", "global context", "Latency", "Request volume"]:
        assert boundary in section, f"missing boundary: {boundary}"


def test_architecture_roles(skill_md):
    arch = skill_md.split("## Setup")[0]
    assert "glm-5.2" in arch, "orchestrator model must be named"
    assert "deepseek-v4-flash" in arch, "executor model must be named"
    assert "work contract" in arch, "the frontier must be defined as the contract"
    assert "Orchestrator" in arch and "Executor" in arch


def test_setup_provider_prefixed_ids(skill_md):
    """Los ids sin proveedor se resolvieron mal en el subproceso (fallo real).
    El setup debe usar ids provider/model."""
    setup = skill_md.split("## Procedure")[0]
    assert "pi -m zai/glm-5.2" in setup, "orchestrator launch must use provider-prefixed id"
    assert "~/.pi/agent/agents/executor.md" in setup
    assert "provider-prefixed" in setup, "must explain why provider-prefixed"


def test_setup_verification_step(skill_md):
    setup = skill_md.split("## Procedure")[0]
    assert "list available subagents" in setup, "setup must include a verification step"


def test_contract_template_has_all_four_keys(skill_md):
    proc = skill_md.split("## Return-value design")[0]
    for key in ["objetivo", "entradas", "restricciones", "criterio_de_exito"]:
        assert key in proc, f"contract template missing key: {key}"


def test_contract_template_requires_absolute_paths(skill_md):
    """Las rutas /tmp rompen en Windows (fallo real: el ejecutor vio dos
    proyectos y destruyó uno). El template debe exigir rutas absolutas."""
    proc = skill_md.split("## Return-value design")[0]
    assert "C:/" in proc, "template must require absolute Windows paths"
    assert "never /tmp" in proc, "template must warn against /tmp"


def test_contract_template_requires_no_delete_clause(skill_md):
    """Sin cláusula no-delete, un ejecutor barato borra archivos hermanos
    (fallo real: 12 tests → 11). Exigimos la frase fuerte (no basta una
    mención suelta)."""
    proc = skill_md.split("## Return-value design")[0]
    assert "no-delete clause" in proc, "template must require an explicit no-delete clause"


def test_procedure_has_decompose_step(skill_md):
    proc = skill_md.split("## Return-value design")[0]
    assert "Decompose into contracts" in proc


def test_procedure_has_warmup_step(skill_md):
    """Primera llamada en solitario antes de la ráfaga paralela (caché)."""
    proc = skill_md.split("## Return-value design")[0]
    assert "Warm up" in proc, "missing cache warm-up step"
    assert "cache" in proc.lower()


def test_procedure_has_deterministic_validation(skill_md):
    proc = skill_md.split("## Return-value design")[0]
    assert "Validate deterministically" in proc, "missing deterministic validation step"


def test_procedure_has_observability(skill_md):
    proc = skill_md.split("## Return-value design")[0]
    assert "Log observability" in proc, "missing observability step"


def test_delegation_never_passes_conversation(skill_md):
    """El principio central del skill: no se pasa la conversación, se pasan
    contratos."""
    proc = " ".join(skill_md.split("## Return-value design")[0].split())
    assert "NEVER pass the orchestrator's conversation" in proc


def test_return_value_three_line_summary(skill_md):
    rv = skill_md.split("## Other patterns")[0]
    assert "## Resumen operativo" in rv
    for line in ["1. Hecho", "2. Estado", "3. Riesgos"]:
        assert line in rv, f"summary missing line: {line}"


def test_pitfalls_cover_observed_failures(skill_md):
    """Cada fallo real vivido debe estar documentado como pitfall."""
    pitfalls = skill_md.split("## Verification")[0]
    for keyword in [
        "conversation",          # pasar el historial al ejecutor
        "3-line summary",        # ejecutor devolviendo diffs completos
        "deterministic validation",  # saltarse la validación
        "Parallel-first bursts", # ráfaga sin warm-up
        "/tmp",                  # trampa de rutas en Windows
        "no-delete",             # ejecutor destructivo
        "provider-prefixed",     # ids de modelo sin proveedor
    ]:
        assert keyword in pitfalls, f"pitfalls missing: {keyword}"


def test_verification_section_concrete(skill_md):
    """La sección de verificación debe poder ejecutarse."""
    verification = skill_md.split("## Testing")[0]
    assert "executor" in verification
    assert "pytest" in verification, "verification must include the test command"
