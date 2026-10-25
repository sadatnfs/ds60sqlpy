"""Day 1 setup migration must not regenerate retired host installers."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import nbformat
import pytest

from scripts.normalize_notebooks import (
    DAY1_ENVIRONMENT_GUIDE,
    DAY1_PACKAGES_GUIDE,
    DAY1_REPL_GUIDE,
    DAY1_SCRIPT_GUIDE,
    DAY1_SETUP_REPAIRS,
    SOURCE_REPLACEMENTS,
    _apply_source_repairs,
)

DAY1 = Path("python/ds-60day/notebooks/day01_setup_and_repl.ipynb")
CURRENT_GUIDANCE = (
    DAY1_ENVIRONMENT_GUIDE,
    DAY1_REPL_GUIDE,
    DAY1_SCRIPT_GUIDE,
    DAY1_PACKAGES_GUIDE,
)


@pytest.mark.parametrize("stage", ["historical", "previously_normalized"])
def test_day1_setup_migrates_both_old_forms_without_touching_executable_cells(stage: str) -> None:
    historical = [
        old for old, new in SOURCE_REPLACEMENTS[DAY1.as_posix()] if new in CURRENT_GUIDANCE
    ]
    legacy = [old for old, _ in DAY1_SETUP_REPAIRS]
    inputs = historical if stage == "historical" else legacy
    assert len(inputs) == len(CURRENT_GUIDANCE) == 4
    # nbformat v4 factories are untyped; keep exceptions at this library boundary.
    code = nbformat.v4.new_code_cell(  # type: ignore[no-untyped-call]
        source='legacy_text = r"""' + legacy[0] + '"""\nprint("preserve this attempt")\n',
        execution_count=7,
        outputs=[
            nbformat.v4.new_output(  # type: ignore[no-untyped-call]
                "stream", name="stdout", text="preserve this output\n"
            )
        ],
        metadata={"tags": ["learner-attempt"]},
    )
    exercise = nbformat.v4.new_markdown_cell(  # type: ignore[no-untyped-call]
        "## Exercise 1\nKeep this exercise identity."
    )
    notebook = nbformat.v4.new_notebook(  # type: ignore[no-untyped-call]
        cells=[
            *(nbformat.v4.new_markdown_cell(source) for source in inputs),  # type: ignore[no-untyped-call]
            code,
            exercise,
        ]
    )
    protected = deepcopy(notebook.cells[-2:])

    assert _apply_source_repairs(notebook, DAY1) == 4
    assert [cell.source for cell in notebook.cells[:4]] == list(CURRENT_GUIDANCE)
    assert notebook.cells[-2:] == protected
    for cell in notebook.cells[:4]:
        assert "setup.ps1" not in cell.source
        assert "bootstrap_windows" not in cell.source
        assert "PowerShell" not in cell.source
        assert "Windows WSL 2" in cell.source
    assert "./classroom" in notebook.cells[0].source
    assert "scripts/setup.sh --dependency-mode locked" in notebook.cells[0].source
    assert "doctor --no-database" in notebook.cells[0].source
    assert ".venv/bin/python" in notebook.cells[0].source
    assert "separate" in notebook.cells[0].source

    once = deepcopy(notebook)
    assert _apply_source_repairs(notebook, DAY1) == 0
    assert notebook == once


def test_day1_legacy_setup_migration_does_not_rewrite_another_lesson() -> None:
    notebook = nbformat.v4.new_notebook(  # type: ignore[no-untyped-call]
        cells=[
            nbformat.v4.new_markdown_cell(old)  # type: ignore[no-untyped-call]
            for old, _ in DAY1_SETUP_REPAIRS
        ]
    )
    before = deepcopy(notebook)

    assert (
        _apply_source_repairs(notebook, Path("python/ds-60day/notebooks/day02_basics_types.ipynb"))
        == 0
    )
    assert notebook == before
