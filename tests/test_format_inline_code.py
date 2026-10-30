"""Fenced-code formatting keeps prose, data and generator boundaries exact."""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts import format_inline_code as inline
from scripts import format_repo


def python_adapter(source: bytes, language: str, suffix: str, root: Path) -> bytes:
    assert language == "python" and suffix == ".py"
    return (ast.unparse(ast.parse(source)) + "\n").encode()


def formatter(root: Path) -> inline.Formatter:
    return inline.Formatter(root, python_adapter)


def document(text: str, root: Path, **kwargs: Any) -> tuple[str, list[dict[str, Any]]]:
    return inline.format_document(
        text, formatter(root), {"python"}, path="docs/example.md", **kwargs
    )


def test_fence_lengths_indentation_and_embedded_short_markers_are_structural() -> None:
    text = (
        "Before\n  ````python title=example\n  x=1\n  ```\n  `````\nAfter\n~~~sql\nselect 1;\n~~~\n"
    )
    blocks, others = inline.fences(text)
    assert len(blocks) == 2 and not others
    assert blocks[0].tag == "python" and blocks[0].closed
    assert blocks[0].body == "  x=1\n  ```\n"
    assert blocks[1].tag == "sql"
    assert text[blocks[0].body_end : blocks[0].end] == "  `````\n"


def test_formats_only_body_preserves_prose_tex_code_spans_and_literal_values(
    tmp_path: Path,
) -> None:
    before = (
        "Exact `a  b` and \\(x^2\\).\n\n```python title=x\n"
        "data={'literal':'a  b','unicode':'é'}\n```\n\nExpected: a  b.\n"
    )
    after, records = document(before, tmp_path)
    assert after.startswith("Exact `a  b` and \\(x^2\\).\n\n```python title=x\n")
    assert after.endswith("```\n\nExpected: a  b.\n")
    assert "'a  b'" in after and "'é'" in after
    assert records[0]["status"] == "formatted"
    again, rows = document(after, tmp_path)
    assert again == after and rows[0]["status"] == "clean"


def test_crlf_and_commonmark_indent_are_preserved(tmp_path: Path) -> None:
    before = "intro\r\n  ~~~python\r\n  x=1\r\n  ~~~\r\nend\r\n"
    after, records = document(before, tmp_path)
    assert after == "intro\r\n  ~~~python\r\n  x = 1\r\n  ~~~\r\nend\r\n"
    assert records[0]["status"] == "formatted"


@pytest.mark.parametrize(
    "text,reason",
    [
        ("```python\nx=1\n", "unclosed-fence"),
        ("```python\n>>> x=1\n```\n", "interactive-prompt-transcript"),
        ("```text\nexpected   output\n```\n", "untyped-or-output-transcript"),
        ("```powershell\nWrite-Host 'literal'\n```\n", "unsupported-language"),
        ("```python\nif x:\n```\n", "fragment-or-invalid-syntax"),
        ("```python\nx=1\r\ny=2\n```\n", "mixed-newline-styles"),
    ],
)
def test_explicit_transcript_fragment_and_container_inventory(
    tmp_path: Path, text: str, reason: str
) -> None:
    result, rows = document(text, tmp_path)
    assert result == text and rows[0]["status"] == "preserved"
    assert rows[0]["reason"].startswith(reason)


def test_nested_markdown_container_is_reported_without_guessing_indentation(tmp_path: Path) -> None:
    text = "> ```python\n> x=1\n> ```\n"
    result, rows = document(text, tmp_path)
    assert result == text and rows
    assert all(row["reason"] == "nested-or-indented-fence" for row in rows)


@pytest.mark.parametrize("replacement", [b"x = 2\n", b"x = '1'\n", b"x =\n"])
def test_changed_value_type_or_syntax_rejects_the_entire_document(
    tmp_path: Path, replacement: bytes
) -> None:
    adapter = inline.Formatter(tmp_path, lambda *args: replacement)
    text = "```python\nx=1\n```\n"
    result, rows = inline.format_document(text, adapter, {"python"}, path="guide.md")
    assert result == text and rows[0]["status"] == "error"
    assert "Formatter" in rows[0]["reason"]


def test_comment_expected_output_is_protected_from_formatter_deletion(tmp_path: Path) -> None:
    text = "```python\nx=1\n# Expected: one  value\n```\n"
    result, rows = document(text, tmp_path)
    assert result == text and rows[0]["status"] == "error"


def test_non_idempotent_formatter_is_rejected(tmp_path: Path) -> None:
    counter = {"calls": 0}

    def alternating(*args: Any) -> bytes:
        counter["calls"] += 1
        return b"x = 1\n" if counter["calls"] == 1 else b"x=1\n"

    text = "```python\nx=1\n```\n"
    result, rows = inline.format_document(
        text, inline.Formatter(tmp_path, alternating), {"python"}, path="guide.md"
    )
    assert result == text and rows[0]["status"] == "error"
    assert "idempotent" in rows[0]["reason"]


def test_generated_markdown_drift_requires_owner_regeneration(tmp_path: Path) -> None:
    text = "```python\nx=1\n```\n"
    result, rows = document(text, tmp_path, generated=True)
    assert result == text and rows[0]["status"] == "needs-regeneration"


def test_protected_evidence_is_not_sent_to_any_formatter(tmp_path: Path) -> None:
    def refuse(*args: Any) -> bytes:
        pytest.fail("Protected source reached adapter")

    text = "```python\nx=1\n```\n"
    result, rows = inline.format_document(
        text,
        inline.Formatter(tmp_path, refuse),
        {"python"},
        path="receipt.md",
        protected="Historical evidence",
    )
    assert result == text and rows[0]["reason"].startswith("protected-source")


def test_authoring_triple_string_changes_only_approved_fence_value(tmp_path: Path) -> None:
    source = 'setting = "untouched"\nguide = r"""Prose \\(x^2\\).\n```python\nx=1\n```\n"""\n'
    updated, rows = inline.format_authoring_python(
        source, formatter(tmp_path), {"python"}, path="courses/demo/authoring/units.py"
    )
    assert 'setting = "untouched"' in updated
    assert 'guide = r"""' in updated and "\\(x^2\\)" in updated
    before = ast.parse(source)
    after = ast.parse(updated)
    left, right, guide = before.body[0], after.body[0], after.body[1]
    assert isinstance(left, ast.Assign) and isinstance(right, ast.Assign)
    assert isinstance(guide, ast.Assign)
    assert isinstance(left.value, ast.Constant) and isinstance(right.value, ast.Constant)
    assert isinstance(guide.value, ast.Constant)
    assert left.value.value == right.value.value
    assert "x = 1\n" in str(guide.value.value)
    assert rows[0]["container"] == "python-authoring-string"


def test_dynamic_authoring_template_is_reported_and_never_executed(tmp_path: Path) -> None:
    source = 'guide = f"""```python\n{dangerous_call()}\n```\n"""\n'
    updated, rows = inline.format_authoring_python(
        source, formatter(tmp_path), {"python"}, path="courses/demo/authoring/build.py"
    )
    assert updated == source and rows[0]["reason"] == "dynamic-authoring-template"


def test_authoring_json_changes_prose_string_body_without_reserializing_other_data(
    tmp_path: Path,
) -> None:
    original = '{ "title": "a  b", "guide": "```python\\nx=1\\n```\\n", "expected": [1, 2] }\n'
    updated, rows = inline.format_authoring_json(
        original, formatter(tmp_path), {"python"}, path="courses/demo/authoring/unit.json"
    )
    assert updated.startswith('{ "title": "a  b", "guide": ')
    assert updated.endswith(', "expected": [1, 2] }\n')
    assert json.loads(updated)["guide"] == "```python\nx = 1\n```\n"
    assert rows[0]["container"] == "json-authoring-string"


def test_all_public_language_adapters_have_an_explicit_fence_alias() -> None:
    assert {family for family, suffix in inline.ALIASES.values()} == set(format_repo.LANGUAGES)


def test_read_only_inventory_and_write_preserve_generated_outputs_and_source_mode(
    tmp_path: Path,
) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "generated").mkdir()
    (tmp_path / "scripts/format-policy.json").write_text(
        json.dumps(
            {
                "exclude": [
                    {"pattern": "*.md", "reason": "Prose is separate"},
                    {
                        "pattern": "generated/*",
                        "reason": "Generated by the subject authoring pipeline",
                    },
                ],
                "preserve": [],
            }
        )
    )
    text = "```python\nx=1\n```\n"
    source = tmp_path / "docs/source.md"
    source.write_text(text)
    source.chmod(0o640)
    generated = tmp_path / "generated/guide.md"
    generated.write_text(text)
    report = inline.inspect_sources(tmp_path, {"python"}, formatter=formatter(tmp_path))
    assert not report["passed"] and source.read_text() == text and generated.read_text() == text
    report = inline.inspect_sources(
        tmp_path, {"python"}, check=False, formatter=formatter(tmp_path)
    )
    assert (
        source.read_text() == "```python\nx = 1\n```\n" and source.stat().st_mode & 0o777 == 0o640
    )
    assert generated.read_text() == text and not report["passed"]
    row = next(row for row in report["records"] if row["status"] == "needs-regeneration")
    assert row["owner_candidates"] == [{"path": "docs/source.md", "line": 1}]


def test_list_only_does_not_require_tools_or_change_source(tmp_path: Path) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/format-policy.json").write_text('{"exclude":[],"preserve":[]}')
    path = tmp_path / "guide.md"
    path.write_text("```scala\nval x=1\n```\n")

    def missing(*args: Any) -> bytes:
        raise AssertionError("Listing used a formatter")

    report = inline.inspect_sources(
        tmp_path, {"scala"}, list_only=True, formatter=inline.Formatter(tmp_path, missing)
    )
    assert report["passed"] and report["status_counts"] == {"candidate": 1}


def test_invocation_refuses_missing_tools_without_silent_language_skip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def absent(*args: Any, **kwargs: Any) -> Any:
        raise FileNotFoundError("missing")

    monkeypatch.setattr(subprocess, "run", absent)
    with pytest.raises(inline.FormatFailure, match="Missing prepared adapter"):
        inline.invoke(["absent"], b"x=1", tmp_path)


def test_xml_only_normalizes_element_indentation_not_mixed_or_preserved_values() -> None:
    compact = b'<root><a n="1">literal  value</a></root>'
    indented = b'<root>\n  <a n="1">literal  value</a>\n</root>'
    assert inline.xml_value(compact) == inline.xml_value(indented)
    assert inline.xml_value(b"<root>start <a>value</a> end</root>") != inline.xml_value(
        b"<root>start<a>value</a>end</root>"
    )
    assert inline.xml_value(b'<root xml:space="preserve"><a>x</a></root>') != inline.xml_value(
        b'<root xml:space="preserve">\n<a>x</a>\n</root>'
    )
    assert inline.xml_value(b"<a>  value  </a>") != inline.xml_value(b"<a>value</a>")


def test_notebook_markdown_changes_leave_code_outputs_and_metadata_values_exact(
    tmp_path: Path,
) -> None:
    notebook: dict[str, Any] = {
        "nbformat": 4,
        "metadata": {"literal": "  exact  "},
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["Prose \\(x\\).\n", "```python\n", "x=1\n", "```\n"],
            },
            {
                "cell_type": "code",
                "source": ["print('a  b')\n"],
                "outputs": [{"text": "a  b\n"}],
                "execution_count": 3,
            },
        ],
    }
    result, rows = inline.format_notebook(
        json.dumps(notebook), formatter(tmp_path), {"python"}, path="example.ipynb"
    )
    after = json.loads(result)
    assert after["metadata"] == notebook["metadata"]
    assert after["cells"][1] == notebook["cells"][1]
    assert after["cells"][0]["source"] == ["Prose \\(x\\).\n", "```python\n", "x = 1\n", "```\n"]
    assert rows[0]["cell"] == 0 and rows[0]["container"] == "notebook-markdown"


def test_read_only_budget_returns_incomplete_evidence_without_a_source_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/format-policy.json").write_text('{"exclude":[],"preserve":[]}')
    path = tmp_path / "guide.md"
    original = "```python\nx=1\n```\n"
    path.write_text(original)
    bounded = formatter(tmp_path)
    bounded.deadline = 0
    report = inline.inspect_sources(tmp_path, {"python"}, formatter=bounded)
    assert report["complete"] is False and report["passed"] is False
    assert report["status_counts"] == {"error": 1}
    assert report["source_inventory"] == []
    assert report["records"][0]["reason"].startswith("source-inventory-unavailable")
    assert path.read_text() == original
    with pytest.raises(ValueError, match="read-only"):
        inline.inspect_sources(tmp_path, {"python"}, check=False, max_seconds=1)


def test_duplicate_notebook_metadata_keys_are_not_lost_during_formatting(tmp_path: Path) -> None:
    source = '{"cells":[],"metadata":{"key":1,"key":2}}'
    with pytest.raises(inline.FormatFailure, match="Duplicate JSON key"):
        inline.format_notebook(source, formatter(tmp_path), {"python"}, path="notebook.ipynb")


def test_xml_namespace_declaration_values_are_preserved_even_when_unused() -> None:
    assert inline.xml_value(b'<root xmlns:model="urn:one">value</root>') != inline.xml_value(
        b'<root xmlns:model="urn:two">value</root>'
    )


def test_inline_inventory_limits_discovery_to_supported_containers() -> None:
    assert inline.eligible_source("courses/demo/authoring/units.py")
    assert inline.eligible_source("docs/example.md")
    assert inline.eligible_source("chapter.ipynb")
    assert inline.eligible_source("chapter.rmd")
    assert not inline.eligible_source("lesson-pages/example.html")
    assert not inline.eligible_source("src/implementation.py")
    assert not inline.eligible_source("qualification/receipt.json")


def test_budget_is_checked_between_files_before_reading_the_next_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/format-policy.json").write_text('{"exclude":[],"preserve":[]}')
    candidate = formatter(tmp_path)
    monkeypatch.setattr(format_repo, "source_files", lambda *args, **kwargs: ["not-read.md"])

    def exhausted() -> None:
        candidate.expired = True
        raise inline.BudgetExhausted("bounded")

    monkeypatch.setattr(candidate, "check_time", exhausted)
    report = inline.inspect_sources(tmp_path, {"python"}, formatter=candidate)
    assert report["complete"] is False and not report["passed"]
    assert report["status_counts"] == {"not-checked": 1}
    assert report["records"][0]["path"] == "not-read.md"
