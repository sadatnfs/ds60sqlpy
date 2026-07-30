from __future__ import annotations

import json

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
