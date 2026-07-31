from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SQL_ROOT = REPO_ROOT / "sql" / "postgres-60day"


def _solution(day: int) -> str:
    return (SQL_ROOT / "solutions" / f"day{day:02d}_solutions.sql").read_text(encoding="utf-8")


def _learner(day: int) -> str:
    matches = sorted(SQL_ROOT.glob(f"day{day:02d}_*.sql"))
    assert len(matches) == 1, f"expected one learner SQL file for Day {day}, found {matches}"
    return matches[0].read_text(encoding="utf-8")


def _guide(day: int) -> str:
    matches = sorted((SQL_ROOT / "companion-guides").glob(f"day{day:02d}_*.md"))
    assert len(matches) == 1, f"expected one guide for Day {day}, found {matches}"
    return matches[0].read_text(encoding="utf-8")


def _code(source: str) -> str:
    """Return normalized SQL code without comments.

    These tests intentionally do not let an explanatory comment satisfy an
    implementation invariant. They remain formatting-insensitive, however, so
    lesson authors can improve layout and prose without rewriting the tests.
    """

    without_block_comments = re.sub(r"/\*.*?\*/", " ", source, flags=re.DOTALL)
    without_line_comments = re.sub(r"--[^\n]*", " ", without_block_comments)
    return re.sub(r"\s+", " ", without_line_comments).strip().lower()


def _exercise(source: str, number: int) -> str:
    match = re.search(
        rf"^-- Exercise {number}\b.*?(?=^-- Exercise [1-9][0-9]*\b|\Z)",
        source,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"solution SQL is missing Exercise {number}"
    return match.group(0)


def _view_body(source: str, view_name: str) -> str:
    code = _code(source)
    match = re.search(
        rf"\bcreate\s+(?:or\s+replace\s+)?view\s+{re.escape(view_name)}\s+as\s+"
        rf"(?P<body>.*?);",
        code,
    )
    assert match is not None, f"missing CREATE VIEW statement for {view_name}"
    return match.group("body")


def test_day41_cube_exposes_all_four_grouping_levels_and_documents_the_mask() -> None:
    solution = _code(_solution(41))
    guide = _guide(41).lower()

    assert re.search(r"\bgroup\s+by\s+cube\s*\(\s*country\s*,\s*category\s*\)", solution)
    assert re.search(
        r"\bgrouping\s*\(\s*country\s*,\s*category\s*\)\s+as\s+grouping_mask",
        solution,
    )

    # PostgreSQL packs GROUPING arguments right-to-left into a bit mask.
    # With (country, category), the precise meanings below prevent learners
    # from mistaking subtotal rows for ordinary NULL dimension values.
    expected_meanings = {
        0: "detail",
        1: "country subtotal",
        2: "category subtotal",
        3: "grand total",
    }
    for mask, meaning in expected_meanings.items():
        assert re.search(
            rf"(?:`{mask}`|\b{mask}\b).{{0,80}}{re.escape(meaning)}",
            guide,
            flags=re.DOTALL,
        ), f"Day 41 guide must explain grouping_mask {mask} as {meaning}"


def test_day44_monitoring_solution_is_read_only_and_preserves_statement_identity() -> None:
    solution = _code(_solution(44))

    for dangerous_function in ("pg_cancel_backend", "pg_terminate_backend"):
        assert dangerous_function not in solution

    table = re.search(
        r"create\s+temp(?:orary)?\s+table\s+top_statement_stats\s*\((?P<body>.*?)\)\s*;",
        solution,
    )
    assert table is not None
    table_body = table.group("body")
    for identity_column in ("ranking", "rank_position", "userid", "dbid", "toplevel", "queryid"):
        assert re.search(rf"\b{identity_column}\b", table_body), (
            "Day 44's temporary result must retain the stable "
            f"(ranking, userid, dbid, toplevel, queryid) identity and {identity_column}"
        )

    assert "from public.pg_stat_statements" in solution
    assert re.search(r"order\s+by\s+ranking\s*,\s*rank_position", solution), (
        "each ranking must display in its own measured order"
    )


def test_day49_scores_models_only_after_complete_comparable_warmup_windows() -> None:
    solution = _code(_solution(49))

    assert "generate_series" in solution
    assert "month_spine" in solution
    assert "monthly_complete" in solution
    assert re.search(
        r"count\s*\([^)]*\)\s+over\s*\(\s*order\s+by\s+month\s+"
        r"rows\s+between\s+6\s+preceding\s+and\s+1\s+preceding\s*\)"
        r"\s+as\s+ma6_history_rows",
        solution,
    )
    assert re.search(
        r"count\s*\([^)]*\)\s+over\s*\(\s*order\s+by\s+month\s+"
        r"rows\s+between\s+12\s+preceding\s+and\s+1\s+preceding\s*\)"
        r"\s+as\s+ma12_history_rows",
        solution,
    )

    # Comparing models on different warm-up populations is an apples-to-oranges
    # backtest. A named common population must require both full windows.
    assert "common_scoring_rows" in solution
    assert re.search(r"\bma6_history_rows\s*=\s*6\b", solution)
    assert re.search(r"\bma12_history_rows\s*=\s*12\b", solution)
    assert "from common_scoring_rows" in solution


def test_day50_preaggregates_each_fact_table_before_the_budget_join() -> None:
    exercise = _code(_exercise(_solution(50), 6))

    expense_cte = exercise.find("expense_monthly as")
    budget_cte = exercise.find("budget_monthly as")
    full_join = exercise.find("full join")
    if full_join == -1:
        full_join = exercise.find("full outer join")

    assert min(expense_cte, budget_cte, full_join) >= 0
    assert expense_cte < full_join and budget_cte < full_join
    assert re.search(
        r"expense_monthly\s+as\s*\(.*?from\s+expenses\b.*?group\s+by",
        exercise,
    )
    assert re.search(
        r"budget_monthly\s+as\s*\(.*?from\s+budgets\b.*?group\s+by",
        exercise,
    )
    assert not re.search(
        r"from\s+expenses(?:\s+\w+)?\s+full(?:\s+outer)?\s+join\s+budgets\b",
        exercise,
    ), "joining raw expenses to raw budgets multiplies both measures"


def test_day53_replay_compares_against_the_same_staged_desired_state() -> None:
    solution = _code(_solution(53))
    exercise = _code(_exercise(_solution(53), 5))

    assert "desired_customer_state" in solution
    assert re.search(
        r"join\s+desired_customer_state(?:\s+\w+)?\s+"
        r"(?:using\s*\(\s*customer_id\s*\)|on\b)",
        exercise,
    )
    assert "training.customers" not in exercise
    assert "is distinct from" in exercise


def test_day58_deduplicates_validated_rows_before_upsert_and_keeps_invalid_json() -> None:
    solution = _code(_solution(58))
    procedure = re.search(
        r"create\s+or\s+replace\s+procedure\s+ingest_customer_stage_solution\b"
        r"(?P<body>.*?)\bcall\s+ingest_customer_stage_solution\b",
        solution,
    )
    assert procedure is not None
    procedure_body = procedure.group("body")

    deduped = procedure_body.find("deduped as")
    upsert = procedure_body.find("insert into customers")
    conflict = procedure_body.find("on conflict")
    assert 0 <= deduped < upsert < conflict
    assert re.search(
        r"insert\s+into\s+customers\b.*?from\s+deduped\b.*?"
        r"(?:winner_rank|source_rank|dedupe_rank)\s*=\s*1\b.*?on\s+conflict",
        procedure_body,
    )

    # Invalid JSON must stay rejectable/quarantinable rather than silently
    # becoming an accepted empty object. IS [NOT] TRUE also catches NULL flags.
    assert re.search(r"\bjson_valid\b", solution)
    assert re.search(r"\bjson_valid\s+is\s+true\b", procedure_body)
    assert re.search(r"\bjson_valid\s+is\s+not\s+true\b", procedure_body)
    for validity_flag in ("email_valid", "country_valid", "phone_valid"):
        assert re.search(rf"\b{validity_flag}\s+is\s+not\s+true\b", procedure_body)


def test_day59_funnel_stages_are_ordered_and_conditioned_on_prior_stages() -> None:
    exercise = _code(_exercise(_solution(59), 2))

    for stage in ("viewed_at", "added_at", "checkout_at", "purchased_at"):
        assert stage in exercise

    # Reaching checkout at any time is not the same as moving through a funnel.
    # The worked answer must require a valid sequence for every later stage.
    ordered_pairs = (
        ("added_at", "viewed_at"),
        ("checkout_at", "added_at"),
        ("purchased_at", "checkout_at"),
    )
    for later, earlier in ordered_pairs:
        assert re.search(rf"\b{later}\s*(?:>=|>)\s*{earlier}\b", exercise), (
            f"Day 59 must condition {later} on {earlier}"
        )

    assert all(
        term in exercise
        for term in (
            "where viewed",
            "where added",
            "where checked_out",
            "where bought",
        )
    )


@pytest.mark.parametrize(
    ("source", "view_name"),
    (
        pytest.param(_learner(60), "v_customer_ltv", id="learner"),
        pytest.param(_solution(60), "v_customer_ltv_solution", id="solution"),
    ),
)
def test_day60_ltv_retains_zero_order_customers_and_uses_header_total_authority(
    source: str,
    view_name: str,
) -> None:
    body = _view_body(source, view_name)

    assert re.search(r"\bfrom\s+customers(?:\s+\w+)?\b", body)
    assert re.search(r"\bleft\s+join\s+orders(?:\s+\w+)?\b", body)
    assert "total_amount" in body
    assert "coalesce" in body
    assert not re.search(r"\bjoin\s+order_items\b", body)


def test_day60_marketing_query_limits_cohorts_and_reports_a_retention_rate() -> None:
    learner = _code(_learner(60))
    marketing = re.search(
        r"\bwith\s+orders_m\s+as\b(?P<body>.*?)\bexplain\b",
        learner,
    )
    assert marketing is not None
    body = marketing.group("body")

    assert re.search(r"\blatest_(?:six|6)(?:_cohorts)?\b", body)
    assert re.search(r"\blimit\s+6\b", body)
    assert "cohort_size" in body
    assert "retention_rate" in body
    assert re.search(r"\bactive_customers\b.*?/\s*nullif\s*\(\s*cohort_size", body)
