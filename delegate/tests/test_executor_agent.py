"""Tests estáticos de agents/executor.md — el agente que recibe los contratos.

La suite de mutación altera estas reglas una a una: si una mutación no rompe
ningún test, o la regla no es crítica o falta cobertura."""

import re


def _body(executor_md: str) -> str:
    return executor_md.split("---", 2)[2]


def test_frontmatter_identity(executor_md):
    assert re.search(r"^name:\s*executor", executor_md, re.M)
    assert re.search(r"^description:", executor_md, re.M)
    assert re.search(r"^model:\s*\S+", executor_md, re.M), "executor must pin a model"


def test_model_provider_prefixed(executor_md):
    """Id sin proveedor → 'No API key found for deepseek' en el subproceso
    (fallo real en el primer lanzamiento)."""
    m = re.search(r"^model:\s*(\S+)", executor_md, re.M)
    assert m, "model field required"
    assert "/" in m.group(1), f"model must be provider-prefixed, got: {m.group(1)}"
    assert "deepseek" in m.group(1).lower(), "executor model should be the cheap one"


def test_tools_restricted(executor_md):
    """Ejecutor rápido y no recursivo: sin web, sin subagentes."""
    fm = executor_md.split("---", 2)[1]
    tools_line = next(
        (l for l in fm.splitlines() if l.strip().startswith("tools:")),
        "",
    )
    assert tools_line, "tools field required in frontmatter"
    for tool in ["read", "write", "edit", "bash"]:
        assert tool in tools_line, f"missing tool: {tool}"
    assert "subagent" not in tools_line, "executor must not delegate recursively"
    assert "web_search" not in tools_line, "executor must not browse the web"


def test_contract_fields_documented(executor_md):
    """La sección 'Your contract' debe listar los 4 campos como bullets
    (no basta una mención suelta en otra regla)."""
    contract = executor_md.split("## Your contract", 1)[1].split("## Rules", 1)[0]
    for key in ["objetivo", "entradas", "restricciones", "criterio_de_exito"]:
        assert f"- **{key}**" in contract, f"contract section must document field: {key}"


def test_no_delete_rule(executor_md):
    assert "Never delete" in executor_md, "no-delete rule missing"


def test_path_rule(executor_md):
    """Rutas exactas: la confusión /tmp vs C:\\tmp destruyó archivos (fallo real)."""
    assert "Paths are exact" in executor_md
    assert "C:/" in executor_md, "rule must mandate absolute Windows paths"
    assert "STOP" in executor_md, "rule must say to stop, not guess"


def test_verify_before_reporting(executor_md):
    assert "Verify before reporting" in executor_md


def test_one_retry(executor_md):
    assert "One retry" in executor_md


def test_keep_outputs_small(executor_md):
    assert "Keep outputs small" in executor_md


def test_stay_in_scope(executor_md):
    assert "Stay in scope" in executor_md


def test_three_line_output_format(executor_md):
    """El contrato de retorno: 3 líneas, nada más."""
    assert "## Resumen operativo" in executor_md
    for line in ["1. Hecho", "2. Estado", "3. Riesgos"]:
        assert line in executor_md, f"output format missing line: {line}"
