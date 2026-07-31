from __future__ import annotations

import re
from pathlib import Path

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


def test_every_catalog_entry_has_a_current_portable_reader() -> None:
    catalog = Catalog.load(REPO_ROOT)
    expected = build_reader_files(catalog)

    assert len(expected) == len(catalog.lessons()) == 154
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
        assert rendered.endswith("\n")
        assert all(line == line.rstrip() for line in rendered.splitlines())


def test_reader_renders_notebooks_and_sql_as_html_not_raw_downloads() -> None:
    catalog = Catalog.load(REPO_ROOT)
    python_reader = build_lesson_html(catalog, catalog.get("python-01"))
    sql_reader = build_lesson_html(catalog, catalog.get("sql-01"))

    assert "Code cell 1" in python_reader
    assert "Readable preview." in python_reader
    assert "1 + 1" in python_reader
    assert 'class="source-code language-sql"' in sql_reader
    assert "SELECT customer_id" in sql_reader
    assert "psql -X -v ON_ERROR_STOP=1" in sql_reader
    assert "START_DS60.cmd" in sql_reader
    assert "Create/open guided SQL notebook" in sql_reader
    assert 'action: "jupyter-sql"' in sql_reader
    assert "Ask Codex about this lesson" in python_reader
    assert "Copy Codex prompt" in python_reader
    assert "guide-ds60sqlpy-learning" in python_reader
    assert "python-01" in python_reader
    assert "python/ds-60day/notebooks/day01_setup_and_repl.ipynb" in python_reader
    assert "solutions/" in python_reader
    assert "advanced_sql_training" in sql_reader
    assert "complete psql transcript/query result" in sql_reader
    assert "Projection, Predicate, Deterministic ordering" in sql_reader


def test_reader_uses_the_guides_lesson_specific_codex_prompt() -> None:
    catalog = Catalog.load(REPO_ROOT)
    rendered = build_lesson_html(catalog, catalog.get("python-04"))

    assert "eager collection building, and lazy generators" in rendered
    assert "Direct catalog prerequisites: `python-03`" in rendered


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
