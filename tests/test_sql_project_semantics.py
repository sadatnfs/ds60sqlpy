from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SQL_ROOT = REPO_ROOT / "sql" / "postgres-60day"
PROFESSIONAL_SQL_ROOT = REPO_ROOT / "sql" / "professional"


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


def _professional_guide(stem: str) -> str:
    return (PROFESSIONAL_SQL_ROOT / "companion-guides" / f"{stem}.md").read_text(encoding="utf-8")


def _professional_guide_exercise(stem: str, number: int) -> str:
    exercises = _markdown_exercises(_professional_guide(stem))
    match = re.search(
        rf"^{number}\.\s+\*\*.*?(?=^{number + 1}\.\s+\*\*|\Z)",
        exercises,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"{stem} guide is missing Exercise {number}"
    return match.group(0)


def _professional_solution(stem: str) -> str:
    return (PROFESSIONAL_SQL_ROOT / "solutions" / f"{stem}_solutions.sql").read_text(
        encoding="utf-8"
    )


def _professional_migration_fixture(filename: str) -> str:
    return (PROFESSIONAL_SQL_ROOT / "fixtures" / "migrations" / filename).read_text(
        encoding="utf-8"
    )


def _markdown_exercises(source: str) -> str:
    match = re.search(
        r"^## Exercises\b.*?(?=^##\s|\Z)",
        source,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, "professional guide is missing its Exercises section"
    return match.group(0)


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
    assert "object_not_in_prerequisite_state" in solution, (
        "the extension view can exist even when pg_stat_statements was not "
        "loaded through shared_preload_libraries"
    )
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
    parser_function = re.search(
        r"create\s+or\s+replace\s+function\s+pg_temp\."
        r"try_parse_customer_timestamp\b(?P<body>.*?)\$function\$",
        solution,
    )
    assert parser_function is not None
    assert re.search(r"\bstable\b", parser_function.group("body"))
    assert not re.search(r"\bimmutable\b", parser_function.group("body"))

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

    winner_example = _code(_exercise(_solution(58), 4))
    for validity_flag in ("email_valid", "country_valid", "phone_valid", "json_valid"):
        assert re.search(rf"\b{validity_flag}\s+is\s+true\b", winner_example)


def test_day59_funnel_stages_are_ordered_and_conditioned_on_prior_stages() -> None:
    solution = _solution(59)
    headline = solution.split("-- Exercise 1", maxsplit=1)[0]
    exercise = _exercise(solution, 2)

    # Reaching checkout at any time is not the same as moving through a funnel.
    # Check both the headline stakeholder result and the later focused exercise
    # so a correct exercise cannot hide a misleading worked dashboard above it.
    for label, source in (("headline", headline), ("Exercise 2", exercise)):
        code = _code(source)
        for stage in ("viewed_at", "added_at", "checkout_at", "purchased_at"):
            assert stage in code, f"Day 59 {label} is missing {stage}"

        ordered_pairs = (
            ("added_at", "viewed_at"),
            ("checkout_at", "added_at"),
            ("purchased_at", "checkout_at"),
        )
        for later, earlier in ordered_pairs:
            assert re.search(rf"\b{later}\s*(?:>=|>)\s*{earlier}\b", code), (
                f"Day 59 {label} must condition {later} on {earlier}"
            )

        assert all(
            term in code
            for term in (
                "where viewed",
                "where added",
                "where checked_out",
                "where bought",
            )
        )


def test_day59_campaign_attribution_uses_only_declared_marketing_touch_events() -> None:
    exercise = _code(_exercise(_solution(59), 4))

    assert re.search(r"\bevent_type\s+in\s*\(", exercise)
    for event_type in ("page_view", "add_to_cart", "checkout"):
        assert f"'{event_type}'" in exercise


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


PROFESSIONAL_GUIDE_STEMS = (
    "sql_analytics_01_query_patterns",
    "sql_ext_01_extensions_spatial_vector",
    "sql_found_01_relational_design",
    "sql_found_02_versioned_migrations",
    "sql_ops_01_indexes_statistics_maintenance",
    "sql_ops_02_backup_restore_recovery",
    "sql_prog_01_routines_triggers",
    "sql_repl_01_cdc_high_availability",
    "sql_sec_01_roles_privileges_rls",
    "sql_temporal_01_domain_modelling",
    "sql_test_01_contracts_migrations",
    "sql_types_01_native_types_search",
)
PROFESSIONAL_SOLUTION_MARKDOWN = tuple(
    sorted((PROFESSIONAL_SQL_ROOT / "solutions").glob("*_solutions.md"))
)


@pytest.mark.parametrize("stem", PROFESSIONAL_GUIDE_STEMS)
def test_professional_exercise_contracts_do_not_treat_sql_tokens_as_relations(
    stem: str,
) -> None:
    exercises = _markdown_exercises(_professional_guide(stem))
    solution = _code(_professional_solution(stem))
    banned_generated_contracts = (
        "expected output: a completed the",
        "the command tag and an independently counted set of affected",
    )
    banned_source_tokens = {
        "cascade",
        "line",
        "matching",
        "n.status",
        "new.status",
        "of",
        "on",
        "pg_trgm",
        "pg_upgrade",
        "public",
        "skip",
        "to",
        "true",
    }
    bad_sources: list[str] = []
    phantom_relations: list[str] = []

    for line in exercises.splitlines():
        if "**Inputs/evidence:**" not in line:
            continue
        for token in re.findall(r"`([^`]+)`", line.lower()):
            is_named_index = token.endswith(("_idx", "_uk"))
            if token in banned_source_tokens or is_named_index:
                bad_sources.append(token)
            if (
                re.fullmatch(
                    r"(?:pro_[a-z0-9_]+|pg_catalog|information_schema)\.[a-z0-9_]+",
                    token,
                )
                and token not in solution
            ):
                phantom_relations.append(token)

    assert bad_sources == [], (
        f"{stem} classifies SQL keywords, aliases, extensions, commands, or "
        f"indexes as input relations: {bad_sources}"
    )
    assert phantom_relations == [], (
        f"{stem} names input relations that do not exist anywhere in its "
        f"executable solution: {phantom_relations}"
    )

    assert "with no outer `GROUP BY`; return exactly one aggregate row" not in exercises, (
        f"{stem} still contains a generated one-row aggregate template; state "
        "the actual grouping and result grain instead"
    )
    for generated_contract in banned_generated_contracts:
        assert generated_contract.lower() not in exercises.lower(), (
            f"{stem} still contains generated exercise boilerplate rather than "
            f"a concrete result contract: {generated_contract!r}"
        )


@pytest.mark.parametrize(
    "solution_path",
    PROFESSIONAL_SOLUTION_MARKDOWN,
    ids=lambda path: path.stem,
)
def test_professional_solution_prose_has_no_generator_false_green(
    solution_path: Path,
) -> None:
    source = solution_path.read_text(encoding="utf-8")
    generic_sentence_families = (
        "the solution actually uses",
        "the chosen form is justified by this lesson-specific rationale",
        "evaluate another form against the concrete expected result",
    )
    known_truncations = (
        "AFTER UPDATE .",
        "ledger reconciliation and reve.",
        "materialize a.",
    )

    for generic_sentence in generic_sentence_families:
        assert generic_sentence.lower() not in source.lower(), (
            f"{solution_path.name} still contains generated false-green prose: {generic_sentence!r}"
        )
    for truncation in known_truncations:
        assert truncation.lower() not in source.lower(), (
            f"{solution_path.name} contains a known truncated sentence: {truncation!r}"
        )


def test_professional_test_matrix_includes_malformed_and_null_boundaries() -> None:
    solution = _code(_professional_solution("sql_test_01_contracts_migrations"))

    assert "malformed" in solution
    assert re.search(r"'[^']*null'[^)]*,\s*null\s*,\s*false\b", solution), (
        "the table-driven boundary matrix must exercise SQL NULL, not only "
        "below/exact/above integers"
    )


def test_professional_analytics_implements_attribution_and_asof_boundaries() -> None:
    source = _professional_solution("sql_analytics_01_query_patterns")
    solution = _code(source)
    attribution = _code(_exercise(source, 5))
    as_of = _code(_exercise(source, 7))

    assert "left join lateral" in solution
    assert re.search(r"order\s+by\s+\w*\.?touched_at\s+desc\s*,\s*\w*\.?touch_id\s+desc", solution)
    assert re.search(
        r"\bselect\b.*?\bselected\.touch_id\b.*?\bselected\.campaign\b",
        attribution,
    ), "the winning touch ID must remain visible for attribution audit"
    assert re.search(r"\bvalid_from\s*<=\s*\w*\.?event_at\b", solution)
    has_finite_upper_predicate = re.search(
        r"\b\w*\.?event_at\s*<\s*\w*\.?valid_to\b",
        solution,
    )
    has_infinite_upper_predicate = re.search(
        r"\b\w*\.?event_at\s*<\s*coalesce\s*\(\s*\w*\.?valid_to\b",
        solution,
    )
    assert has_finite_upper_predicate or has_infinite_upper_predicate
    assert re.search(
        r"\bhaving\s+count\s*\(\s*(?:\*|\w+(?:\.\w+)?)\s*\)\s*>\s*1\b",
        as_of,
    ), "an as-of answer must detect overlapping matches, not hide them with LIMIT 1"


def test_professional_analytics_guide_states_the_real_result_grains() -> None:
    stem = "sql_analytics_01_query_patterns"
    islands = _professional_guide_exercise(stem, 4).lower()
    attribution = _professional_guide_exercise(stem, 5).lower()
    as_of = _professional_guide_exercise(stem, 7).lower()
    percentiles = _professional_guide_exercise(stem, 9).lower()
    approximation = _professional_guide_exercise(stem, 13).lower()

    assert "one row per user-date" not in islands
    assert re.search(r"one row per .*island", islands)
    for field in ("user_id", "island_start", "island_end", "active_days"):
        assert f"`{field}`" in islands

    for relation in (
        "pro_analytics_lab.deduplicated_events",
        "pro_analytics_lab.campaign_touches",
    ):
        assert f"`{relation}`" in attribution
    assert re.search(r"one row per .*purchase", attribution)
    for field in ("source_event_id", "purchased_at", "touch_id", "campaign"):
        assert f"`{field}`" in attribution

    for relation in (
        "pro_analytics_lab.event_probes",
        "pro_analytics_lab.user_tiers",
    ):
        assert f"`{relation}`" in as_of
    assert re.search(r"one row per .*probe", as_of)
    for field in ("probe_id", "event_at", "tier_name", "matching_tiers"):
        assert f"`{field}`" in as_of

    assert "disposable restore target" not in percentiles
    assert re.search(r"(?:exactly )?one (?:aggregate |summary )?row", percentiles)
    for field in ("session_count", "median_and_p90"):
        assert f"`{field}`" in percentiles

    assert "command tag" not in approximation
    for field in (
        "exact_distinct_users",
        "criterion_number",
        "criterion",
        "required_evidence",
    ):
        assert f"`{field}`" in approximation


def test_professional_analytics_learner_demonstrates_positive_month_one_retention() -> None:
    learner = _code(
        (PROFESSIONAL_SQL_ROOT / "lessons" / "sql_analytics_01_query_patterns.sql").read_text(
            encoding="utf-8"
        )
    )

    assert re.search(
        r"\(\s*1\s*,\s*date\s*'2026-02-\d{2}'\s*\)",
        learner,
    ), (
        "the worked cohort fixture needs at least one retained January user in "
        "February, while another January cohort member remains nonretained"
    )
    has_direct_month_one_assertion = re.search(
        r"\bmonth_number\s*=\s*1\b.*?\bretained_users\s*>\s*0\b",
        learner,
    )
    has_named_fixture_assertion = re.search(
        r"\bjanuary_month_1_users\s*<>\s*1\b",
        learner,
    )
    assert has_direct_month_one_assertion or has_named_fixture_assertion


def test_professional_foundation_drift_report_can_observe_unexpected_columns() -> None:
    solution = _code(_professional_solution("sql_found_02_versioned_migrations"))
    observed = re.search(
        r"\bobserved\s+as\s*\((?P<body>.*?)\)\s*select\b",
        solution,
    )

    assert observed is not None
    assert "drift_status" in solution
    assert not re.search(r"\bcolumn_name\s+in\s*\(", observed.group("body")), (
        "filtering observed columns to the expected names makes the "
        "'unexpected' FULL JOIN branch unreachable"
    )


@pytest.mark.parametrize(
    ("filename", "migration_name", "content_tag"),
    (
        (
            "001_create_service_requests.sql",
            "create_service_requests",
            "course-fixture-001-v1",
        ),
        ("002_expand_priority.sql", "expand_priority", "course-fixture-002-v1"),
        ("003_backfill_priority.sql", "backfill_priority", "course-fixture-003-v1"),
        ("004_contract_priority.sql", "contract_priority", "course-fixture-004-v1"),
        (
            "005_forward_fix_priority_rank.sql",
            "forward_fix_priority_rank",
            "course-fixture-005-v1",
        ),
    ),
)
def test_professional_migration_skip_requires_exact_immutable_identity(
    filename: str,
    migration_name: str,
    content_tag: str,
) -> None:
    source = _professional_migration_fixture(filename)
    code = _code(source)
    preflight = _code(source.split(r"\if :migration_applied", maxsplit=1)[0])

    for field in ("migration_id", "migration_name", "content_tag"):
        assert field in preflight, (
            f"{filename} must compare {field} before deciding an existing "
            "manifest row is safe to skip"
        )
    assert f"'{migration_name}'" in preflight
    assert f"'{content_tag}'" in preflight
    assert "pg_advisory_xact_lock" in code, (
        f"{filename} needs the shared migration-runner lock before inspecting "
        "or changing manifest/schema state"
    )
    assert any(
        catalog_probe in preflight
        for catalog_probe in (
            "information_schema.",
            "pg_catalog.",
            "assert_migration_contract",
            "verify_migration_contract",
        )
    ), (
        f"{filename} must verify the already-applied schema contract before "
        "skipping; an exact manifest row can coexist with later schema drift"
    )


def test_professional_migrations_share_one_serialization_lock() -> None:
    lock_keys: list[str] = []
    for filename in (
        "001_create_service_requests.sql",
        "002_expand_priority.sql",
        "003_backfill_priority.sql",
        "004_contract_priority.sql",
        "005_forward_fix_priority_rank.sql",
    ):
        migration = _code(_professional_migration_fixture(filename))
        lock = re.search(
            r"\bpg_advisory_xact_lock\s*\((?P<key>.*?)\)\s*;",
            migration,
        )
        assert lock is not None, f"{filename} is missing its migration-runner lock"
        lock_keys.append(lock.group("key"))

    assert len(set(lock_keys)) == 1, (
        "all migrations must serialize on the same lock key; per-version locks "
        "still allow version N and N+1 to race"
    )


def test_professional_first_migration_does_not_adopt_an_unknown_existing_table() -> None:
    migration = _code(_professional_migration_fixture("001_create_service_requests.sql"))

    assert not re.search(
        r"\bcreate\s+table\s+if\s+not\s+exists\s+"
        r"pro_migration_lab\.schema_migrations\b",
        migration,
    ), (
        "IF NOT EXISTS can silently adopt a drifted manifest table; exact "
        "catalog verification or a hard duplicate-object failure is safer"
    )


def test_professional_relational_design_exercises_prove_their_actual_contracts() -> None:
    solution_source = _professional_solution("sql_found_01_relational_design")
    solution = _code(solution_source)
    solution_reasoning = (
        PROFESSIONAL_SQL_ROOT / "solutions" / "sql_found_01_relational_design_solutions.md"
    ).read_text(encoding="utf-8")
    historical_fee = _code(_exercise(solution_source, 4))
    normalized_assignments = _code(_exercise(solution_source, 5))
    outer_join_report = _code(_exercise(solution_source, 6))
    deletion_policy = _code(_exercise(solution_source, 7))
    catalog_contract = _code(_exercise(solution_source, 8))

    assert re.search(r"\bdaily_fee_at_checkout\s+numeric\b", historical_fee)
    assert re.search(
        r"\binsert\s+into\s+pro_relational_lab\.\w*loans?\b"
        r".*?\bdaily_fee_at_checkout\b",
        historical_fee,
    )
    assert re.search(
        r"\bselect\b.*?\bdaily_fee_at_checkout\b.*?"
        r"\bfrom\s+pro_relational_lab\.\w*loans?\b",
        historical_fee,
    )

    for relation, key in (
        ("providers", "provider_id"),
        ("technicians", "technician_id"),
    ):
        assert re.search(
            rf"\bcreate\s+table\s+pro_relational_lab\.{relation}\s*\("
            rf".*?\b{key}\b.*?\bprimary\s+key\b",
            normalized_assignments,
        )
    assert re.search(
        r"\bcreate\s+table\s+pro_relational_lab\.visit_technicians\s*\("
        r".*?\bprimary\s+key\s*\(\s*visit_id\s*,\s*technician_id\s*\)",
        normalized_assignments,
    )
    assert re.search(
        r"\bcreate\s+table\s+pro_relational_lab\.visit_providers\s*\("
        r".*?\bvisit_id\b.*?\bprimary\s+key\b",
        normalized_assignments,
    )

    assert re.search(
        r"\bselect\s+\w*\.?item_id\s*,\s*\w*\.?asset_tag\s*,"
        r".*?\bcount\s*\(\s*\w*\.?loan_id\s*\)\s+as\s+loan_count\s*,"
        r".*?\bmax\s*\(\s*\w*\.?checked_out_on\s*\)\s+as\s+latest_checkout"
        r".*?\bfrom\s+pro_relational_lab\.equipment_items\b"
        r".*?\bleft\s+join\s+pro_relational_lab\.loans\b",
        outer_join_report,
    )

    assert "pg_catalog.pg_constraint" in deletion_policy
    assert "expected_action" in deletion_policy
    assert "actual_action" in deletion_policy
    assert "restrict" in deletion_policy and "cascade" in deletion_policy
    assert "is distinct from" in deletion_policy or "matches" in deletion_policy

    for field in ("conname", "contype", "pg_get_constraintdef"):
        assert field in catalog_contract
    assert re.search(r"\border\s+by\b[^;]*\bconname\b", catalog_contract)
    assert "daily_fee_at_checkout" in solution

    assert not re.search(
        r"\bcoalesce\s*\(\s*completed_on\s*,\s*opened_on\s*\)",
        solution_reasoning,
        flags=re.IGNORECASE,
    ), (
        "the executable generated column returns NULL for an open visit; the "
        "Markdown must not show the old COALESCE-to-zero definition"
    )
    assert not re.search(
        r"\bservice_days\b.{0,80}\bzero\b.{0,80}\bopen\b",
        solution_reasoning,
        flags=re.IGNORECASE | re.DOTALL,
    ), "solution prose must not claim service_days is zero while a visit is open"


def test_professional_relational_deletion_matrix_matches_all_eight_foreign_keys() -> None:
    stem = "sql_found_01_relational_design"
    solution_source = _professional_solution(stem)
    deletion_policy_source = _exercise(solution_source, 7)
    deletion_policy = _code(deletion_policy_source)
    guide = _professional_guide(stem)
    learner = (PROFESSIONAL_SQL_ROOT / "lessons" / f"{stem}.sql").read_text(encoding="utf-8")
    solution_markdown = (PROFESSIONAL_SQL_ROOT / "solutions" / f"{stem}_solutions.md").read_text(
        encoding="utf-8"
    )

    expected_actions = {
        ("equipment_items", "equipment_categories"): "restrict",
        ("loans", "equipment_items"): "restrict",
        ("loans", "members"): "restrict",
        ("maintenance_visits", "equipment_items"): "restrict",
        ("visit_providers", "maintenance_visits"): "cascade",
        ("visit_providers", "providers"): "restrict",
        ("visit_technicians", "maintenance_visits"): "cascade",
        ("visit_technicians", "technicians"): "restrict",
    }
    declared_actions = {
        (child.lower(), parent.lower()): action.lower()
        for child, parent, action in re.findall(
            r"\(\s*'(\w+)'(?:::\w+)?\s*,\s*'(\w+)'(?:::\w+)?\s*,"
            r"\s*'(restrict|cascade|set null)'",
            deletion_policy_source,
            flags=re.IGNORECASE,
        )
    }

    assert declared_actions == expected_actions
    assert len(
        re.findall(
            r"\breferences\s+pro_relational_lab\.",
            _code(solution_source),
        )
    ) == len(expected_actions), (
        "the solution calls this a complete foreign-key inventory, so the "
        "fixture and expected deletion-policy manifest must stay the same size"
    )

    for output_field in (
        "relationship",
        "expected_action",
        "actual_action",
        "drift_status",
        "rationale",
    ):
        assert output_field in deletion_policy

    learner_contract = re.search(
        r"^-- 7\..*?(?=^-- 8\.|\Z)",
        learner,
        flags=re.MULTILINE | re.DOTALL,
    )
    markdown_contract = re.search(
        r"^## Exercise 7\b.*?(?=^## Exercise 8\b|\Z)",
        solution_markdown,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert learner_contract is not None
    assert markdown_contract is not None

    for surface_name, contract in (
        ("guide", _markdown_exercises(guide)),
        ("learner", learner_contract.group(0)),
        ("solution Markdown", markdown_contract.group(0)),
    ):
        normalized = contract.lower()
        assert "all eight implemented foreign keys" in normalized, (
            f"{surface_name} must state the same complete eight-FK scope as the executable answer"
        )
        assert "eight rows" in normalized
        for output_field in (
            "relationship",
            "expected_action",
            "actual_action",
            "drift_status",
            "rationale",
        ):
            assert f"`{output_field}`" in normalized


def test_professional_programming_exercises_a_true_zero_row_statement_trigger() -> None:
    solution = _code(_professional_solution("sql_prog_01_routines_triggers"))

    assert re.search(
        r"update\s+pro_routines_lab\.work_items\b.*?\bwhere\b"
        r".*?(?:\bfalse\b|\bitem_id\s*(?:=|<)\s*-\s*1\b)",
        solution,
    )
    assert re.search(r"\bmatched_rows\s*=\s*0\b", solution)


def test_professional_programming_transition_join_key_cannot_change() -> None:
    solution = _code(_professional_solution("sql_prog_01_routines_triggers"))

    assert re.search(
        r"\bold\.item_id\s+is\s+distinct\s+from\s+new\.item_id\b",
        solution,
    )
    assert re.search(
        r"\bjoin\s+new_rows\b.*?\busing\s*\(\s*item_id\s*\)",
        solution,
    )


def test_professional_replication_detects_leading_gaps_and_orders_ddl_phases() -> None:
    solution = _code(_professional_solution("sql_repl_01_cdc_high_availability"))

    assert "generate_series( av.versions[1]" not in solution
    assert re.search(r"\bmissing_(?:version|versions)\b", solution)
    assert "step_number" in solution
    assert re.search(r"\border\s+by\s+step_number\b", solution)


def test_professional_replication_separates_broker_ack_from_consumer_effects() -> None:
    solution = _code(_professional_solution("sql_repl_01_cdc_high_availability"))
    consumer = re.search(
        r"\bcreate\s+procedure\s+pro_replication_lab\.deliver_event\b"
        r".*?\bas\s+\$procedure\$(?P<body>.*?)\$procedure\$",
        solution,
    )
    publisher_ack = re.search(
        r"\bcreate\s+procedure\s+pro_replication_lab\.mark_published\b"
        r".*?\bas\s+\$procedure\$(?P<body>.*?)\$procedure\$",
        solution,
    )

    assert consumer is not None
    assert publisher_ack is not None
    acknowledged_relation = re.search(
        r"\bupdate\s+pro_replication_lab\.(?P<relation>\w+)\b"
        r".*?\bset\s+published\s*=\s*true\b",
        publisher_ack.group("body"),
    )
    assert acknowledged_relation is not None
    outbox_relation = acknowledged_relation.group("relation")
    assert not re.search(
        rf"\bupdate\s+pro_replication_lab\.{outbox_relation}\b.*?\bpublished\b",
        consumer.group("body"),
    ), (
        "a consumer side effect is not proof that the publisher's broker "
        "delivery was durably acknowledged"
    )


def test_professional_security_proves_tenant_isolation_and_a_narrow_writer() -> None:
    solution = _code(_professional_solution("sql_sec_01_roles_privileges_rls"))

    for tenant_role in ("ds60_sec_north", "ds60_sec_south"):
        assert re.search(rf"\bset\s+local\s+role\s+{tenant_role}\b", solution)

    writer_role = re.search(r"\bcreate\s+role\s+(ds60_sec_\w*writer\w*)\s+nologin\b", solution)
    assert writer_role is not None
    assert re.search(rf"\bset\s+local\s+role\s+{writer_role.group(1)}\b", solution)
    writer = writer_role.group(1)
    assert not re.search(
        rf"\bgrant\s+insert\b.*?\bto\s+{writer}\b",
        solution,
    )
    assert not re.search(
        rf"\bgrant\s+usage\s+on\s+sequence\b.*?\bto\s+{writer}\b",
        solution,
    )
    assert re.search(
        rf"\bgrant\s+execute\b.*?\bto\s+{writer}\b",
        solution,
    )
    assert re.search(
        rf"\bhas_table_privilege\s*\(\s*'{writer}'\s*,.*?'insert'\s*\)",
        solution,
    )
    assert re.search(
        rf"\bhas_sequence_privilege\s*\(\s*'{writer}'\s*,.*?'usage'\s*\)",
        solution,
    )


def test_professional_security_proves_creator_specific_defaults_and_definer_identity() -> None:
    solution = _code(_professional_solution("sql_sec_01_roles_privileges_rls"))

    assert "ds60_sec_other_owner" in solution
    assert re.search(
        r"\bset\s+local\s+role\s+ds60_sec_other_owner\b.*?"
        r"\bcreate\s+table\s+pro_security_lab\.other_owner_\w+\b",
        solution,
    )
    assert re.search(
        r"\bif\s+pg_catalog\.has_table_privilege\s*\(\s*"
        r"'ds60_sec_auditor'\s*,\s*'pro_security_lab\.other_owner_\w+'\s*,"
        r"\s*'select'\s*\).*?\braise\s+exception\b",
        solution,
    ), "the second creator's table must prove the first owner's defaults did not leak"

    identity_probe = re.search(
        r"\bcreate\s+function\s+pro_security_lab\.identity_probe\b"
        r".*?\bas\s+\$function\$(?P<body>.*?)\$function\$",
        solution,
    )
    assert identity_probe is not None
    for identity in ("session_user", "current_user"):
        assert identity in identity_probe.group("body")
    assert re.search(
        r"\bset\s+local\s+role\s+ds60_sec_auditor\b.*?"
        r"\bfrom\s+pro_security_lab\.identity_probe\s*\(\s*\)",
        solution,
    )


def test_professional_temporal_enforces_immutability_and_single_match_contracts() -> None:
    solution = _code(_professional_solution("sql_temporal_01_domain_modelling"))

    for relation in ("ledger", "retention_decisions"):
        assert re.search(
            rf"\bcreate\s+trigger\b.*?\bbefore\b.*?\bupdate\b.*?\bdelete\b"
            rf".*?\bon\s+pro_temporal_lab\.{relation}\b",
            solution,
        ), f"{relation} is described as immutable but has no UPDATE/DELETE guard"

    assert re.search(
        r"\bgroup\s+by\s+\w*\.?order_key\b.*?\bhaving\s+count\s*\("
        r"\s*\w*\.?customer_version_id\s*\)\s*>\s*1\b",
        solution,
    ), "the Type-2 join must fail if one fact matches multiple dimension versions"
    assert "upper_inf(" in solution or "range_agg(" in solution, (
        "gap/overlap logic must preserve an unbounded prior range instead of "
        "letting max(upper(range)) ignore NULL"
    )


def test_professional_temporal_classifies_dst_anomalies_before_interpreting_them() -> None:
    dst = _code(
        _exercise(
            _professional_solution("sql_temporal_01_domain_modelling"),
            7,
        )
    )

    for anomaly in ("nonexistent", "ambiguous"):
        assert f"'{anomaly}'" in dst
    assert re.search(r"\b(?:civil_time_status|classification|anomaly_kind)\b", dst)
    assert re.search(r"\b(?:resolution_policy|disambiguation|rejection_policy)\b", dst)


def test_professional_temporal_retention_log_has_one_authoritative_order() -> None:
    source = _professional_solution("sql_temporal_01_domain_modelling")
    solution = _code(source)
    validator = re.search(
        r"\bcreate\s+function\s+pro_temporal_lab\.validate_retention_decision\b"
        r".*?\bas\s+\$function\$(?P<body>.*?)\$function\$",
        solution,
    )

    assert validator is not None
    body = validator.group("body")
    has_monotonic_decision_time = re.search(
        r"\bnew\.decided_at\s*(?:<=|<)\s*(?:previous_|prior_|latest_)?decided_at\b",
        body,
    )
    has_append_order_state_machine = re.search(
        r"\border\s+by\s+\w*\.?decision_event_id\s+desc\b",
        body,
    )
    assert has_monotonic_decision_time or has_append_order_state_machine, (
        "state transitions need one authoritative order; ordering prior state "
        "by decided_at without rejecting backdated appends can corrupt chronology"
    )
    assert re.search(
        r"\bdelete\s+from\s+pro_temporal_lab\.retention_decisions\b",
        solution,
    ), "the immutable decision log must exercise both UPDATE and DELETE rejection"


def test_professional_types_validate_integer_json_before_casting() -> None:
    source = _professional_solution("sql_types_01_native_types_search")
    generated_column = _code(_exercise(source, 10))

    assert "jsonb_typeof" in generated_column
    assert re.search(
        r"\b(?:trunc|floor)\s*\(",
        generated_column,
    ), "a JSON number may be fractional even though jsonb_typeof reports 'number'"
    assert re.search(
        r"(?:<=\s*2147483647\b|<\s*2147483648\b|"
        r"\bbetween\s+\d+\s+and\s+2147483647\b)",
        generated_column,
    ), "validate the PostgreSQL integer upper bound before the generated-column cast"


def test_professional_types_compare_all_promised_money_representations() -> None:
    money = _code(
        _exercise(
            _professional_solution("sql_types_01_native_types_search"),
            9,
        )
    )

    assert re.search(
        r"\b(?:minor_units|amount_in_minor_units|amount_cents|minor\s+units)\b",
        money,
    )
    assert re.search(r"\b(?:double\s+precision|float8|real)\b", money)


def test_professional_type_normalization_handles_legacy_duplicate_tags() -> None:
    solution = _code(_professional_solution("sql_types_01_native_types_search"))
    bridge_insert = re.search(
        r"insert\s+into\s+pro_types_lab\.document_tags\b(?P<body>.*?);",
        solution,
    )

    assert bridge_insert is not None
    body = bridge_insert.group("body")
    has_deduplicated_source = "select distinct" in body or "group by" in body
    has_duplicate_preflight = re.search(
        r"\bhaving\s+count\s*\(\s*\*\s*\)\s*>\s*1\b",
        solution,
    )
    assert has_deduplicated_source or has_duplicate_preflight, (
        "a duplicate tag in a legacy array must be deliberately deduplicated "
        "or rejected before the composite-key bridge insert"
    )


def test_professional_ops_uses_transaction_local_hot_update_evidence() -> None:
    solution = _code(_professional_solution("sql_ops_01_indexes_statistics_maintenance"))

    assert "pg_catalog.pg_stat_xact_user_tables" in solution


def test_professional_ops_partition_and_scorecard_answers_are_executable() -> None:
    source = _professional_solution("sql_ops_01_indexes_statistics_maintenance")
    partitioning = _code(_exercise(source, 10))
    scorecard = _code(_exercise(source, 12))

    assert re.search(r"\bcreate\s+table\b.*?\bpartition\s+by\b", partitioning)
    assert re.search(r"\bcreate\s+table\b.*?\bpartition\s+of\b", partitioning)
    assert "explain" in partitioning
    has_child_index_inventory = "pg_catalog.pg_indexes" in partitioning or (
        "pg_catalog.pg_index" in partitioning and "pg_catalog.pg_inherits" in partitioning
    )
    assert has_child_index_inventory, (
        "the pruning plan proves only the selected partition; inventory every "
        "child index to prove the partitioned index was realized everywhere"
    )
    for promised_field in ("budget", "cadence", "escalation", "runbook"):
        assert promised_field in scorecard


def test_professional_ops_preload_detection_ignores_list_whitespace() -> None:
    capability = _code(
        _exercise(
            _professional_solution("sql_ops_01_indexes_statistics_maintenance"),
            6,
        )
    )

    has_whitespace_aware_split = "regexp_split_to_array" in capability
    has_trimmed_entries = (
        "string_to_array" in capability
        and "unnest" in capability
        and re.search(r"\bbtrim\s*\(", capability)
    )
    assert has_whitespace_aware_split or has_trimmed_entries


def test_professional_recovery_uses_canonical_checksums_and_rich_schema_contracts() -> None:
    source = _professional_solution("sql_ops_02_backup_restore_recovery")
    solution = _code(source)
    checksum = re.search(
        r"\bcreate\s+function\s+pro_recovery_lab\.records_checksum\b"
        r".*?\bas\s+\$function\$(?P<body>.*?)\$function\$",
        solution,
    )

    assert checksum is not None
    checksum_body = checksum.group("body")
    has_structured_rows = any(
        serializer in checksum_body
        for serializer in ("jsonb_build_array", "json_build_array", "row_to_json")
    )
    has_length_prefix = "octet_length" in checksum_body
    assert has_structured_rows or has_length_prefix, (
        "delimiter-concatenated rows can collide; serialize fields canonically "
        "or length-prefix every value before hashing"
    )
    assert "coalesce" in checksum_body, "empty inputs need a deterministic checksum"

    schema_contract = _code(_exercise(source, 1))
    for semantic_property in (
        "udt_name",
        "numeric_precision",
        "numeric_scale",
        "datetime_precision",
        "column_default",
        "is_identity",
        "identity_generation",
        "identity_start",
        "identity_increment",
        "is_generated",
        "generation_expression",
        "collation_name",
    ):
        assert semantic_property in schema_contract
    assert "semantic_definition" in schema_contract
    for contract_side in ("source_records", "restored_records"):
        assert f"'{contract_side}'" in schema_contract
    has_bidirectional_comparison = (
        "full join" in schema_contract
        or "full outer join" in schema_contract
        or schema_contract.count(" except ") >= 2
    )
    assert has_bidirectional_comparison, (
        "a restored-only fingerprint is not verification; compare normalized "
        "expected/source and restored semantic rows in both directions"
    )
    assert re.search(
        r"\b(?:contracts?_match|contract_status|comparison_status|drift_status|"
        r"mismatch_(?:side|rows))\b",
        schema_contract,
    )


def test_professional_vector_distance_rejects_nulls_and_defines_empty_input() -> None:
    source = _professional_solution("sql_ext_01_extensions_spatial_vector")
    solution = _code(source)
    function = re.search(
        r"\bcreate\s+function\s+pro_extensions_lab\.checked_l2\b"
        r".*?\bas\s+\$function\$(?P<body>.*?)\$function\$",
        solution,
    )

    assert function is not None
    body = function.group("body")
    has_combined_null_check = re.search(
        r"\bunnest\s*\(\s*p_left\s*\|\|\s*p_right\s*\).*?\bis\s+null\b",
        body,
    )
    for parameter in ("p_left", "p_right"):
        has_array_check = re.search(
            rf"\barray_position\s*\(\s*{parameter}\s*,\s*null\s*\)",
            body,
        )
        has_unnest_check = re.search(
            rf"\bunnest\s*\(\s*{parameter}\s*\).*?\bis\s+null\b",
            body,
        )
        assert has_array_check or has_unnest_check or has_combined_null_check, (
            f"checked_l2 must reject a NULL element in {parameter}; SUM silently "
            "ignores NULL inputs"
        )

    has_explicit_empty_policy = re.search(
        r"\bcardinality\s*\(\s*p_left\s*\)\s*=\s*0\b",
        body,
    ) or re.search(r"\bcoalesce\s*\(\s*sqrt\s*\(", body)
    assert has_explicit_empty_policy, (
        "checked_l2 must explicitly reject two empty vectors or define their "
        "distance instead of returning an accidental NULL"
    )
    assert re.search(
        r"\barray\s*\[[^\]]*\bnull\b[^\]]*\]\s*::\s*double\s+precision\s*\[\]",
        solution,
    ), "the executable negative matrix must demonstrate a NULL-element vector"
    assert re.search(
        r"\barray\s*\[\s*\]\s*::\s*double\s+precision\s*\[\]",
        solution,
    ), "the executable boundary matrix must demonstrate the empty-vector policy"
