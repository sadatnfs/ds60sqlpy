"""Offline publication checks catch broken anchors without executing page code."""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

from ds60sqlpy.curriculum_framework import is_content_link
from scripts.check_published_links import ASSETS, inspect_published, main


@pytest.fixture
def site(tmp_path: Path) -> Path:
    documents = {
        "START_HERE.html": '<h1 id="start">Start</h1>',
        "lesson-pages/python-01.html": '<h1 id="lesson">Lesson</h1>',
        "reference-pages/docs/setup.md.html": '<h1 id="setup">Setup</h1>',
        "src/ds60sqlpy/assets/classroom.html": '<main id="workspace">Classroom</main>',
        **dict.fromkeys(ASSETS.values(), "/* mapped asset fixture */"),
    }
    for relative, content in documents.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return tmp_path


def write_page(site: Path, relative: str, document: str) -> None:
    (site / relative).write_text(document, encoding="utf-8")


def test_relative_urls_unicode_fragments_aliases_and_static_assets(site: Path) -> None:
    write_page(
        site,
        "lesson-pages/python-01.html",
        """<h1 id="café & tea">Lesson</h1>
        <a href="#caf%C3%A9%20%26%20tea">Local heading</a>
        <a href="?view=reading#caf%C3%A9%20%26%20tea">Same document query</a>
        <a href="../reference-pages/docs/setup.md.html?view=reading#setup">Setup</a>
        <a href="../learn?lesson=python-01#workspace">Classroom</a>
        <a href="/#workspace">Home alias</a>
        <a href="/journeys#workspace">Earlier alias</a>
        <a href="/journey-preview#workspace">Preview alias</a>
        <a href="../START_HERE.html#start">Contents</a>
        <link href="/assets/classroom.css" rel="stylesheet">
        <link href="/assets/rich-content.css" rel="stylesheet">
        <script src="/assets/classroom.js"></script>
        <script src="/assets/browser-preview.js"></script>""",
    )
    report = inspect_published(site)
    assert report["failure_count"] == 0
    assert report["local_links_checked"] == 12
    assert report["fragments_checked"] == 8


def test_stale_heading_link_is_rejected_until_the_authored_link_is_updated(site: Path) -> None:
    write_page(
        site,
        "reference-pages/docs/setup.md.html",
        '<h2 id="optional-legacy-windows-first-run-wizard">Optional wizard</h2>',
    )
    write_page(
        site,
        "START_HERE.html",
        '<a href="reference-pages/docs/setup.md.html#windows-start-with-the-first-run-wizard">'
        "Windows</a>",
    )
    report = inspect_published(site)
    assert report["failure_count"] == 1
    assert report["failures"][0]["kind"] == "missing_fragment"
    write_page(
        site,
        "START_HERE.html",
        '<a href="reference-pages/docs/setup.md.html#optional-legacy-windows-first-run-wizard">'
        "Windows</a>",
    )
    assert inspect_published(site)["failure_count"] == 0


def test_unserved_raw_files_missing_pages_and_missing_assets_are_rejected(site: Path) -> None:
    (site / "private.md").write_text("Existing but not served", encoding="utf-8")
    write_page(
        site,
        "START_HERE.html",
        '<a href="private.md">Raw</a><a href="lesson-pages/missing.html">Missing</a>'
        '<script src="/assets/missing.js"></script>',
    )
    report = inspect_published(site)
    assert [failure["kind"] for failure in report["failures"]] == ["missing_local_target"] * 3


def test_duplicate_ids_are_reported_but_escaped_code_and_script_strings_are_not_parsed(
    site: Path,
) -> None:
    write_page(
        site,
        "START_HERE.html",
        """<h1 id="duplicate">Title</h1><h2 id="duplicate">Again</h2>
        <pre>&lt;a href="missing.html" id="duplicate"&gt;example&lt;/a&gt;</pre>
        <script>const example = '<a href="also-missing.html" id="duplicate">';</script>""",
    )
    report = inspect_published(site)
    assert report["local_links_checked"] == 0
    assert report["failures"] == [
        {"path": "START_HERE.html", "line": 1, "kind": "duplicate_id", "target": "duplicate"}
    ]


def test_external_urls_and_text_matching_are_explicitly_unverified(site: Path) -> None:
    write_page(
        site,
        "START_HERE.html",
        """<a href="https://example.invalid/missing#not-a-real-heading">External</a>
        <a href="//example.invalid/missing">Protocol relative</a>
        <a href="mailto:learner@example.test">Email</a>
        <img src="data:image/png;base64,AAAA">
        <a href="lesson-pages/python-01.html#:~:text=unverified">Text fragment</a>""",
    )
    report = inspect_published(site)
    assert report["failure_count"] == 0
    assert report["external_urls_skipped"] == 4
    assert report["text_fragment_directives_skipped"] == 1
    assert report["fragments_checked"] == 0
    assert any("not fetched" in limit for limit in report["limitations"])


def test_base_url_cannot_silently_change_resolution(site: Path) -> None:
    write_page(site, "START_HERE.html", '<base href="https://example.invalid/">')
    assert inspect_published(site)["failures"][0]["kind"] == "unsupported_base_url"


def test_symlinked_html_is_not_read_outside_the_package(
    site: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    outside = tmp_path_factory.mktemp("outside-publication") / "outside.html"
    outside.write_bytes(b"\xff")
    target = site / "lesson-pages/linked.html"
    try:
        target.symlink_to(outside)
    except NotImplementedError:
        pytest.skip("This platform does not implement symlinks")
    except OSError as exc:
        if sys.platform == "win32" and getattr(exc, "winerror", None) in {5, 1314}:
            pytest.skip("Windows symlink creation requires unavailable privileges")
        raise
    report = inspect_published(site)
    assert any(failure["kind"] == "linked_published_source" for failure in report["failures"])


def test_missing_publication_inputs_and_optional_json_report(tmp_path: Path) -> None:
    report_path = tmp_path / "report.json"
    assert main(["--root", str(tmp_path), "--report", str(report_path)]) == 1
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["html_pages_checked"] == 0
    assert report["failure_count"] > 0


def test_legacy_named_anchors_and_browser_top_fragment_are_accepted(site: Path) -> None:
    write_page(
        site,
        "START_HERE.html",
        '<a name="legacy"></a><a href="#legacy">Legacy</a><a href="#top">Top</a>',
    )
    assert inspect_published(site)["failure_count"] == 0


def test_junction_directory_is_pruned_before_its_children_are_enumerated(
    site: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import check_published_links as checker

    junction = site / "reference-pages" / "redirect"
    junction.mkdir()
    (junction / "not-public.html").write_bytes(b"\xff")
    real_check = is_content_link
    real_walk = os.walk
    visited: list[Path] = []
    monkeypatch.setattr(
        checker, "is_content_link", lambda path: path == junction or real_check(path)
    )

    def walk(directory: Path, *, followlinks: bool) -> Iterator[tuple[str, list[str], list[str]]]:
        assert followlinks is False
        for current, names, files in real_walk(directory, followlinks=followlinks):
            visited.append(Path(current))
            assert not Path(current).is_relative_to(junction)
            yield current, names, files

    monkeypatch.setattr(os, "walk", walk)
    report = checker.inspect_published(site)
    assert junction not in visited
    assert report["failures"] == [
        {
            "path": "reference-pages/redirect",
            "line": 0,
            "kind": "linked_published_source",
            "target": "",
        }
    ]


def test_junction_at_publication_root_is_not_walked(
    site: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import check_published_links as checker

    junction = site / "lesson-pages"
    real_check = is_content_link
    real_walk = os.walk
    monkeypatch.setattr(
        checker, "is_content_link", lambda path: path == junction or real_check(path)
    )

    def walk(directory: Path, *, followlinks: bool) -> Iterator[tuple[str, list[str], list[str]]]:
        assert directory != junction
        yield from real_walk(directory, followlinks=followlinks)

    monkeypatch.setattr(os, "walk", walk)
    report = checker.inspect_published(site)
    assert any(
        failure["path"] == "lesson-pages" and failure["kind"] == "linked_published_source"
        for failure in report["failures"]
    )


def test_linked_asset_ancestor_is_checked_before_file_stat_or_read(
    site: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import check_published_links as checker

    junction = site / "src"
    real_check = is_content_link
    real_is_file = Path.is_file

    def check(path: Path) -> bool:
        assert path == junction or not path.is_relative_to(junction)
        return path == junction or real_check(path)

    def is_file(path: Path) -> bool:
        assert not path.is_relative_to(junction)
        return real_is_file(path)

    monkeypatch.setattr(checker, "is_content_link", check)
    monkeypatch.setattr(Path, "is_file", is_file)
    report = checker.inspect_published(site)
    assert report["html_pages_checked"] == 3
    assert {failure["path"] for failure in report["failures"]} == {
        "src/ds60sqlpy/assets/classroom.html",
        *ASSETS.values(),
    }
    assert all(failure["kind"] == "linked_published_source" for failure in report["failures"])
