"""Independent request, time, monitoring, access and migration invariants."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROGRAMS = ROOT / "courses/data-ml-engineering/authoring/foundations/examples"


def reference(number: int) -> ModuleType:
    if number in {41, 42}:
        pytest.importorskip("fastapi", reason="Prepared data-engineering runtime required")
    name = f"dme_operations_{number}"
    spec = importlib.util.spec_from_file_location(name, PROGRAMS / f"dme-{number:03}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("number", range(41, 49))
def test_complete_operations_examples(number: int) -> None:
    module = reference(number)
    assert isinstance(module.example_one(), dict)
    assert isinstance(module.example_two(), dict)


def test_fresh_arrival_cannot_make_an_old_observation_fresh() -> None:
    module = reference(41)
    model = module.trained_model()
    valid = module.fixture()[0]
    assert module.score(model, [{**valid, "event_hour": 24, "known_hour": 48}])
    for changed in [
        {**valid, "event_hour": 23, "known_hour": 48},
        {**valid, "event_hour": 47, "known_hour": 46},
        {**valid, "event_hour": 48, "known_hour": 49},
    ]:
        with pytest.raises(ValueError, match="known by decision"):
            module.score(model, [changed])
    with pytest.raises(ValueError, match="uniquely"):
        module.score(model, [valid, valid])


def test_cancellation_cleanup_and_effect_reconciliation_are_repeatable() -> None:
    module = reference(42)
    for _ in range(3):
        assert module.example_one()["active_after_cleanup"] == 0
        result = module.example_two()
        assert result["retry"] == {"outcome": "replayed", "accepted_total": 3}
        assert result["conflicting_retry_status"] == 409


def test_latency_failure_overlap_counts_each_request_once() -> None:
    module = reference(43)
    rows = [
        {"eligible": True, "status": 503, "latency_ms": 300},
        {"eligible": True, "status": 200, "latency_ms": 300},
        {"eligible": True, "status": 200, "latency_ms": 100},
        {"eligible": False, "status": 400, "latency_ms": 1},
    ]
    summary = module.indicators(rows)
    assert summary == {"eligible": 3, "excluded": 1, "available": 2, "timely_success": 1, "bad": 2}
    assert module.burn(summary, Fraction(1, 2)) == Fraction(4, 3)
    with pytest.raises(ValueError, match="empty"):
        module.indicators([])
    with pytest.raises(ValueError, match="positive error budget"):
        module.burn(summary, Fraction(1))


def test_label_boundary_retains_false_and_missing_without_immature_leakage() -> None:
    module = reference(44)
    predictions = [
        {"id": "A", "decision_day": 7, "probability": 0.2},
        {"id": "B", "decision_day": 7, "probability": 0.8},
        {"id": "C", "decision_day": 8, "probability": 0.8},
    ]
    labels = [
        {"id": "A", "known_day": 10, "outcome": False},
        {"id": "B", "known_day": 11, "outcome": True},
        {"id": "C", "known_day": 9, "outcome": True},
    ]
    result = module.evaluate(predictions, labels, 10, 3)
    assert (
        result["eligible"],
        result["labelled"],
        result["coverage"],
        result["accuracy_observed"],
    ) == (2, 1, 0.5, 1.0)
    assert result["population"][1]["outcome"] is None
    assert module.evaluate(predictions, [], 1, 3)["accuracy_observed"] is None
    assert module.total_variation(["a"], ["b"]) == 1


def test_file_boundary_rejects_ambiguous_json_oversize_and_unauthorized_role(
    tmp_path: Path,
) -> None:
    module = reference(45)
    principal = module.Principal("fixture", "north", frozenset({"analyst"}))
    (tmp_path / "a.json").write_text('{"packages":1,"packages":2}')
    with pytest.raises(ValueError, match="Duplicated"):
        module.read_report(tmp_path, principal, "report-a")
    (tmp_path / "a.json").write_text(" " * 5000)
    with pytest.raises(ValueError, match="bounded"):
        module.read_report(tmp_path, principal, "report-a")
    with pytest.raises(PermissionError):
        module.read_report(tmp_path, module.Principal("fixture", "north", frozenset()), "report-a")


def test_queue_model_matches_hand_schedule_and_rejects_nonfinite_demand() -> None:
    module = reference(46)
    records = module.schedule([0, 0, 0.1], 0.2, 2)
    assert [row["start"] for row in records] == [0.0, 0.0, 0.2]
    assert [row["finish"] for row in records] == [0.2, 0.2, 0.4]
    assert math.isclose(records[2]["waiting"], 0.1)
    assert math.isclose(records[2]["latency"], 0.3)
    with pytest.raises(ValueError):
        module.schedule([float("nan")], 0.1, 2)
    with pytest.raises(ValueError):
        module.schedule([0], 0.1, 0)


def test_failed_half_open_probe_reopens_without_extra_attempts() -> None:
    module = reference(47)
    breaker = module.Breaker()
    assert breaker.request(0, lambda: False) == "fallback"
    assert breaker.request(1, lambda: False) == "fallback"
    assert breaker.calls == 3 and breaker.state == "open"
    assert breaker.request(6, lambda: False) == "fallback"
    assert breaker.calls == 4 and breaker.opened_at == 6
    assert breaker.request(7, lambda: True) == "fallback" and breaker.calls == 4
    assert breaker.request(11, lambda: True) == "live" and breaker.calls == 5
    with pytest.raises(ValueError, match="monotone"):
        breaker.request(10, lambda: True)


def test_reader_activation_rejects_partial_backfill_and_stale_rollback() -> None:
    module = reference(48)
    connection = module.database()
    try:
        original = module.read(connection, 1)
        module.expand(connection)
        with connection:
            connection.execute("update deliveries set region='north' where id='A'")
        with pytest.raises(ValueError, match="complete"):
            module.activate(connection, 2, 1)
        assert connection.execute("select reader from deployment").fetchone() == (1,)
        module.fill_regions(connection)
        module.activate(connection, 2, 1)
        with pytest.raises(ValueError, match="version changed"):
            module.activate(connection, 1, 1)
        assert connection.execute("select reader from deployment").fetchone() == (2,)
        assert module.activate(connection, 1, 2) == original
    finally:
        connection.close()


@pytest.mark.parametrize("number", [41, 43, 44, 46])
def test_operations_result_contracts_publish_exact_bounded_outputs(
    number: int, tmp_path: Path
) -> None:
    from ds60sqlpy.plot_artifacts import output_directory, validate_artifacts

    with output_directory(tmp_path):
        reference(number).main()
    artifacts = validate_artifacts(json.loads((tmp_path / "ds60-figures.json").read_text()))
    assert [item["kind"] for item in artifacts] == ["table", "json"]
    assert all(item["description"] for item in artifacts)
    if number == 44:
        rows = artifacts[0]["table"]["rows"]
        assert len(rows) == 7 and rows[-1][-1] is None
