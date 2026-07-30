"""Tests for the BRIDGE-ANALYTICS-01 local analytics project."""

from __future__ import annotations

import inspect
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from bridge.professional.lessons import bridge_analytics_01_local_project as learner
from bridge.professional.solutions import (
    bridge_analytics_01_local_project_solution as solution,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
GUIDE_PATH = (
    REPOSITORY_ROOT
    / "bridge"
    / "professional"
    / "companion-guides"
    / "bridge_analytics_01_local_project.md"
)
REQUIRED_GUIDE_HEADINGS = (
    "## Level and prerequisites",
    "## Learning objectives",
    "## Vocabulary and concepts",
    "## Worked example / walkthrough",
    "## Exercises",
    "## Self-check",
    "## Common pitfalls",
    "## Next step",
)


def test_learner_stays_answer_free_and_guide_has_required_structure() -> None:
    learner_source = inspect.getsource(learner)
    assert "professional.solutions" not in learner_source
    assert learner_source.count("NotImplementedError") >= 6
    assert learner.LESSON_ID == "bridge-analytics-01"

    guide = GUIDE_PATH.read_text(encoding="utf-8")
    positions = [guide.index(heading) for heading in REQUIRED_GUIDE_HEADINGS]
    assert positions == sorted(positions)


@pytest.mark.parametrize(
    ("rows", "expected_exception", "message"),
    (
        (((1, "Ada"),), ValueError, "expected 3"),
        (((None, "Ada", "enterprise"),), ValueError, "cannot be null"),
        ((("1", "Ada", "enterprise"),), TypeError, "invalid Python type"),
        (
            (
                (1, "Ada", "enterprise"),
                (1, "Ada again", "small_business"),
            ),
            ValueError,
            "declared grain",
        ),
    ),
)
def test_producer_contract_rejects_bad_rows(
    rows: tuple[tuple[object, ...], ...],
    expected_exception: type[Exception],
    message: str,
) -> None:
    contract = solution.PRODUCER_CONTRACTS[0]
    with pytest.raises(expected_exception, match=message):
        solution.validate_producer_rows(contract, rows)


def test_model_dag_is_deterministic_and_rejects_invalid_graphs() -> None:
    ordered = solution.topological_order(
        solution.MODELS,
        source_names=solution.SOURCE_NAMES,
    )
    assert tuple(model.name for model in ordered) == (
        "stg_customers",
        "stg_order_items",
        "stg_orders",
        "int_order_revenue",
        "mart_daily_revenue",
    )

    missing = solution.ModelSpec(
        "model_with_missing_source",
        "staging",
        "one row per id",
        ("raw_missing",),
        "SELECT 1 AS id",
    )
    with pytest.raises(ValueError, match="missing dependencies"):
        solution.topological_order((missing,), source_names=frozenset())

    model_a = solution.ModelSpec(
        "model_a",
        "intermediate",
        "one row per id",
        ("model_b",),
        "SELECT * FROM model_b",
    )
    model_b = solution.ModelSpec(
        "model_b",
        "intermediate",
        "one row per id",
        ("model_a",),
        "SELECT * FROM model_a",
    )
    with pytest.raises(ValueError, match="cycle"):
        solution.topological_order(
            (model_a, model_b),
            source_names=frozenset(),
        )


def test_metric_definition_records_grain_calculation_and_exclusions() -> None:
    metric = solution.GROSS_REVENUE_METRIC
    assert metric.model_name == "mart_daily_revenue"
    assert metric.expression == "gross_revenue"
    assert metric.aggregation == "sum"
    assert metric.time_dimension == "order_date"
    assert "quantity times unit price" in metric.description
    assert "cancelled and placed orders are excluded" in metric.description


def test_local_project_is_correct_tested_and_idempotent() -> None:
    connection = solution.open_memory_duckdb()
    try:
        first = solution.run_project(connection)
        second = solution.run_project(connection)
    finally:
        connection.close()

    assert first == second
    assert first.build_order == (
        "stg_customers",
        "stg_order_items",
        "stg_orders",
        "int_order_revenue",
        "mart_daily_revenue",
    )
    assert all(result.violation_count == 0 for result in first.test_results)
    assert first.mart_rows == (
        (date(2026, 1, 1), Decimal("37.50"), 2, 1),
        (date(2026, 1, 2), Decimal("21.75"), 1, 1),
    )


def test_data_tests_and_reconciliation_detect_corruption() -> None:
    connection = solution.open_memory_duckdb()
    try:
        solution.run_project(connection)
        connection.execute(
            """
INSERT INTO mart_daily_revenue
SELECT *
FROM mart_daily_revenue
ORDER BY order_date
LIMIT 1
"""
        )
        results = solution.run_data_tests(connection, solution.DATA_TESTS)
        violations = {result.name: result.violation_count for result in results}
        assert violations["mart_daily_grain"] == 1

        solution.run_project(connection)
        connection.execute(
            """
UPDATE mart_daily_revenue
SET gross_revenue = gross_revenue + 1
WHERE order_date = DATE '2026-01-01'
"""
        )
        with pytest.raises(AssertionError, match="reconciliation failed"):
            solution.reconcile_mart(connection)
    finally:
        connection.close()


def test_table_contract_detects_column_drift() -> None:
    connection = solution.open_memory_duckdb()
    try:
        solution.run_project(connection)
        connection.execute(
            """
CREATE OR REPLACE TABLE mart_daily_revenue AS
SELECT
    order_date AS event_date,
    gross_revenue,
    order_count,
    customer_count
FROM mart_daily_revenue
"""
        )
        with pytest.raises(ValueError, match="column drift"):
            solution.validate_table_contract(connection, solution.MART_CONTRACT)
    finally:
        connection.close()


def test_solution_uses_only_local_in_memory_execution(capsys: pytest.CaptureFixture[str]) -> None:
    source = inspect.getsource(solution)
    lowered = source.lower()
    assert 'database=":memory:"' in source
    assert ".duckdb" not in lowered
    assert "http://" not in lowered
    assert "https://" not in lowered
    assert "api_key" not in lowered
    assert "password=" not in lowered

    assert solution.main() == 0
    output = capsys.readouterr().out
    assert "models=5" in output
    assert "tests=6" in output
    assert "mart_rows=2" in output
    assert "idempotent=True" in output
