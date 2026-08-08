"""Integración: ejecuta el agente executor REAL (spawn de pi) sobre una tarea
fixture y verifica que cumple el contrato end-to-end.

Gated por RUN_INTEGRATION=1 porque cuesta dinero real (llamada a la API).
Replica la invocación del extension subagent:

  pi --mode json -p --no-session --model <frontmatter model>
     --tools <frontmatter tools> --append-system-prompt <agent body>
     Task: <task>

Devuelve líneas JSON en stdout (eventos message_end/tool_result_end) con
usage por mensaje — de ahí se extrae el coste real.
"""

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION") != "1",
    reason="set RUN_INTEGRATION=1 to run real-API tests",
)

FIXTURE_MODULE = '''"""Módulo fixture del test de integración."""


def double(x):
    return x * 2


def halve(x):
    return x / 2


def is_even(x):
    return x % 2 == 0
'''

FIXTURE_UNITTEST = '''import unittest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from calc import double, halve, is_even


class TestDouble(unittest.TestCase):
    def test_double_positive(self):
        self.assertEqual(double(4), 8)

    def test_double_zero(self):
        self.assertEqual(double(0), 0)


class TestHalve(unittest.TestCase):
    def test_halve_exact(self):
        self.assertEqual(halve(10), 5.0)


class TestIsEven(unittest.TestCase):
    def test_is_even_true(self):
        self.assertTrue(is_even(8))

    def test_is_even_false(self):
        self.assertFalse(is_even(7))


if __name__ == "__main__":
    unittest.main()
'''

CONTRACT = """Contrato de trabajo:

objetivo: Migrar C:/<PROJECT>/tests/test_calc_unittest.py de unittest a pytest, manteniendo los mismos tests.

entradas:
- C:/<PROJECT>/tests/test_calc_unittest.py (archivo a migrar)
- C:/<PROJECT>/tests/conftest.py (ya existe; provee la fixture `calc` y resuelve el import)
- C:/<PROJECT>/calc.py (módulo bajo test, solo lectura)

restricciones:
- Mantener los nombres exactos de los tests: test_double_positive, test_double_zero, test_halve_exact, test_is_even_true, test_is_even_false
- Usar la fixture `calc` de conftest.py en lugar de imports manuales y sys.path
- Eliminar imports de unittest, las clases TestDouble/TestHalve/TestIsEven y el bloque if __name__ == "__main__"
- Los tests quedan como funciones pytest: def test_double_positive(calc): assert calc.double(4) == 8 (usar pytest.raises si hace falta)
- NO borrar ni modificar NINGÚN otro archivo. NO recrear archivos. Solo este archivo.

criterio_de_exito:
- `cd C:/<PROJECT> && python -m pytest tests/test_calc_unittest.py -q` pasa con 5 passed
- `grep -c unittest tests/test_calc_unittest.py` devuelve 0
"""

CONFTEST = """import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import calc as calc_module


@pytest.fixture
def calc():
    return calc_module
"""


def _pi_invocation() -> list[str]:
    """Node + cli.js directo: evita cmd.exe, que corrompe argumentos con
    `&&` y saltos de línea al invocar pi.CMD (fallo real en este test)."""
    if os.environ.get("PI_BIN"):
        return [os.environ["PI_BIN"]]
    node = shutil.which("node") or "node"
    pi_cmd = shutil.which("pi")
    if pi_cmd:
        cli = (pathlib.Path(pi_cmd).parent / "node_modules" / "@earendil-works"
               / "pi-coding-agent" / "dist" / "cli.js")
        if cli.exists():
            return [node, str(cli)]
    return ["pi"]


def _run_pi(args, cwd):
    return subprocess.run(
        [*_pi_invocation(), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )


def _parse_events(stdout: str):
    """message_end con role assistant → texto final + usage."""
    texts = []
    usage = {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "cost": 0.0}
    model = None
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "message_end" and event.get("message"):
            msg = event["message"]
            if msg.get("role") == "assistant":
                u = msg.get("usage") or {}
                usage["input"] += u.get("input") or 0
                usage["output"] += u.get("output") or 0
                usage["cacheRead"] += u.get("cacheRead") or 0
                usage["cacheWrite"] += u.get("cacheWrite") or 0
                usage["cost"] += (u.get("cost") or {}).get("total") or 0
                model = msg.get("model") or model
                content = msg.get("content") or []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        texts.append(part["text"])
    return "\n".join(texts), usage, model


def test_executor_completes_a_contract(tmp_path):
    # 1. Proyecto fixture (misma forma que el demo real)
    proj = tmp_path / "project"
    (proj / "tests").mkdir(parents=True)
    (proj / "calc.py").write_text(FIXTURE_MODULE, encoding="utf-8")
    (proj / "tests" / "conftest.py").write_text(CONFTEST, encoding="utf-8")
    (proj / "tests" / "test_calc_unittest.py").write_text(FIXTURE_UNITTEST, encoding="utf-8")

    # Baseline unittest
    base = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
        cwd=str(proj), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert base.returncode == 0 and "OK" in base.stdout + base.stderr, \
        f"baseline failed: {base.stdout + base.stderr}"

    # 2. Lanzar el agente executor real (misma invocación que el extension)
    root = pathlib.Path(__file__).resolve().parent.parent
    agent_md = (root / "agents" / "executor.md").read_text(encoding="utf-8")
    fm = agent_md.split("---", 2)[1]
    model = re.search(r"^model:\s*(\S+)", fm, re.M).group(1)
    tools = re.search(r"^tools:\s*(.+)$", fm, re.M).group(1).strip()
    body = agent_md.split("---", 2)[2]

    proj_win = str(proj).replace("\\", "/")  # forward slashes: Git Bash corrompe backslashes
    task = CONTRACT.replace("<PROJECT>", proj_win)

    with tempfile.TemporaryDirectory() as td:
        prompt_file = pathlib.Path(td) / "executor-prompt.md"
        prompt_file.write_text(body, encoding="utf-8")
        proc = _run_pi(
            [
                "--mode", "json", "-p", "--no-session",
                "--model", model,
                "--tools", tools,
                "--append-system-prompt", str(prompt_file),
                f"Task: {task}",
            ],
            cwd=str(proj),
        )

    assert proc.returncode == 0, f"pi failed: rc={proc.returncode}\nstdout={proc.stdout[-2000:]}\nstderr={proc.stderr[-2000:]}"

    text, usage, used_model = _parse_events(proc.stdout)
    assert "## Resumen operativo" in text, f"agent must return the 3-line summary, got:\n{text[-1500:]}"
    assert "1. Hecho" in text and "2. Estado" in text and "3. Riesgos" in text

    # 3. Validación determinista (la hace el test, no el agente)
    migrated = (proj / "tests" / "test_calc_unittest.py").read_text(encoding="utf-8")
    assert "unittest" not in migrated, (
        f"unittest imports must be gone. Agent report:\n{text[-1500:]}"
    )
    for name in ["test_double_positive", "test_double_zero", "test_halve_exact",
                 "test_is_even_true", "test_is_even_false"]:
        assert f"def {name}" in migrated, f"test name lost: {name}"

    run = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_calc_unittest.py", "-q"],
        cwd=str(proj), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert run.returncode == 0, f"pytest failed:\n{run.stdout}\n{run.stderr}"

    # 4. Observabilidad: coste real del paso
    print(f"\n[integration] model={used_model} cost=${usage['cost']:.5f} "
          f"input={usage['input']} output={usage['output']} "
          f"cacheRead={usage['cacheRead']} cacheWrite={usage['cacheWrite']}")
