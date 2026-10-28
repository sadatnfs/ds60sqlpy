"""Independent complete-product, replay, ML, restore, migration and evidence contracts."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROGRAMS = ROOT / "courses/data-ml-engineering/authoring/foundations/examples"


@pytest.fixture(autouse=True)
def offline_tracking(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in {
        "FEAST_USAGE": "False",
        "MLFLOW_ENABLE_TELEMETRY": "false",
        "MLFLOW_DISABLE_AGENT_HINT": "1",
        "DO_NOT_TRACK": "true",
    }.items():
        monkeypatch.setenv(key, value)


def reference(number: int) -> ModuleType:
    for dependency in {
        49: ["polars", "duckdb"],
        51: ["feast", "mlflow", "skops"],
        53: ["pyarrow"],
    }.get(number, []):
        pytest.importorskip(dependency, reason="Prepared data-engineering runtime required")
    name = f"dme_capstone_{number}"
    spec = importlib.util.spec_from_file_location(name, PROGRAMS / f"dme-{number:03}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("number", range(49, 57))
def test_complete_capstone_cases(number: int) -> None:
    module = reference(number)
    assert isinstance(module.example_one(), dict)
    assert isinstance(module.example_two(), dict)


def test_product_replay_preserves_bytes_and_duplicate_grain_cannot_publish(tmp_path: Path) -> None:
    module = reference(49)
    source = tmp_path / "input.csv"
    module.fixture(source)
    root = tmp_path / "product"
    first = module.publish(root, source, 3)
    path = root / "versions" / first["version"] / "summary.parquet"
    before = path.read_bytes()
    assert module.publish(root, source, 3)["replayed"]
    assert path.read_bytes() == before
    source.write_text("delivery_id,route,packages\nA,10,2\nA,10,3\n")
    rejected = module.publish(root, source, 2)
    assert not rejected["accepted"] and rejected["duplicated_identity"]
    assert module.current(root)["version"] == first["version"]
    path.write_bytes(b"changed-owned-artifact")
    with pytest.raises(ValueError, match="content changed"):
        module.current(root)


def test_event_log_rejects_conflicting_old_revision_even_after_newer_state(tmp_path: Path) -> None:
    module = reference(50)
    connection = module.database(tmp_path / "events.db")
    try:
        module.apply(connection, [*module.fixture(), ("A2", "A", 2, 20, 4)])
        before = module.totals(connection)
        with pytest.raises(ValueError, match="Historical entity revision"):
            module.apply(connection, [("different-source-id", "A", 1, 10, 999)])
        assert module.totals(connection) == before == {10: 3, 20: 5}
        assert connection.execute("select count(*) from events").fetchone() == (4,)
    finally:
        connection.close()


def test_actual_feast_offline_and_online_paths_exclude_future_known_correction(
    tmp_path: Path,
) -> None:
    module = reference(51)
    store, rows = module.feature_store(tmp_path)
    try:
        assert rows.request_id.tolist() == list(range(40))
        assert rows.signal.tolist() == [float(n % 20) + (0.25 if n >= 20 else 0) for n in range(40)]
        online = store.get_online_features(
            features=["serving_signal:signal"],
            entity_rows=[{"account_id": 0}, {"account_id": 39}, {"account_id": 999}],
        ).to_dict()
        keyed = dict(zip(online["account_id"], online["signal"], strict=True))
        assert keyed == {0: 0.0, 39: 19.25, 999: None}
    finally:
        store.teardown()


def test_backup_restore_refuses_existing_destination_and_wrong_population(tmp_path: Path) -> None:
    module = reference(52)
    source = module.database(tmp_path / "source.db")
    try:
        with source:
            source.execute("insert into events values('A',2,1)")
        manifest = module.backup(source, tmp_path / "backup.db", 1)
        target = tmp_path / "protected.db"
        target.write_bytes(b"existing-owned-state")
        with pytest.raises(ValueError, match="nonempty"):
            module.restore(tmp_path / "backup.db", manifest, target)
        assert target.read_bytes() == b"existing-owned-state"
        with pytest.raises(ValueError, match="population"):
            module.restore(
                tmp_path / "backup.db", {**manifest, "row_count": 2}, tmp_path / "wrong.db"
            )
        assert not (tmp_path / "wrong.db").exists()
    finally:
        source.close()


def test_migration_rejects_changed_currency_even_when_total_matches(tmp_path: Path) -> None:
    module = reference(53)
    source = module.fixture(tmp_path)
    original = module.accepted(tmp_path)
    path = module.candidate(
        tmp_path, "currencychange", [{**row, "currency": "EUR"} for row in original]
    )
    with pytest.raises(ValueError, match="currency"):
        module.activate(tmp_path, source, path)
    assert module.accepted(tmp_path) == original
    source.write_text("order_id,amount_usd\n001,1.999\n")
    with pytest.raises(ValueError, match="exact USD cents"):
        module.old_reader(source)


def test_actual_child_validation_failure_preserves_prior_state_and_stale_rollback_fails(
    tmp_path: Path,
) -> None:
    module = reference(54)
    module.initialize(tmp_path)
    attempt = module.run_worker(tmp_path, claimed_total=900)
    assert attempt["returncode"] == 23
    assert module.inspect(tmp_path) == {"accepted": (1, 6), "receipt": None, "products": [(1, 6)]}
    with pytest.raises(ValueError, match="precondition"):
        module.rollback(tmp_path, expected=2, target=1, reason="stale fixture operation")
    assert module.inspect(tmp_path)["accepted"] == (1, 6)


def test_design_choice_changes_only_when_the_constraint_changes() -> None:
    module = reference(55)
    requirements = {
        "freshness_minutes": 2,
        "latency_ms": 500,
        "retention_days": 7,
        "cost_units": 100,
    }
    assert module.choose(module.proposals(), requirements)["selected"] == "online"
    assert (
        module.choose(module.proposals(), requirements, require_qualification=True)["selected"]
        is None
    )


def test_evidence_invalidates_changed_input_even_with_identical_source(tmp_path: Path) -> None:
    module = reference(56)
    module.bundle(tmp_path)
    receipt = module.execute(tmp_path)
    (tmp_path / "input.json").write_text("[2,3,4]")
    with pytest.raises(ValueError, match="different source or input"):
        module.validate_claim(tmp_path, receipt, "bounded-local-correctness")
    updated = module.execute(tmp_path)
    assert updated["observed"] == {"rows": 3, "total": 9}
    assert module.validate_claim(tmp_path, updated, "bounded-local-correctness")


@pytest.mark.parametrize(
    "number,kinds",
    [
        (49, ["table", "json"]),
        (51, ["table", "json"]),
        (55, ["table", "json"]),
        (56, ["json", "json"]),
    ],
)
def test_capstone_outputs_are_native_validated(
    number: int, kinds: list[str], tmp_path: Path
) -> None:
    from ds60sqlpy.plot_artifacts import output_directory, validate_artifacts

    with output_directory(tmp_path):
        reference(number).main()
    artifacts = validate_artifacts(json.loads((tmp_path / "ds60-figures.json").read_text()))
    assert [item["kind"] for item in artifacts] == kinds
    assert all(item["description"] for item in artifacts)
