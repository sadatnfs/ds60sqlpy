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
from scripts import inline_format_contracts as guard_contracts


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
        return b"x = 1\n" if counter["calls"] % 2 else b"x=1\n"

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


def test_python_cell_marker_and_unicode_comments_remain_exact(tmp_path: Path) -> None:
    original = '#%%\nvalue="é"  #Expected: é  value\n'
    candidate = '# %%\nvalue = "é"  # Expected: é  value\n'
    tool = inline.Formatter(tmp_path, lambda *args: candidate.encode())
    assert tool.format(original.encode(), "python", ".py").decode() == (
        '#%%\nvalue = "é"  #Expected: é  value\n'
    )


@pytest.mark.parametrize(
    "grammar,before,after",
    guard_contracts.TREE_EQUIVALENCES,
)
def test_reviewed_tree_layout_changes_preserve_program_structure(
    grammar: str, before: str, after: str
) -> None:
    pytest.importorskip(
        "tree_sitter_language_pack", reason="Pinned native formatter parser required"
    )
    assert (
        inline.tree_signature(before.encode(), grammar)[0]
        == inline.tree_signature(after.encode(), grammar)[0]
    )


@pytest.mark.parametrize(
    "grammar,before,after",
    guard_contracts.TREE_DIFFERENCES,
)
def test_tree_normalization_preserves_holes_tuple_arity_types_and_literal_values(
    grammar: str, before: str, after: str
) -> None:
    pytest.importorskip(
        "tree_sitter_language_pack", reason="Pinned native formatter parser required"
    )
    assert (
        inline.tree_signature(before.encode(), grammar)[0]
        != inline.tree_signature(after.encode(), grammar)[0]
    )


def test_html_attribute_quotes_and_text_are_restored_exactly(tmp_path: Path) -> None:
    pytest.importorskip(
        "tree_sitter_language_pack", reason="Pinned native formatter parser required"
    )
    before = b"<p title='a  &amp; b'>literal  text</p>\n"
    candidate = b'<p title="a  &amp; b">literal  text</p>\n'
    tool = inline.Formatter(tmp_path, lambda *args: candidate)
    assert tool.format(before, "web", ".html") == before


@pytest.mark.parametrize(
    "source,mode",
    [
        (b"class Main { public static void main(String[] args) {} }\n", "unit"),
        (b"int total=2+3; assert total==5;\n", "statements"),
        (b"static int twice(int value) { return 2*value; }\n", "members"),
        (b"private int value = 2;\n", "members"),
        (
            b"boolean failed=false; try { fail(); } catch(Exception e) { failed=true; }\n",
            "statements",
        ),
    ],
)
def test_java_excerpts_have_bounded_syntax_context(source: bytes, mode: str) -> None:
    pytest.importorskip(
        "tree_sitter_language_pack", reason="Pinned native formatter parser required"
    )
    wrapped, observed = inline.java_context(source)
    assert observed == mode
    assert inline.java_unwrap(wrapped, mode) == source


def test_java_wrapper_escape_and_unparseable_fragments_are_refused() -> None:
    pytest.importorskip(
        "tree_sitter_language_pack", reason="Pinned native formatter parser required"
    )
    with pytest.raises(inline.UnsupportedSnippet):
        inline.java_context(b"} dangerous(); {\n")
    with pytest.raises(inline.FormatFailure, match="identity"):
        inline.java_unwrap(b"class Replaced {}\n", "members")
    with pytest.raises(inline.UnsupportedSnippet, match="mixed-member"):
        inline.java_context(b"static void f() {} assert true;\n")


def test_fenced_cpp_adapter_disables_only_added_namespace_comments(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "docker/formatting"
    config.mkdir(parents=True)
    (config / "clang-format.yaml").write_text("BasedOnStyle: LLVM\nSortIncludes: Never\n")
    observed = []

    def fake(command: list[str], source: bytes, root: Path) -> bytes:
        observed.extend(command)
        return source

    monkeypatch.setattr(inline, "invoke", fake)
    inline.adapter_bytes(b"namespace x {}\n", "cpp", ".cpp", tmp_path)
    style = json.loads(next(option for option in observed if option.startswith("--style="))[8:])
    assert style == {"BasedOnStyle": "LLVM", "SortIncludes": "Never", "FixNamespaceComments": False}


def test_shell_placeholder_is_preserved_but_quoted_literal_remains_code(tmp_path: Path) -> None:
    pytest.importorskip(
        "tree_sitter_language_pack", reason="Pinned native formatter parser required"
    )
    tool = inline.Formatter(tmp_path, lambda source, *args: source)
    placeholder = "```sh\ndocker run <your-formatting-image> command\n```\n"
    output, rows = inline.format_document(placeholder, tool, {"shell"}, path="docs/tools.md")
    assert output == placeholder and rows[0]["reason"] == "unsubstituted-shell-template-placeholder"
    literal = "```sh\nprintf '%s' '<your-formatting-image>'\n```\n"
    output, rows = inline.format_document(literal, tool, {"shell"}, path="docs/tools.md")
    assert output == literal and rows[0]["status"] == "clean"


def test_python_non_prose_values_and_replace_needles_are_not_formatted(tmp_path: Path) -> None:
    text = "```python\nx=1\n```\n"
    source = (
        "guide = " + repr(text) + "\nexpected = " + repr(text) + "\n"
        "guide = guide.replace(" + repr(text) + ", 'literal replacement')\n"
        "code = {'body': " + repr(text) + "}\n"
    )
    updated, records = inline.format_authoring_python(
        source, formatter(tmp_path), {"python"}, path="courses/demo/authoring/units.py"
    )
    tree = ast.parse(updated)
    assert isinstance(tree.body[0], ast.Assign) and isinstance(tree.body[0].value, ast.Constant)
    assert tree.body[0].value.value == "```python\nx = 1\n```\n"
    assert "expected = " + repr(text) in updated
    assert "guide.replace(" + repr(text) in updated
    assert "code = {'body': " + repr(text) + "}" in updated
    assert any("non-prose" in item["reason"] for item in records)


def test_reviewed_nlp_example_role_does_not_admit_solution_arguments(tmp_path: Path) -> None:
    text = "```python\nx=1\n```\n"
    source = "author(1, 'intro', [], [('title', " + repr(text) + ")], [], " + repr(text) + ")\n"
    updated, records = inline.format_authoring_python(
        source, formatter(tmp_path), {"python"}, path="courses/nlp/authoring/advanced/batch.py"
    )
    assert updated.count("x = 1") == 1 and updated.count("x=1") == 1
    assert [record["status"] for record in records].count("formatted") == 1


def test_json_prose_and_identical_expected_values_are_distinct_roles(tmp_path: Path) -> None:
    text = "```python\nx=1\n```\n"
    source = json.dumps(
        {"guide": text, "expected": text, "worked_examples": [{"explanation": text, "code": text}]}
    )
    updated, records = inline.format_authoring_json(
        source, formatter(tmp_path), {"python"}, path="courses/demo/authoring/units.json"
    )
    parsed = json.loads(updated)
    assert parsed["guide"] == "```python\nx = 1\n```\n"
    assert parsed["expected"] == text and parsed["worked_examples"][0]["code"] == text
    assert parsed["worked_examples"][0]["explanation"] == "```python\nx = 1\n```\n"
    assert [record["status"] for record in records] == [
        "formatted",
        "preserved",
        "formatted",
        "preserved",
    ]


def test_literal_restoration_may_converge_but_final_output_must_be_idempotent(
    tmp_path: Path,
) -> None:
    variants = {b"x=1\n": b"x =1\n", b"x =1\n": b"x = 1\n", b"x = 1\n": b"x = 1\n"}
    tool = inline.Formatter(tmp_path, lambda source, *args: variants[source])
    assert tool.format(b"x=1\n", "python", ".py") == b"x = 1\n"


def test_html_void_tail_is_sibling_text_but_foreign_content_is_not_normalized() -> None:
    parsers = pytest.importorskip(
        "tree_sitter_language_pack", reason="Pinned native formatter parser required"
    )
    before = b'<label><input type="checkbox">Show a reminder</label>'
    after = b'<label><input type="checkbox" />Show a reminder</label>'
    assert inline.tree_signature(before, "html")[0] == inline.tree_signature(after, "html")[0]
    assert (
        inline.tree_signature(before, "html")[0]
        != inline.tree_signature(after.replace(b"reminder", b"different"), "html")[0]
    )
    tree = parsers.get_parser("html").parse(b'<svg><input name="literal"></input></svg>')
    pending = [tree.root_node]
    while pending:
        node = pending.pop()
        assert not inline.html_void_tag(node)
        pending.extend(node.children)


@pytest.mark.parametrize(
    "before,after",
    [
        (b'type A = {kind:"one"} | {kind:"two"};', b'type A = | {kind:"one"} | {kind:"two"};'),
        (b"type A = string | (number & B);", b"type A = | string | (number & B);"),
    ],
)
def test_typescript_leading_union_separator_retains_all_members(
    before: bytes, after: bytes
) -> None:
    pytest.importorskip(
        "tree_sitter_language_pack", reason="Pinned native formatter parser required"
    )
    assert (
        inline.tree_signature(before, "typescript")[0]
        == inline.tree_signature(after, "typescript")[0]
    )
    assert (
        inline.tree_signature(b"type A = string | number;", "typescript")[0]
        != inline.tree_signature(b"type A = | string;", "typescript")[0]
    )


def test_rust_macro_punctuation_is_opaque_and_restored_with_explicit_inventory(
    tmp_path: Path,
) -> None:
    pytest.importorskip(
        "tree_sitter_language_pack", reason="Pinned native formatter parser required"
    )
    before = b"fn main(){custom!(a,b);}\n"
    candidate = b"fn main() { custom!(a, b,); }\n"
    tool = inline.Formatter(tmp_path, lambda *args: candidate)
    output, rows = inline.format_document(
        "```rust\n" + before.decode() + "```\n", tool, {"rust"}, path="guide.md"
    )
    assert "custom!(a,b)" in output and "custom!(a, b,)" not in output
    assert rows[0]["preserved_regions"] == {"opaque-rust-macro-token-trees": 1}
    assert "opaque-rust-macro" in rows[0]["reason"]
    assert (
        inline.tree_signature(before, "rust")[0]
        != inline.tree_signature(before.replace(b"a,b", b"a,b,"), "rust")[0]
    )


def test_scala_single_string_continuation_keeps_its_literal_value() -> None:
    pytest.importorskip(
        "tree_sitter_language_pack", reason="Pinned native formatter parser required"
    )
    before = b'val query = "SELECT id FROM rows"\n'
    after = b'val query =\n  "SELECT id FROM rows"\n'
    assert inline.tree_signature(before, "scala")[0] == inline.tree_signature(after, "scala")[0]
    assert (
        inline.tree_signature(before, "scala")[0]
        != inline.tree_signature(after.replace(b"id", b"name"), "scala")[0]
    )


def generation_root(tmp_path: Path) -> Path:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/format-policy.json").write_text(
        json.dumps(
            {
                "exclude": [
                    {"pattern": "generated/*.md", "reason": "Generated by the owner renderer"}
                ],
                "preserve": [
                    {"path": "generated/historical.md", "reason": "Immutable historical receipt"}
                ],
            }
        )
    )
    return tmp_path


def test_generation_hook_formats_memory_and_preserves_owner_write_boundary(tmp_path: Path) -> None:
    root = generation_root(tmp_path)
    source = "Prose \\(x^2\\).\n```python\nx=1\n```\n"
    result = inline.canonical_markdown(
        source, root=root, path="generated/guide.md", formatter=formatter(root)
    )
    assert result == "Prose \\(x^2\\).\n```python\nx = 1\n```\n"
    assert not (root / "generated/guide.md").exists()
    assert (
        inline.canonical_markdown(
            result, root=root, path="generated/guide.md", formatter=formatter(root)
        )
        == result
    )


@pytest.mark.parametrize(
    "path",
    [
        "../escape.md",
        "/absolute.md",
        "generated/guide.html",
        "authored.md",
        "generated/historical.md",
    ],
)
def test_generation_hook_rejects_unowned_or_unsafe_outputs(tmp_path: Path, path: str) -> None:
    root = generation_root(tmp_path)
    with pytest.raises(ValueError):
        inline.canonical_markdown(
            "```python\nx=1\n```\n", root=root, path=path, formatter=formatter(root)
        )


def test_generation_hook_missing_tool_is_not_silently_skipped(tmp_path: Path) -> None:
    root = generation_root(tmp_path)

    def unavailable(*args: Any) -> bytes:
        raise inline.FormatFailure("Missing prepared adapter: ruff")

    tool = inline.Formatter(root, unavailable)
    with pytest.raises(inline.FormatFailure, match="prepared formatter environment"):
        inline.canonical_markdown(
            "```python\nx=1\n```\n", root=root, path="generated/guide.md", formatter=tool
        )


def test_generation_hook_reports_transcripts_without_changing_them(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = generation_root(tmp_path)
    source = "```text\nExpected   output\n```\n"
    assert (
        inline.canonical_markdown(
            source, root=root, path="generated/guide.md", formatter=formatter(root)
        )
        == source
    )
    assert "untyped-or-output-transcript" in capsys.readouterr().err


def test_python_formatter_cannot_move_an_identical_type_ignore_between_statements(
    tmp_path: Path,
) -> None:
    before = b"x: int = 'first' # type: ignore[assignment]\ny: int = 'second'\n"
    after = b"x: int = 'first'\ny: int = 'second' # type: ignore[assignment]\n"
    tool = inline.Formatter(tmp_path, lambda *args: after)
    with pytest.raises(inline.FormatFailure, match="syntax or literal"):
        tool.format(before, "python", ".py")


def test_native_contract_gate_rejects_a_guard_that_erases_semantic_differences(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(inline, "tree_signature", lambda *args, **kwargs: ("same", []))
    with pytest.raises(ValueError, match="semantic distinction"):
        guard_contracts.verify(tmp_path, {"web"})


def test_python_native_contract_gate_needs_no_non_python_parser(tmp_path: Path) -> None:
    assert guard_contracts.verify(tmp_path, {"python"}) == 2


def test_web_example_raw_code_slot_preserves_all_other_values(tmp_path: Path) -> None:
    calls = []

    def json_adapter(source: bytes, language: str, suffix: str, root: Path) -> bytes:
        assert language == "web" and suffix == ".json"
        calls.append(source)
        return (json.dumps(json.loads(source), indent=2) + "\n").encode()

    untouched = '~~~json\n{"expected":1}\n~~~\n'
    value: dict[str, Any] = {
        "schema_version": 1,
        "chapters": [
            {
                "examples": [
                    [untouched, untouched, "json", '{"literal":"a  b","marks":"~~~"}', untouched]
                ],
                "other": "exact",
            }
        ],
    }
    source = json.dumps(value, ensure_ascii=False)
    tool = inline.Formatter(tmp_path, json_adapter)
    changed, records = inline.format_authoring_json(
        source, tool, {"web"}, path="courses/web-development/authoring/chapters.json"
    )
    result = json.loads(changed)
    assert result["chapters"][0]["examples"][0][:3] == value["chapters"][0]["examples"][0][:3]
    assert result["chapters"][0]["examples"][0][4] == untouched
    assert result["chapters"][0]["other"] == "exact"
    code = result["chapters"][0]["examples"][0][3]
    assert json.loads(code) == {"literal": "a  b", "marks": "~~~"}
    assert not code.endswith("\n") and code != value["chapters"][0]["examples"][0][3]
    assert any(
        record["container"] == "json-authoring-code" and record["json_path"][-1] == 3
        for record in records
    )
    assert all(
        record["status"] == "preserved" for record in records if record["json_path"][-1] != 3
    )
    assert calls
    repeated, _ = inline.format_authoring_json(
        changed, tool, {"web"}, path="courses/web-development/authoring/chapters.json"
    )
    assert repeated == changed


def test_raw_web_slot_does_not_admit_other_paths_or_unselected_tools(tmp_path: Path) -> None:
    source = json.dumps(
        {
            "schema_version": 1,
            "chapters": [{"examples": [["heading", "intro", "json", '{"x":1}', "expected"]]}],
        }
    )

    def forbidden(*args: Any) -> bytes:
        pytest.fail("Unselected or unknown raw-code slot reached a formatter")

    tool = inline.Formatter(tmp_path, forbidden)
    unknown, rows = inline.format_authoring_json(
        source, tool, {"web"}, path="courses/other/authoring/chapters.json"
    )
    assert unknown == source and rows == []
    unselected, rows = inline.format_authoring_json(
        source, tool, {"python"}, path="courses/web-development/authoring/chapters.json"
    )
    assert unselected == source and rows[0]["status"] == "not-selected"


def test_raw_web_transcript_and_malformed_schema_are_not_rewritten(tmp_path: Path) -> None:
    source = json.dumps(
        {
            "schema_version": 1,
            "chapters": [
                {"examples": [["heading", "intro", "text", "expected   output\n", "observation"]]}
            ],
        }
    )
    changed, rows = inline.format_authoring_json(
        source, formatter(tmp_path), {"web"}, path="courses/web-development/authoring/chapters.json"
    )
    assert changed == source and rows[0]["reason"] == "untyped-or-output-transcript"
    invalid = json.dumps(
        {"schema_version": 1, "chapters": [{"examples": [["heading", "intro", "json", "{}"]]}]}
    )
    with pytest.raises(inline.FormatFailure, match="five|heading, intro"):
        inline.format_authoring_json(
            invalid,
            formatter(tmp_path),
            {"web"},
            path="courses/web-development/authoring/chapters.json",
        )


def test_raw_web_program_value_change_rejects_entire_json(tmp_path: Path) -> None:
    source = json.dumps(
        {
            "schema_version": 1,
            "chapters": [{"examples": [["heading", "intro", "json", '{"x":1}', "expected"]]}],
        }
    )
    tool = inline.Formatter(tmp_path, lambda *args: b'{"x": 2}\n')
    changed, records = inline.format_authoring_json(
        source, tool, {"web"}, path="courses/web-development/authoring/chapters.json"
    )
    assert changed == source and records[0]["status"] == "error"
