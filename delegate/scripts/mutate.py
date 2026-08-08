#!/usr/bin/env python3
"""Mutation testing para el skill delegate.

Copia delegate/ a un directorio temporal, aplica UNA mutación a la copia,
ejecuta la suite estática contra la copia mutada y reporta qué mutaciones
fueron eliminadas (killed: algún test falló) y cuáles sobrevivieron (survived:
ningún test la detectó → hueco en la suite o mutación benigna).

Uso:
    python scripts/mutate.py             # suite estática (rápida, gratis)
    python scripts/mutate.py --verbose   # muestra stdout de pytest por mutante
"""

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
TESTS = REPO / "tests"

# (etiqueta, archivo relativo, old, new) — new puede ser "" para eliminar.
# Cada mutación ataca un comportamiento que los tests deben detectar.
MUTATIONS = [
    # --- SKILL.md: template del contrato ---
    ("template pierde cláusula no-delete", "SKILL.md",
     "Every contract must also carry an explicit **no-delete clause**",
     "Every contract must carry an explicit cleanup clause"),
    ("template pierde rutas absolutas", "SKILL.md",
     "entradas: <files/data/resources needed — ABSOLUTE Windows paths (C:/...), never /tmp>",
     "entradas: <files/data/resources needed>"),
    ("template pierde criterio_de_exito", "SKILL.md",
     "criterio_de_exito: <how to verify the task is done correctly>",
     "criterio: <how to verify>"),
    # --- SKILL.md: setup ---
    ("setup usa id sin proveedor", "SKILL.md",
     "pi -m zai/glm-5.2", "pi -m glm-5.2"),
    ("setup pierde verificación del agente", "SKILL.md",
     "list available subagents", "check the agent list"),
    # --- SKILL.md: procedimiento ---
    ("procedimiento pierde warm-up", "SKILL.md",
     "### 3. Warm up the cache (parallel bursts)", "### 3. (removed)"),
    ("procedimiento pierde validación determinista", "SKILL.md",
     "### 5. Validate deterministically", "### 5. (removed)"),
    ("procedimiento pierde observabilidad", "SKILL.md",
     "### 7. Log observability", "### 7. (removed)"),
    ("delegación permite pasar la conversación", "SKILL.md",
     "NEVER pass the orchestrator's", "Try to keep the orchestrator's"),
    # --- SKILL.md: retorno y límites ---
    ("retorno pierde resumen de 3 líneas", "SKILL.md",
     "## Resumen operativo", "## Summary"),
    ("límites de uso borrados", "SKILL.md",
     "Do NOT use when:", "Consider skipping when:"),
    ("arquitectura pierde modelo ejecutor", "SKILL.md",
     "`deepseek-v4-flash` (pinned in agent frontmatter)",
     "`deepseek-v4` (pinned in agent frontmatter)"),
    ("sección Pitfalls renombrada", "SKILL.md",
     "## Pitfalls", "## Risks"),
    # --- executor.md: identidad ---
    ("modelo sin prefijo de proveedor", "agents/executor.md",
     "model: opencode-go/deepseek-v4-flash", "model: deepseek-v4-flash"),
    ("tools gana web_search", "agents/executor.md",
     "tools: read, write, edit, bash, grep, find, ls, ctx_execute",
     "tools: read, write, edit, bash, grep, find, ls, ctx_execute, web_search"),
    ("tools gana subagent", "agents/executor.md",
     "tools: read, write, edit, bash, grep, find, ls, ctx_execute",
     "tools: read, write, edit, bash, grep, find, ls, ctx_execute, subagent"),
    # --- executor.md: reglas ---
    ("regla de no-borrado eliminada", "agents/executor.md",
     "3. **Never delete.**", "3. **(removed).**"),
    ("regla de rutas exactas eliminada", "agents/executor.md",
     "2. **Paths are exact.**", "2. **(removed).**"),
    ("regla verify-before-reporting eliminada", "agents/executor.md",
     "5. **Verify before reporting.**", "5. **(removed).**"),
    ("regla one-retry eliminada", "agents/executor.md",
     "6. **One retry.**", "6. **(removed).**"),
    ("regla keep-outputs-small eliminada", "agents/executor.md",
     "7. **Keep outputs small.**", "7. **(removed).**"),
    ("regla stay-in-scope eliminada", "agents/executor.md",
     "4. **Stay in scope.**", "4. **(removed).**"),
    # --- executor.md: contrato y retorno ---
    ("contrato pierde criterio_de_exito", "agents/executor.md",
     "criterio_de_exito", "criterio_exito"),
    ("formato de retorno de 3 líneas roto", "agents/executor.md",
     "## Resumen operativo", "## Summary"),
]


def run_suite(skill_dir: pathlib.Path, verbose: bool) -> subprocess.CompletedProcess:
    env = dict(__import__("os").environ)
    env["DELEGATE_SKILL_DIR"] = str(skill_dir)
    return subprocess.run(
        [sys.executable, "-m", "pytest", str(TESTS / "test_skill.py"),
         str(TESTS / "test_executor_agent.py"), "-q", "--no-header"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    print(f"=== Mutation testing del skill delegate ({len(MUTATIONS)} mutantes) ===\n")
    killed, survived, not_applied = [], [], []

    for label, rel, old, new in MUTATIONS:
        with tempfile.TemporaryDirectory() as td:
            copy = pathlib.Path(td) / "delegate"
            shutil.copytree(REPO, copy, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
            target = copy / rel
            text = target.read_text(encoding="utf-8")
            if old not in text:
                not_applied.append((label, "OLD NOT FOUND"))
                continue
            target.write_text(text.replace(old, new, 1), encoding="utf-8")

            proc = run_suite(copy, args.verbose)
            if proc.returncode != 0:
                killed.append(label)
                print(f"  [KILLED]   {label}")
            else:
                survived.append(label)
                print(f"  [SURVIVED] {label}")
            if args.verbose and proc.returncode != 0:
                for line in (proc.stdout + proc.stderr).splitlines():
                    if "failed" in line or "FAILED" in line:
                        print(f"      {line.strip()}")

    print(f"\n=== Resultado: {len(killed)} killed, {len(survived)} survived, "
          f"{len(not_applied)} no aplicadas ===")
    score = len(killed) / max(1, len(MUTATIONS) - len(not_applied))
    print(f"Mutation score: {score:.0%}")

    if survived:
        print("\nSURVIVED (huecos de cobertura o mutaciones benignas):")
        for s in survived:
            print(f"  - {s}")
    if not_applied:
        print("\nNO APLICADAS (el texto mutado no existe en el skill):")
        for label, why in not_applied:
            print(f"  - {label}: {why}")

    return 0 if not survived else 1


if __name__ == "__main__":
    sys.exit(main())
