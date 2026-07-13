from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_portfolio_architecture_contract() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_portfolio_architecture.py"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_architecture_pytest_is_documented_and_run_by_ci() -> None:
    contract = json.loads((ROOT / "docs" / "ARCHITECTURE.yaml").read_text())
    command_text = "\n".join(contract["tests"]["commands"].values())
    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    workflow_text = (ROOT / ".github" / "workflows" / "portfolio-architecture.yml").read_text(
        encoding="utf-8"
    )

    assert "pytest" in command_text
    assert "tests/architecture" in command_text
    assert "pytest" in agents_text
    assert "tests/architecture" in agents_text
    assert "python -m pytest tests/architecture" in workflow_text


def test_optimization_boundaries_are_recorded() -> None:
    contract = json.loads((ROOT / "docs" / "ARCHITECTURE.yaml").read_text())
    forbidden = "\n".join(contract["architecture"]["import_boundaries"]["forbidden"])
    assert "views must not construct PuLP models directly" in forbidden
    assert "optimization service must not import django.shortcuts" in forbidden
    decision = contract["libraries"]["decisions"][0]
    assert decision["capability"] == "linear programming optimization"
    assert "PuLP 3.2.1" in decision["selected"]


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_runtime_import_boundaries_are_enforced() -> None:
    app = ROOT / "revenew_proj" / "optimizador"
    views_imports = _imports(app / "views.py")
    results_imports = _imports(app / "results.py")
    service_imports = _imports(app / "services.py")

    assert "pulp" not in views_imports
    assert "pulp" not in results_imports
    assert not {"django.shortcuts", "django.db", "django.template"} & service_imports
    assert "optimizador.services" not in results_imports
