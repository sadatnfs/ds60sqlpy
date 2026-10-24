from __future__ import annotations

import re
from dataclasses import replace
from html.parser import HTMLParser
from pathlib import Path

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.lesson_reader import (
    LinkResolver,
    artifact_targets,
    build_lesson_html,
    build_reader_files,
    build_reference_files,
    reader_drift,
    reference_drift,
    reference_relative_path,
    render_inline,
    render_markdown,
    rendered_targets,
    write_reader_files,
    write_reference_files,
)
from scripts.build_lesson_readers import main

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_LOCAL_ARTIFACT_HREF = re.compile(
    r'href="(?!https?://|mailto:|#|vscode:)[^"]+\.(?:md|sql|ipynb|py)(?:[?#][^"]*)?"',
    flags=re.IGNORECASE,
)
LEAKED_AUTHORING_COMMENT = re.compile(
    r"<!--\s*(?:(?:BEGIN|END)\b|beginner-solution-enrichment\b)",
    re.IGNORECASE,
)


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _visible_text(document: str) -> str:
    parser = _VisibleTextParser()
    parser.feed(document)
    return "".join(parser.parts)


def test_every_catalog_entry_has_a_current_portable_reader() -> None:
    catalog = Catalog.load(REPO_ROOT)
    expected = build_reader_files(catalog)

    assert len(expected) == len(catalog.lessons())
    assert reader_drift(expected, repo_root=REPO_ROOT) == []

    for lesson in catalog:
        relative = f"lesson-pages/{lesson.id}.html"
        rendered = expected[relative]
        assert f"<title>{lesson.id} ·" in rendered
        assert 'id="guide"' in rendered
        assert 'id="learner"' in rendered
        assert 'id="solution-1"' in rendered
        assert 'id="solution-2"' in rendered
        assert lesson.guide_path in rendered
        assert lesson.lesson_path in rendered
        assert '<script src="' not in rendered
        assert '<link rel="stylesheet"' not in rendered
        assert 'const SERVER_TOKEN = "";' in rendered
        assert RAW_LOCAL_ARTIFACT_HREF.search(rendered) is None
        assert LEAKED_AUTHORING_COMMENT.search(_visible_text(rendered)) is None
        assert rendered.endswith("\n")
        assert all(line == line.rstrip() for line in rendered.splitlines())


def test_reader_renders_notebooks_and_sql_as_html_not_raw_downloads() -> None:
    catalog = Catalog.load(REPO_ROOT)
    python_reader = build_lesson_html(catalog, catalog.get("python-01"))
    sql_reader = build_lesson_html(catalog, catalog.get("sql-01"))

    assert "Code cell 1" in python_reader
    assert "Readable preview." in python_reader
    assert "1 + 1" in _visible_text(python_reader)
    assert 'class="source-code language-sql"' in sql_reader
    assert "SELECT customer_id" in _visible_text(sql_reader)
    assert "psql -X -v ON_ERROR_STOP=1" in sql_reader
    assert "START_DS60.cmd" in sql_reader
    assert "Create/open guided SQL notebook" in sql_reader
    assert 'action: "jupyter-sql"' in sql_reader
    assert "Ask an AI tutor about this lesson" in python_reader
    assert "Copy tutor prompt" in python_reader
    assert "guide-ds60sqlpy-learning" in python_reader
    assert "python-01" in python_reader
    assert "python/ds-60day/notebooks/day01_setup_and_repl.ipynb" in python_reader
    assert "solutions/" in python_reader
    assert "advanced_sql_training" in sql_reader
    assert "complete psql transcript/query result" in sql_reader
    assert "Projection, Predicate, Deterministic ordering" in sql_reader


@pytest.mark.parametrize(
    ("runner", "suffix", "source", "expected"),
    [
        ("cpp", ".cpp", "#include <iostream>\n// Exercise 1: inspect <script>.", "C++ source file"),
        ("scala", ".scala", '// Exercise 1: inspect println("<hello>").', "Scala source file"),
        ("kubernetes", ".yaml", "# Exercise 1: explain replicas.\nreplicas: 2", "YAML manifest"),
        ("none", ".md", "## Exercises\n\n1. Explain the evidence.", "record your evidence"),
    ],
)
def test_future_readers_preserve_language_and_capability_boundaries(
    tmp_path: Path, runner: str, suffix: str, source: str, expected: str
) -> None:
    original = Catalog.load(REPO_ROOT).get("python-01")
    lesson = replace(
        original,
        id="future-01",
        track="future",
        day=1,
        runner=runner,
        prerequisites=(),
        lesson_path=f"courses/future/learner{suffix}",
        guide_path="courses/future/guide.md",
        solution_paths=("courses/future/solutions/explanation.md",),
    )
    for path, content in (
        (lesson.lesson_path, source),
        (lesson.guide_path, "# Future lesson\n\nA readable guide."),
        (lesson.solution_paths[0], "# Explanation\n\nSeparate worked reasoning."),
    ):
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    catalog = Catalog(
        tmp_path,
        [lesson],
        tracks={"future": {"title": "Future track", "plan": lesson.guide_path}},
    )
    document = build_lesson_html(catalog, lesson, targets=artifact_targets(catalog))

    assert expected in document
    assert "Run this Python file" not in document
    assert "Run this notebook with the course kernel" not in document
    assert 'id="solution-1"' in document and 'id="solution-2"' not in document
    assert "const LAB_MODE = false;" in document
    assert 'class="lab-only" href="../learn?lesson=future-01" hidden' in document
    assert "<script>." not in document
    if runner != "none":
        assert "execution adapter is not implemented" in document


def test_registered_plan_is_rendered_without_a_link_from_existing_docs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("ds60sqlpy.lesson_reader.COURSE_GUIDE_REFERENCE_PATHS", ())
    plan = tmp_path / "courses" / "new-topic" / "README.md"
    plan.parent.mkdir(parents=True)
    plan.write_text("# A new track\n\nIts plan is catalog metadata.", encoding="utf-8")
    catalog = Catalog(
        tmp_path,
        [],
        tracks={"new-topic": {"title": "New topic", "plan": "courses/new-topic/README.md"}},
    )

    references = build_reference_files(catalog)

    assert reference_relative_path("courses/new-topic/README.md") in references


def test_math_in_tables_keeps_conditional_probability_and_superscripts() -> None:
    resolver = LinkResolver(repo_root=REPO_ROOT, source_path=REPO_ROOT / "README.md", targets={})
    document = render_markdown(
        "| Concept | Notation |\n| --- | --- |\n"
        r"| Conditional | \(P(A\mid B)\) |" + "\n"
        r"| Score | \(R^2\) |" + "\n"
        r"| Escaped pipe | a\|b |" + "\n",
        resolver=resolver,
    )

    assert '<math xmlns="http://www.w3.org/1998/Math/MathML"' in document
    assert "<mo>∣</mo>" in document and "<msup>" in document
    assert "Amid B" not in document and "<td>a|b</td>" in document
    assert render_inline(r"`\(R^2\)`", resolver) == r"<code>\(R^2\)</code>"


@pytest.mark.parametrize(
    "suffix",
    [".cpp", ".scala", ".java", ".mjs", ".mts", ".yaml", ".json", ".csv", ".txt", ".toml", ".lock"],
)
def test_authored_text_reference_is_escaped_and_rendered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, suffix: str
) -> None:
    monkeypatch.setattr("ds60sqlpy.lesson_reader.COURSE_GUIDE_REFERENCE_PATHS", ())
    plan = tmp_path / "courses" / "future" / "README.md"
    plan.parent.mkdir(parents=True)
    plan.write_text(f"# Track\n\n[Fixture](fixture{suffix})", encoding="utf-8")
    (plan.parent / f"fixture{suffix}").write_text("<script>example</script>", encoding="utf-8")
    catalog = Catalog(
        tmp_path, [], tracks={"future": {"title": "Future", "plan": "courses/future/README.md"}}
    )

    references = build_reference_files(catalog)
    reference = reference_relative_path(f"courses/future/fixture{suffix}")

    assert reference in references
    assert "<script>example</script>" in _visible_text(references[reference])
    assert "<script>example</script>" not in references[reference]
    plan_reference = references[reference_relative_path("courses/future/README.md")]
    assert f"fixture{suffix}.html" in plan_reference


@pytest.mark.parametrize(
    "path", [".learning/pads/saved.json", "artifacts/private.json", "courses/a/credentials.json"]
)
def test_private_files_are_not_rendered_as_reference_pages(path: str) -> None:
    with pytest.raises(ValueError, match="Unsafe source path"):
        reference_relative_path(path)


def test_license_has_a_safe_text_reference(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ds60sqlpy.lesson_reader.COURSE_GUIDE_REFERENCE_PATHS", ())
    (tmp_path / "README.md").write_text("# Track\n\n[License](LICENSE)", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("Permission to use <authored> text.", encoding="utf-8")
    catalog = Catalog(tmp_path, [], tracks={"future": {"title": "Future", "plan": "README.md"}})

    references = build_reference_files(catalog)

    assert "&lt;authored&gt;" in references[reference_relative_path("LICENSE")]


def test_reader_uses_the_guides_lesson_specific_tutor_prompt() -> None:
    catalog = Catalog.load(REPO_ROOT)
    rendered = build_lesson_html(catalog, catalog.get("python-04"))

    assert "eager collection building, and lazy generators" in rendered
    assert "Direct catalog prerequisites: `python-foundations-02`" in rendered


def test_markdown_links_to_catalog_artifacts_become_reader_links() -> None:
    catalog = Catalog.load(REPO_ROOT)
    guide = catalog.resolve(catalog.get("python-01").guide_path)
    resolver = LinkResolver(
        repo_root=REPO_ROOT,
        source_path=guide,
        targets=artifact_targets(catalog),
    )

    rendered = render_inline(
        "[learner](../notebooks/day01_setup_and_repl.ipynb) "
        "[solution](../solutions/day01_setup_and_repl/day01_solutions.md)",
        resolver,
    )

    assert 'href="python-01.html#learner"' in rendered
    assert 'href="python-01.html#solution-1"' in rendered
    assert ".ipynb" not in rendered


def test_markdown_links_to_course_docs_become_rendered_reference_links() -> None:
    catalog = Catalog.load(REPO_ROOT)
    guide = catalog.resolve(catalog.get("python-01").guide_path)
    resolver = LinkResolver(
        repo_root=REPO_ROOT,
        source_path=guide,
        targets=rendered_targets(catalog),
        output_path="lesson-pages/python-01.html",
    )

    rendered = render_inline("[Windows setup](../../../docs/setup/windows.md)", resolver)

    assert 'href="../reference-pages/docs/setup/windows.md.html"' in rendered


def test_markdown_renderer_escapes_html_and_blocks_unsafe_schemes() -> None:
    catalog = Catalog.load(REPO_ROOT)
    guide = catalog.resolve(catalog.get("python-01").guide_path)
    resolver = LinkResolver(
        repo_root=REPO_ROOT,
        source_path=guide,
        targets=artifact_targets(catalog),
    )

    rendered = render_markdown(
        "# Safe\n\n<script>alert('no')</script>\n\n[bad](javascript:alert(1))",
        resolver=resolver,
    )

    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "javascript:" not in rendered


def test_markdown_renderer_hides_comments_except_in_fenced_examples() -> None:
    catalog = Catalog.load(REPO_ROOT)
    guide = catalog.resolve(catalog.get("python-01").guide_path)
    resolver = LinkResolver(
        repo_root=REPO_ROOT,
        source_path=guide,
        targets=artifact_targets(catalog),
    )

    rendered = render_markdown(
        """# Visible heading

<!-- BEGIN INTERNAL AUTHORING MARKER -->
Visible before <!-- inline maintainer note --> visible after.
<!-- a multiline note
that must not reach learners -->

Inline code keeps the literal marker: `<!-- learner-visible example -->`.

An unclosed marker stays visible and cannot swallow the rest: <!-- unfinished

```html
<!-- This fenced comment is lesson content. -->
```
""",
        resolver=resolver,
    )

    assert "INTERNAL AUTHORING MARKER" not in rendered
    assert "inline maintainer note" not in rendered
    assert "that must not reach learners" not in rendered
    assert "Visible before  visible after." in rendered
    assert "&lt;!-- learner-visible example --&gt;" in rendered
    assert "&lt;!-- unfinished" in rendered
    assert "&lt;!-- This fenced comment is lesson content. --&gt;" in rendered


def test_markdown_emphasis_can_span_inline_code() -> None:
    catalog = Catalog.load(REPO_ROOT)
    guide = catalog.resolve(catalog.get("python-01").guide_path)
    resolver = LinkResolver(
        repo_root=REPO_ROOT,
        source_path=guide,
        targets=artifact_targets(catalog),
    )

    rendered = render_inline("**`pip` installs to the selected interpreter:** yes", resolver)

    assert rendered == (
        "<strong><code>pip</code> installs to the selected interpreter:</strong> yes"
    )


def test_rendered_references_cover_recursive_local_markdown_and_sql_links() -> None:
    catalog = Catalog.load(REPO_ROOT)
    expected = build_reference_files(catalog)

    assert len(expected) >= 30
    assert reference_relative_path("README.md") in expected
    assert reference_relative_path("docs/lesson-readers.md") in expected
    assert reference_relative_path("docs/setup/windows.md") in expected
    assert reference_relative_path("sql/professional/fixtures/migrations/cleanup.sql") in expected
    assert reference_drift(expected, repo_root=REPO_ROOT) == []

    for relative_path, rendered in expected.items():
        assert relative_path.startswith("reference-pages/")
        assert "<title>" in rendered
        assert "Back to lessons" in rendered
        assert RAW_LOCAL_ARTIFACT_HREF.search(rendered) is None
        assert LEAKED_AUTHORING_COMMENT.search(_visible_text(rendered)) is None
        assert '<script src="' not in rendered
        assert '<link rel="stylesheet"' not in rendered
        assert rendered.endswith("\n")
        assert all(line == line.rstrip() for line in rendered.splitlines())


def test_static_reader_defers_completion_to_dashboard() -> None:
    catalog = Catalog.load(REPO_ROOT)
    rendered = build_lesson_html(catalog, catalog.get("python-01"))

    assert '<label class="completion launcher-only" hidden>' in rendered
    assert "Track completion on the course dashboard" in rendered
    assert 'document.querySelectorAll(".static-only")' in rendered
    assert "if (launcherMode) {" in rendered


def test_reader_writer_supports_external_output_and_detects_drift(tmp_path: Path) -> None:
    catalog = Catalog.load(REPO_ROOT)
    expected = build_reader_files(catalog)
    output = tmp_path / "readers"

    write_reader_files(expected, repo_root=REPO_ROOT, output_dir=output)
    assert reader_drift(expected, repo_root=REPO_ROOT, output_dir=output) == []

    (output / "python-01.html").write_text("changed", encoding="utf-8")
    (output / "old.html").write_text("obsolete", encoding="utf-8")
    drift = reader_drift(expected, repo_root=REPO_ROOT, output_dir=output)
    assert any(item.startswith("changed:") for item in drift)
    assert any(item.startswith("unexpected:") for item in drift)


def test_reference_writer_supports_external_output_and_detects_drift(tmp_path: Path) -> None:
    catalog = Catalog.load(REPO_ROOT)
    expected = build_reference_files(catalog)
    output = tmp_path / "references"

    write_reference_files(expected, repo_root=REPO_ROOT, output_dir=output)
    assert reference_drift(expected, repo_root=REPO_ROOT, output_dir=output) == []

    windows_page = output / "docs" / "setup" / "windows.md.html"
    windows_page.write_text("changed", encoding="utf-8")
    obsolete = output / "obsolete" / "old.html"
    obsolete.parent.mkdir()
    obsolete.write_text("obsolete", encoding="utf-8")
    drift = reference_drift(expected, repo_root=REPO_ROOT, output_dir=output)
    assert any(item.startswith("changed:") for item in drift)
    assert any(item.startswith("unexpected:") for item in drift)


def test_reader_script_can_write_and_check_external_output(tmp_path: Path) -> None:
    output = tmp_path / "generated"

    assert main(["--output-dir", str(output)]) == 0
    assert main(["--output-dir", str(output), "--check"]) == 0
    assert (output / "lesson-pages" / "python-01.html").is_file()
    assert (output / "reference-pages" / "docs" / "setup" / "windows.md.html").is_file()


def test_reference_build_reuses_one_validated_closure_for_all_links(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ds60sqlpy import lesson_reader

    monkeypatch.setattr(lesson_reader, "COURSE_GUIDE_REFERENCE_PATHS", ())
    folder = tmp_path / "courses" / "fixture"
    folder.mkdir(parents=True)
    (folder / "README.md").write_text("# Fixture\n\n[Related](reference.md)\n", encoding="utf-8")
    (folder / "reference.md").write_text("# Related\n\n[Back](README.md)\n", encoding="utf-8")
    catalog = Catalog(
        tmp_path, [], tracks={"fixture": {"title": "Fixture", "plan": "courses/fixture/README.md"}}
    )
    discover = lesson_reader.reference_source_paths
    calls = 0

    def count_discovery(selected: Catalog) -> tuple[Path, ...]:
        nonlocal calls
        calls += 1
        return discover(selected)

    monkeypatch.setattr(lesson_reader, "reference_source_paths", count_discovery)
    pages = build_reference_files(catalog)
    assert calls == 1
    assert set(pages) == {
        "reference-pages/courses/fixture/README.md.html",
        "reference-pages/courses/fixture/reference.md.html",
    }
    assert 'href="reference.md.html"' in pages["reference-pages/courses/fixture/README.md.html"]
    assert 'href="README.md.html"' in pages["reference-pages/courses/fixture/reference.md.html"]
