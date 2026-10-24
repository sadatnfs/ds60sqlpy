from __future__ import annotations

import json
from pathlib import Path

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.checks import (
    check_bridge,
    check_catalog,
    check_markdown_links,
    check_professional_lessons,
    check_sql_guide_contract,
)


def test_catalog_references_exist() -> None:
    catalog = Catalog.load()
    failures = [result for result in check_catalog(catalog) if result.severity == "fail"]
    assert failures == []


def test_markdown_links_are_not_broken() -> None:
    catalog = Catalog.load()
    failures = [result for result in check_markdown_links(catalog) if result.severity == "fail"]
    assert failures == []


def test_bridge_artifacts_are_complete_and_parse() -> None:
    catalog = Catalog.load()
    failures = [result for result in check_bridge(catalog) if result.severity == "fail"]
    assert failures == []


def test_sql_companion_guides_follow_authoring_contract() -> None:
    catalog = Catalog.load()
    failures = [result for result in check_sql_guide_contract(catalog) if result.severity == "fail"]
    assert failures == []


def test_professional_lessons_follow_shared_contract() -> None:
    catalog = Catalog.load()
    failures = [
        result for result in check_professional_lessons(catalog) if result.severity == "fail"
    ]
    assert failures == []


def test_catalog_is_json() -> None:
    catalog = Catalog.load()
    path = catalog.repo_root / "curriculum" / "catalog.json"
    assert isinstance(json.loads(path.read_text(encoding="utf-8")), dict)


def test_link_check_skips_generated_builds_but_checks_authored_docs(tmp_path: Path) -> None:
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "README.md").write_text("[ignored](missing.md)", encoding="utf-8")
    (tmp_path / "README.md").write_text("[authored](real-missing.md)", encoding="utf-8")
    results = check_markdown_links(Catalog(tmp_path, ()))
    failures = [item for item in results if item.severity == "fail" and item.path is not None]
    assert len(failures) == 1
    assert failures[0].path == "README.md"


@pytest.mark.parametrize("fence", ["```", "~~~", "````"])
def test_markdown_link_checker_ignores_code_but_keeps_real_links(
    tmp_path: Path, fence: str
) -> None:
    source = (
        f"{fence}cpp\n"
        "const auto require = [&checks](bool ok, const char* message) {};\n"
        + ("```\n[still code](not-a-link.md)\n" if fence == "````" else "")
        + f"{fence}\n\n"
        + "Inline `[capture](argument)` and ``[example](literal)`` are code.\n"
        + "[Real broken link](missing.md)\n[Real valid link](exists.md)\n"
        + "[`Code label`](second-missing.md)\n"
    )
    (tmp_path / "README.md").write_text(source, encoding="utf-8")
    (tmp_path / "exists.md").write_text("# Exists\n", encoding="utf-8")
    failures = [r for r in check_markdown_links(Catalog(tmp_path, ())) if r.code == "markdown.link"]
    assert [item.message for item in failures] == [
        "Broken link target: missing.md",
        "Broken link target: second-missing.md",
    ]
