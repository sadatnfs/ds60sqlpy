"""TMB numerical and artifact contracts, without requiring a host R install."""

import importlib.util
import json
import re
import unittest
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "courses" / "tmb-modeling"


def _reference_tests() -> type[unittest.TestCase]:
    path = COURSE / "projects" / "tmb-local" / "tests" / "test_reference.py"
    spec = importlib.util.spec_from_file_location("tmb_reference_tests", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast(type[unittest.TestCase], module.ReferenceTests)


TestTmbAlgebra = _reference_tests()


def test_tmb_companions_are_complete_and_source_bound() -> None:
    manifest = COURSE / "lessons.json"
    lessons = json.loads(manifest.read_text())["lessons"]
    assert [item["id"] for item in lessons] == [f"tmb-{n:03d}" for n in range(1, 49)]
    for item in lessons:
        guide = (ROOT / item["guide_path"]).read_text()
        source = (ROOT / item["source_path"]).read_text().strip()
        assert source in guide, item["id"]
        assert "Worked case A" in guide and "Worked case B" in guide
        assert item["runtime_profile"] == "r-statistics"
        assert item["verification_id"] is None
        assert "companion run is not a TMB compiler or rpy2 receipt" in guide
        assert "\u2014" not in guide


def test_tmb_dependency_archive_pins_are_explicit() -> None:
    lock = json.loads((COURSE / "projects/tmb-local/dependencies.lock.json").read_text())
    assert lock["r_version"] == "4.6.1"
    assert lock["framework"] == "CppAD"
    assert {p["name"] for p in lock["packages"]} == {"TMB", "RcppEigen"}
    for package in lock["packages"]:
        assert re.fullmatch(r"[a-f0-9]{64}", package["sha256"])
        assert package["url"].startswith("https://cran.r-project.org/src/contrib/")
        assert package["license"]


def test_tmb_public_api_inventory_has_complete_pinned_surface() -> None:
    inventory = json.loads((COURSE / "api-inventory.json").read_text())
    entries = {item["name"]: item for item in inventory["entries"]}
    assert len(inventory["explicit_exports"]) == 30
    assert len(inventory["registered_s3_methods"]) == 9
    assert set(inventory["explicit_exports"]) | set(inventory["registered_s3_methods"]) <= set(
        entries
    )
    assert entries["GK"]["status"] == "documented-not-exported"
    assert entries["as.list.sdreport"]["status"] == "registered-s3"
    assert entries["confint.tmbprofile"]["status"] == "registered-s3"
    for entry in entries.values():
        assert (COURSE / "guides" / f"{entry['chapter_id']}.md").is_file()
        assert entry["signature"].startswith(entry["name"] + "(")
        assert entry["typical_use"] and entry["cautions"]


def test_tmb_runtime_export_fixture_matches_canonical_inventory() -> None:
    canonical = json.loads((COURSE / "api-inventory.json").read_text())
    runtime = json.loads((COURSE / "projects/tmb-local/tests/public_api_exports.json").read_text())
    assert runtime["explicit_exports"] == canonical["explicit_exports"]
    assert runtime["namespace_sha256"] == canonical["namespace_sha256"]


def test_tmb_cpp_authoring_families_have_chapters_and_source_provenance() -> None:
    inventory = json.loads((COURSE / "cpp-api-families.json").read_text())
    assert inventory["tmb_version"] == "1.9.25"
    assert len(inventory["families"]) == 10
    symbols = {symbol for family in inventory["families"] for symbol in family["symbols"]}
    assert {
        "DATA_ARRAY",
        "PARAMETER_ARRAY",
        "density::GMRF",
        "density::SEPARABLE",
        "density::VECSCALE",
        "TMB_ATOMIC_VECTOR_FUNCTION",
    } <= symbols
    for digest in inventory["source_header_sha256"].values():
        assert re.fullmatch(r"[a-f0-9]{64}", digest)
    for family in inventory["families"]:
        for chapter_id in family["chapters"]:
            assert (COURSE / "guides" / f"{chapter_id}.md").is_file()
    assert len(list((COURSE / "projects/tmb-cpp-api/models").glob("*.cpp"))) == 5
