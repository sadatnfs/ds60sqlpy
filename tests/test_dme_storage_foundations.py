"""Independent storage, version, analytical-grain and provenance oracles."""

from __future__ import annotations

import importlib.util
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROGRAMS = ROOT / "courses/data-ml-engineering/authoring/foundations/examples"


def reference(number: int) -> ModuleType:
    dependency = {26: "duckdb", 27: "pyarrow", 28: "duckdb", 30: "duckdb", 32: "duckdb"}.get(number)
    if dependency:
        pytest.importorskip(dependency, reason="Prepared data-engineering runtime required")
    name = f"dme_storage_{number}"
    spec = importlib.util.spec_from_file_location(name, PROGRAMS / f"dme-{number:03}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("number", range(25, 33))
def test_complete_storage_examples(number: int) -> None:
    module = reference(number)
    assert isinstance(module.example_one(), dict)
    assert isinstance(module.example_two(), dict)


def test_actual_local_cas_allows_only_one_writer_for_a_generation() -> None:
    module = reference(25)
    store = module.Store()
    generation = store.put("current", b"baseline", None)

    def publish(value: int) -> str:
        try:
            store.put("current", str(value).encode(), generation)
            return "accepted"
        except module.Conflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = list(pool.map(publish, range(8)))
    assert outcomes.count("accepted") == 1 and outcomes.count("conflict") == 7
    assert store.get("current", generation)[1] == b"baseline"


def test_manifest_checks_dataset_grain_population_and_removed_fields(tmp_path: Path) -> None:
    module = reference(26)
    one = module.write_file(
        tmp_path, "one", module.pa.table({"delivery_id": ["A"], "packages": [2]})
    )
    duplicate = module.write_file(
        tmp_path, "two", module.pa.table({"delivery_id": ["A"], "packages": [3]})
    )
    with pytest.raises(ValueError, match="unique"):
        module.read_manifest(tmp_path, [one, duplicate])
    with pytest.raises(ValueError, match="Repeated"):
        module.read_manifest(tmp_path, [one, one])
    with pytest.raises(ValueError, match="population"):
        module.read_manifest(tmp_path, [{**one, "rows": 2}])
    missing = module.write_file(tmp_path, "missing", module.pa.table({"delivery_id": ["B"]}))
    with pytest.raises(ValueError, match="removed"):
        module.read_manifest(tmp_path, [missing])


def test_snapshot_conflict_is_visible_across_independent_catalog_connections(
    tmp_path: Path,
) -> None:
    module = reference(27)
    path = tmp_path / "catalog.db"
    first, second = module.catalog(path), module.catalog(path)
    try:
        original = module.data_file(tmp_path, "initial", [{"id": "A", "packages": 2}])
        module.commit(first, tmp_path, 1, 0, [original], [])
        replacement = module.data_file(tmp_path, "candidate", [{"id": "B", "packages": 3}])
        module.commit(first, tmp_path, 2, 1, [original, replacement], [])
        with pytest.raises(ValueError, match="parent changed"):
            module.commit(second, tmp_path, 3, 1, [original], ["A"])
        assert module.read_snapshot(second, tmp_path, 1) == {"A": 2}
        assert module.read_snapshot(second, tmp_path, 2) == {"A": 2, "B": 3}
        assert second.execute("select count(*) from snapshots").fetchone() == (2,)
    finally:
        first.close()
        second.close()


def test_registered_catalog_candidate_cannot_bypass_required_grain() -> None:
    module = reference(28)
    with module.database() as connection:
        module.register(connection, 1, module.CONTRACT, "a" * 64)
        module.activate(connection, 1, "curator", 0)
        module.register(connection, 2, {**module.CONTRACT, "grain": ["region"]}, "b" * 64)
        with pytest.raises(ValueError, match="consumer contract"):
            module.activate(connection, 2, "curator", 1)
        assert module.resolve(connection, "analyst")["version"] == 1
        with pytest.raises(PermissionError):
            module.authorize(connection, "unlisted-resource", "curator", "publish")


def test_replica_model_exposes_ambiguity_instead_of_inventing_a_cassandra_tie_rule() -> None:
    module = reference(29)
    with pytest.raises(ValueError, match="equal-clock"):
        module.latest([(2, "live", 4), (2, "deleted", None)])
    assert module.latest([None, (3, "deleted", None), (1, "live", 100)]) == (3, "deleted", None)
    assert module.example_one()["all_days_query_partition_fanout"] == 3


def test_current_entity_resolution_precedes_status_filtering() -> None:
    module = reference(30)
    rows = [
        ("A", 1, "north", 2, "paid"),
        ("B", 1, "north", 3, "paid"),
        ("A", 2, "north", 2, "cancelled"),
    ]
    with module.duckdb.connect(":memory:") as connection:
        module.current_rows(connection, rows)
        assert connection.execute(
            "select sum(packages) from current where status='paid'"
        ).fetchone() == (3,)
        assert connection.execute(
            "select sum(packages) from events where status='paid'"
        ).fetchone() == (5,)
    with module.duckdb.connect(":memory:") as connection:
        with pytest.raises(ValueError, match="conflicting"):
            module.current_rows(connection, [rows[0], ("A", 1, "south", 100, "paid")])
        assert connection.execute("select count(*) from information_schema.tables").fetchone() == (
            0,
        )


def test_lineage_detects_changed_artifact_recipe_and_implementation(tmp_path: Path) -> None:
    module = reference(31)
    ledger = module.build(tmp_path)
    (tmp_path / "totals.json").write_text('{"north":999}')
    result = module.invalidated(tmp_path, ledger)
    assert result["direct"] == ["totals"] and result["affected"] == ["report", "totals"]
    (tmp_path / "totals.json").write_text('{"north":5,"south":1}')
    assert module.invalidated(tmp_path, ledger)["affected"] == []
    ledger["clean"]["recipe"]["implementation_sha256"] = "0" * 64
    result = module.invalidated(tmp_path, ledger)
    assert result["direct"] == ["clean"] and result["affected"] == ["clean", "report", "totals"]


@pytest.mark.parametrize("number", [29, 32])
def test_required_table_and_report_outputs_are_native_validated(
    number: int, tmp_path: Path
) -> None:
    from ds60sqlpy.plot_artifacts import output_directory, validate_artifacts

    with output_directory(tmp_path):
        reference(number).main()
    artifacts = validate_artifacts(json.loads((tmp_path / "ds60-figures.json").read_text()))
    assert [item["kind"] for item in artifacts] == ["table", "json"]
    assert all(item["description"] for item in artifacts)
    if number == 29:
        assert sum(row[2] for row in artifacts[0]["table"]["rows"]) == 14
    else:
        assert artifacts[0]["table"]["rows"] == [["north", "20s", 2, 5]]
        assert artifacts[1]["data"]["retention_audit"] == {
            "cutoff_inclusive": "2024-01-04",
            "before": 4,
            "after": 3,
            "removed": 1,
        }
