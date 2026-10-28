"""Independent ingestion, time, representation and publication oracles."""

from __future__ import annotations

import importlib.util
import json
from concurrent.futures import ThreadPoolExecutor
from itertools import permutations
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROGRAMS = ROOT / "courses/data-ml-engineering/authoring/foundations/examples"


def reference(number: int) -> ModuleType:
    dependency = {9: "duckdb", 10: "fastapi", 12: "duckdb", 13: "pyarrow", 16: "polars"}.get(number)
    if dependency:
        pytest.importorskip(dependency, reason="Prepared data-engineering runtime required")
    spec = importlib.util.spec_from_file_location(
        f"dme_ingestion_{number}", PROGRAMS / f"dme-{number:03}.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("number", range(9, 17))
def test_complete_ingestion_examples(number: int) -> None:
    module = reference(number)
    assert isinstance(module.example_one(), dict)
    assert isinstance(module.example_two(), dict)


def test_empty_delivery_and_conflicting_batch_identity(tmp_path: Path) -> None:
    module = reference(9)
    path = tmp_path / "delivery.csv"
    with module.database() as connection:
        empty = module.delivery(path, "empty", "delivery_id,route_id,packages\n", 0)
        assert module.ingest(connection, path, empty) == "accepted"
        assert module.ingest(connection, path, empty) == "already-applied"
        assert connection.execute("select count(*) from deliveries").fetchone() == (0,)
        changed = module.delivery(path, "empty", "delivery_id,route_id,packages\nA,10,2\n", 1)
        with pytest.raises(ValueError, match="different input"):
            module.ingest(connection, path, changed)
        assert connection.execute("select count(*) from deliveries").fetchone() == (0,)


def test_ingestion_read_is_bounded_and_failed_batch_is_atomic(tmp_path: Path) -> None:
    module = reference(9)
    path = tmp_path / "delivery.csv"
    with module.database() as connection:
        manifest = module.delivery(path, "large", "x" * 5000, 0)
        with pytest.raises(ValueError, match="bounded manifest"):
            module.ingest(connection, path, manifest)
        assert connection.execute("select count(*) from batches").fetchone() == (0,)
    assert module.example_two()["retained_accepted_ids"] == [("A",), ("B",), ("C",)]


def test_actual_asgi_idempotency_under_concurrent_requests() -> None:
    module = reference(10)
    app, state = module.application()
    with module.TestClient(app) as client:

        def create(_: int) -> int:
            return int(
                client.post(
                    "/deliveries",
                    json={"delivery_id": "D", "packages": 4},
                    headers={"Idempotency-Key": "same-effect"},
                ).status_code
            )

        with ThreadPoolExecutor(max_workers=4) as pool:
            statuses = list(pool.map(create, range(8)))
        assert statuses.count(201) == 1 and statuses.count(200) == 7
        assert state["rows"]["D"] == {"delivery_id": "D", "packages": 4}


def test_version_tombstone_survives_all_arrival_orders() -> None:
    module = reference(11)
    events = [(1, "upsert", 2), (2, "upsert", 5), (3, "delete", None)]
    for order in permutations(events):
        connection = module.database()
        try:
            for version, operation, value in order:
                module.apply_event(connection, "A", version, operation, value)
            assert module.visible(connection) == []
            assert connection.execute("select source_version,deleted from state").fetchall() == [
                (3, 1)
            ]
        finally:
            connection.close()


def test_historical_join_has_independent_cardinality_oracle() -> None:
    result = reference(12).example_two()
    assert result["matches_per_delivery"] == [(1, 2), (2, 2), (3, 1), (4, 0)]
    assert set(map(tuple, result["overlapping_interval_pairs"])) == {
        (10, "north", "east"),
        (10, "east", "west"),
    }
    assert result["publishable"] is False


def test_actual_serialization_outputs_are_json_native_and_distinguish_null(tmp_path: Path) -> None:
    from ds60sqlpy.plot_artifacts import output_directory, validate_artifacts

    module = reference(13)
    with output_directory(tmp_path):
        module.main()
    artifacts = validate_artifacts(json.loads((tmp_path / "ds60-figures.json").read_text()))
    assert [row["kind"] for row in artifacts] == ["table", "json"]
    rows = artifacts[0]["table"]["rows"]
    assert rows[0][0] == "001" and rows[0][3] == "" and rows[1][3] is None
    assert artifacts[1]["data"]["note_validity"] == [True, False]


def test_two_clocks_include_the_boundary_without_confusing_zero_and_unknown() -> None:
    module = reference(14)
    records = [{"event_hour": 2, "known_hour": 3, "value": 0}]
    assert module.select_known(records, 2) is None
    assert module.select_known(records, 3) == 0
    assert module.example_one()["eligible_values"] == [10, 20, 20]
    assert module.example_two()["known_coverage"] == pytest.approx(2 / 3)


def test_failed_activation_cannot_change_the_accepted_pointer(tmp_path: Path) -> None:
    module = reference(15)
    module.prepare_version(tmp_path, "v1", [2, 3, 1])
    module.activate(tmp_path, "v1")
    before = (tmp_path / "current.json").read_bytes()
    module.prepare_version(tmp_path, "v2", [2, 3, 4])
    (tmp_path / "versions/v2/data.json").write_text("[999]")
    with pytest.raises(ValueError, match="digest"):
        module.activate(tmp_path, "v2")
    assert (tmp_path / "current.json").read_bytes() == before
    assert module.current(tmp_path) == {"version": "v1", "rows": 3, "packages": 6}


def test_quality_snapshot_respects_versions_and_schema_not_input_order() -> None:
    module = reference(16)
    baseline = module.fixture()
    expected = module.inspect(baseline)
    assert module.inspect(baseline.reverse())["current"] == expected["current"]
    assert (
        module.inspect(baseline.select(list(reversed(baseline.columns))))["current"]
        == expected["current"]
    )
    assert sum(row["packages"] for row in expected["current"]) == 4 + 3
    wrong_type = baseline.with_columns(module.pl.col("packages").cast(module.pl.Float64))
    with pytest.raises(ValueError, match="typed column schema"):
        module.inspect(wrong_type)
