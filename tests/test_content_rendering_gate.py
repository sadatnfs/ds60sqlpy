from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.catalog import Catalog
from scripts.check_content_rendering import inspect_catalog, main


@pytest.fixture
def rendered_catalog(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Catalog:
    monkeypatch.setattr("ds60sqlpy.lesson_reader.COURSE_GUIDE_REFERENCE_PATHS", ())
    lesson = replace(
        Catalog.load().get("python-01"),
        prerequisites=(),
        guide_path="course/guide.md",
        lesson_path="course/learner.ipynb",
        solution_paths=("course/solution.md",),
    )
    catalog = Catalog(
        tmp_path, [lesson], tracks={"python": {"title": "Python", "plan": "README.md"}}
    )
    (tmp_path / "course").mkdir()
    (tmp_path / "README.md").write_text("# Fixture classroom\n")
    (tmp_path / "course/guide.md").write_text(r"A correct formula: \(\sqrt{x^2}\)." + "\n")
    (tmp_path / "course/solution.md").write_text("# Explanation\n")
    (tmp_path / "course/learner.ipynb").write_text(
        json.dumps(
            {
                "metadata": {"language_info": {"name": "python"}},
                "cells": [
                    {"cell_type": "markdown", "source": r"Use \(\mu\)."},
                    {"cell_type": "code", "source": r'print("\(\unknown{x}\)")', "outputs": []},
                ],
            }
        )
    )
    return catalog


def test_gate_uses_actual_renderer_and_keeps_code_math_literal(rendered_catalog: Catalog) -> None:
    guide = rendered_catalog.repo_root / "course/guide.md"
    guide.write_text(r"""A correct formula: \(\frac{1}{2}\).

Inline source `\(\unknown{x}\)`.

```python
print("\(\unknown{x}\)")
```not-a-closer
literal \(\unknown{x}\)
````

```latex
\unknown{x}
```

~~~text
\(\unknown{x}\)
""")
    before = {p: p.read_bytes() for p in rendered_catalog.repo_root.rglob("*") if p.is_file()}
    report = inspect_catalog(rendered_catalog)
    assert report["files_checked"] == 4
    assert report["math_expressions"] == 2
    assert report["code_blocks"] == 4
    assert report["failures"] == []
    assert {p: p.read_bytes() for p in before} == before


def test_gate_rejects_invalid_prose_math_in_recursive_references(rendered_catalog: Catalog) -> None:
    guide = rendered_catalog.repo_root / "course/guide.md"
    guide.write_text(guide.read_text() + "\n[Reference](details.md)\n")
    (rendered_catalog.repo_root / "course/details.md").write_text(r"Unsupported \(\unknown{x}\).")
    report = inspect_catalog(rendered_catalog)
    assert report["files_checked"] == 5 and report["failure_count"] == 1
    assert report["failures"][0]["path"] == "course/details.md"
    assert report["failures"][0]["kind"] == "math_fallback"
    assert report["failures"][0]["source"] == r"\(\unknown{x}\)"


def test_explicit_math_fence_is_checked_and_unregistered_scratch_is_not(
    rendered_catalog: Catalog,
) -> None:
    (rendered_catalog.repo_root / "scratch.md").write_text(r"\(\unknown{scratch}\)")
    (rendered_catalog.repo_root / "course/guide.md").write_text("```math\n\\unknown{x}\n```\n")
    report = inspect_catalog(rendered_catalog)
    assert report["failure_count"] == 1
    assert report["failures"][0]["path"] == "course/guide.md"


def test_gate_reports_notebook_prose_error_without_executing_cells(
    rendered_catalog: Catalog,
) -> None:
    notebook = rendered_catalog.repo_root / "course/learner.ipynb"
    payload = json.loads(notebook.read_text())
    payload["cells"][0]["source"] = r"\(x^^2\)"
    payload["cells"][1]["source"] = "raise AssertionError('never execute')"
    notebook.write_text(json.dumps(payload))
    report = inspect_catalog(rendered_catalog)
    assert report["failure_count"] == 1
    assert report["failures"][0]["path"] == "course/learner.ipynb"
    assert report["failures"][0]["kind"] == "math_fallback"


def test_gate_reports_structurally_broken_notebook(rendered_catalog: Catalog) -> None:
    (rendered_catalog.repo_root / "course/learner.ipynb").write_text("{}")
    report = inspect_catalog(rendered_catalog)
    assert report["failure_count"] == 1
    assert report["failures"][0]["kind"] == "render_error"


def test_cli_exit_status_counts_and_explicit_report(
    rendered_catalog: Catalog,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "scripts.check_content_rendering.Catalog.load", lambda _root: rendered_catalog
    )
    args = ["--root", str(rendered_catalog.repo_root)]
    before = {p for p in rendered_catalog.repo_root.rglob("*") if p.is_file()}
    assert main(args) == 0
    assert {p for p in rendered_catalog.repo_root.rglob("*") if p.is_file()} == before
    (rendered_catalog.repo_root / "course/guide.md").write_text(r"Broken \(\unknown{x}\).")
    report_path = tmp_path / "explicit-output" / "report.json"
    assert main([*args, "--report", str(report_path)]) == 1
    report: dict[str, Any] = json.loads(report_path.read_text())
    assert report["failure_count"] == 1 and report["files_checked"] == 4
    assert "course/guide.md: math_fallback" in capsys.readouterr().out


def test_cli_discovery_failure_returns_nonzero_without_creating_repository(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    assert main(["--root", str(missing)]) == 1
    assert not missing.exists()


def test_cli_rejects_nested_source_instead_of_validating_its_parent(
    rendered_catalog: Catalog, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Catalog.load deliberately discovers a parent for interactive commands.
    # A publication gate must validate the exact root requested by its caller.
    monkeypatch.setattr(
        "scripts.check_content_rendering.Catalog.load", lambda _root: rendered_catalog
    )
    requested = rendered_catalog.repo_root / "empty-source"
    requested.mkdir()
    before = {p: p.read_bytes() for p in rendered_catalog.repo_root.rglob("*") if p.is_file()}
    assert main(["--root", str(requested)]) == 1
    assert "0 sources" in capsys.readouterr().out
    assert {p: p.read_bytes() for p in before} == before
