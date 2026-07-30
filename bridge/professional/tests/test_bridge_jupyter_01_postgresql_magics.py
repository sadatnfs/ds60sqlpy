"""Offline structural and content checks for BRIDGE-JUPYTER-01."""

from __future__ import annotations

import re
from pathlib import Path
from typing import cast

import nbformat
from nbformat import NotebookNode

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PROFESSIONAL_ROOT = REPOSITORY_ROOT / "bridge" / "professional"
LEARNER = PROFESSIONAL_ROOT / "notebooks" / "bridge_jupyter_01_postgresql_magics.ipynb"
SOLUTION = PROFESSIONAL_ROOT / "solutions" / "bridge_jupyter_01_postgresql_magics_solution.ipynb"
GUIDE = PROFESSIONAL_ROOT / "companion-guides" / "bridge_jupyter_01_postgresql_magics.md"
SOLUTION_NOTES = (
    PROFESSIONAL_ROOT / "solutions" / "bridge_jupyter_01_postgresql_magics_solutions.md"
)

ORDERED_NOTEBOOK_HEADINGS = (
    "## Goal",
    "## Setup",
    "## Steps",
    "## Checks",
    "## Next Steps",
)
ORDERED_GUIDE_HEADINGS = (
    "## Level and prerequisites",
    "## Learning objectives",
    "## Vocabulary and concepts",
    "## Worked example / walkthrough",
    "## Exercises",
    "## Self-check",
    "## Common pitfalls",
    "## Next step",
)


def read_notebook(path: Path) -> NotebookNode:
    notebook = nbformat.read(path, as_version=4)  # type: ignore[no-untyped-call]
    nbformat.validate(notebook)
    return cast(NotebookNode, notebook)


def notebook_source(notebook: NotebookNode) -> str:
    return "\n".join(str(cell.source) for cell in notebook.cells)


def code_sources(notebook: NotebookNode) -> list[str]:
    return [str(cell.source) for cell in notebook.cells if cell.cell_type == "code"]


def test_artifacts_use_exact_stable_paths() -> None:
    assert LEARNER.is_file()
    assert SOLUTION.is_file()
    assert GUIDE.is_file()
    assert SOLUTION_NOTES.is_file()
    assert LEARNER.name == "bridge_jupyter_01_postgresql_magics.ipynb"
    assert SOLUTION.name == "bridge_jupyter_01_postgresql_magics_solution.ipynb"
    assert SOLUTION_NOTES.name == "bridge_jupyter_01_postgresql_magics_solutions.md"


def test_notebooks_are_clean_nbformat_45_with_repository_kernel() -> None:
    for path, artifact in ((LEARNER, "learner"), (SOLUTION, "solution")):
        notebook = read_notebook(path)
        assert (notebook.nbformat, notebook.nbformat_minor) == (4, 5)
        assert notebook.metadata.kernelspec.name == "ds60sqlpy"
        assert notebook.metadata.language_info.name == "python"
        assert notebook.metadata.course == {
            "artifact": artifact,
            "day": "professional",
            "lesson_id": "bridge-jupyter-01",
            "tags": [
                "bridge",
                "jupyter",
                "jupysql",
                "live-postgres",
                "manual",
                "professional",
            ],
            "track": "bridge",
        }

        cell_ids = [str(cell.id) for cell in notebook.cells]
        assert len(cell_ids) == len(set(cell_ids))
        assert all(cell_ids)
        for cell in notebook.cells:
            if cell.cell_type == "code":
                assert cell.execution_count is None
                assert cell.outputs == []


def test_tutorial_sections_are_in_required_order() -> None:
    for path in (LEARNER, SOLUTION):
        source = notebook_source(read_notebook(path))
        positions = [source.index(heading) for heading in ORDERED_NOTEBOOK_HEADINGS]
        assert positions == sorted(positions)

    guide = GUIDE.read_text(encoding="utf-8")
    positions = [guide.index(heading) for heading in ORDERED_GUIDE_HEADINGS]
    assert positions == sorted(positions)


def test_magic_and_live_cells_have_offline_validation_tags() -> None:
    for path in (LEARNER, SOLUTION):
        notebook = read_notebook(path)
        for cell in notebook.cells:
            if cell.cell_type != "code":
                continue
            source = str(cell.source)
            tags = set(cell.metadata.get("tags", []))
            lines = source.splitlines()
            has_magic_syntax = any(
                line.lstrip().startswith(("%", "!")) or " = %sql " in line for line in lines
            )
            if has_magic_syntax:
                assert "skip-static-validation" in tags, cell.id

            requires_server = (
                any(
                    line.lstrip().startswith(("%sql", "%%sql")) or " = %sql " in line
                    for line in lines
                )
                or "engine.begin()" in source
            )
            if requires_server:
                assert "live-postgres" in tags, cell.id


def test_required_jupysql_and_safety_content_is_present() -> None:
    for path in (LEARNER, SOLUTION):
        source = notebook_source(read_notebook(path))
        required = (
            "%load_ext sql",
            "%sql engine --alias ds60-course",
            "%sql --connections",
            "%sql --close ds60-course",
            "%%sql",
            "DS60_DATABASE_URL",
            "make_url",
            "postgresql+psycopg",
            "SqlMagic.displaycon = False",
            "SqlMagic.autolimit",
            "SqlMagic.displaylimit",
            "SqlMagic.autopandas",
            "SqlMagic.named_parameters",
            ".DataFrame()",
            ":order_status",
            ":minimum_total",
            "{{value}}",
            "Identifier",
            "autocommit",
            "Psycopg",
            "advanced_sql_training",
            "engine.dispose()",
        )
        for needle in required:
            assert needle in source, f"{path.name} lacks {needle!r}"


def test_notebooks_have_no_install_shell_secret_or_destructive_cells() -> None:
    credential_url = re.compile(
        r"postgres(?:ql)?(?:\+psycopg)?://[^/\s:]+:[^@\s]+@",
        re.IGNORECASE,
    )
    for path in (LEARNER, SOLUTION):
        notebook = read_notebook(path)
        source = notebook_source(notebook)
        lowered = source.casefold()
        assert "%pip" not in lowered
        assert "!pip" not in lowered
        assert "%%bash" not in lowered
        assert "%%powershell" not in lowered
        assert "https://" not in lowered
        assert "http://" not in lowered
        assert credential_url.search(source) is None
        assert "/users/" not in lowered
        assert "\\users\\" not in lowered

        sql_code = "\n".join(code_sources(notebook)).casefold()
        for destructive in (
            "drop schema",
            "drop table",
            "truncate ",
            "insert into",
            "update training.",
            "delete from",
            "create table",
            "alter table",
            "\\copy",
        ):
            assert destructive not in sql_code


def test_learner_has_answer_free_check_and_solution_completes_it() -> None:
    learner_source = notebook_source(read_notebook(LEARNER))
    solution_source = notebook_source(read_notebook(SOLUTION))

    assert "Replace this diagnostic row" in learner_source
    assert "LEFT JOIN training.orders" not in learner_source
    assert "customer_totals = %sql" not in learner_source

    assert "Replace this diagnostic row" not in solution_source
    assert "customer_totals = %sql" in solution_source
    assert "LEFT JOIN training.orders" in solution_source
    assert ":exercise_country" in solution_source
    assert ":exercise_minimum_total" in solution_source


def test_cross_platform_guide_and_reasoning_contract() -> None:
    guide = GUIDE.read_text(encoding="utf-8")
    assert "# Windows PowerShell" in guide
    assert "# macOS/Linux" in guide
    assert r".\.venv\Scripts\python.exe -m jupyter lab" in guide
    assert ".venv/bin/python -m jupyter lab" in guide
    assert "$env:DS60_DATABASE_URL = Read-Host" in guide
    assert "read -r -s" in guide
    assert "code ." in guide
    assert "%pip" in guide
    assert "Do not install packages" in guide

    notes = SOLUTION_NOTES.read_text(encoding="utf-8")
    assert "## Tradeoffs" in notes
    assert "parameter" in notes.casefold()
    assert "transaction" in notes.casefold()
    assert "Psycopg" in notes
