from __future__ import annotations

import importlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import pytest

from ds60sqlpy.catalog import Catalog, Lesson

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG = Catalog.load(REPO_ROOT)

_CONTRACT_FIELDS = ("inputs", "expected", "verify")
_CONTRACT_LABEL = re.compile(
    r"(?:\*\*)?"
    r"(?P<label>"
    r"Inputs(?:/evidence)?|"
    r"Expected result/shape|"
    r"Verify|"
    r"Independent verification"
    r"):"
    r"(?:\*\*)?\s*"
    r"(?P<body>.+?)\s*$"
)
_EXERCISE_PREFIX = re.compile(
    r"^For (?P<lesson_id>sql-[a-z0-9-]+) Exercise (?P<number>[1-9][0-9]*),"
)
_GUIDE_EXERCISE = re.compile(r"^(?P<number>[1-9][0-9]*)\.\s+", re.MULTILINE)
_LEARNER_EXERCISE = re.compile(
    r"^\s*--\s+(?P<number>[1-9][0-9]*)\.\s+",
    re.MULTILINE,
)
_SOLUTION_EXERCISE = re.compile(
    r"^## Exercise (?P<number>[1-9][0-9]*)\b",
    re.MULTILINE,
)
_DML_CONTRACT_LANGUAGE = (
    "before writing",
    "command tag",
    "`returning`",
    "target set",
    "affected-row",
    "idempotent retry",
    "conflict policy",
    "add one row",
    "insert rows",
)


@dataclass(frozen=True)
class Contract:
    inputs: str
    expected: str
    verify: str


def _canonical_field(label: str) -> str:
    if label.startswith("Inputs"):
        return "inputs"
    if label == "Expected result/shape":
        return "expected"
    return "verify"


_PROSE_REPAIRS = json.loads((REPO_ROOT / "curriculum/prose-repairs.json").read_text())["repairs"]
# SQL files retain their exact executable bytes, including historical comments.
# Only approved alphabetic joins may gain spaces during this prose comparison.
# Numbers, operators, identifiers with underscores and word spelling stay strict.
_CONTRACT_SPACING = {
    source: target
    for source, target in _PROSE_REPAIRS.items()
    if source.isalpha() and re.sub(r"\s+", "", target) == source
}
_CONTRACT_SPACING_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(word) for word in _CONTRACT_SPACING) + r")\b"
)


def _normalize_contract(body: str) -> str:
    body = _CONTRACT_SPACING_PATTERN.sub(lambda match: _CONTRACT_SPACING[match.group()], body)
    return re.sub(r"\s+", " ", body).strip()


def test_contract_typography_does_not_relax_numbers_operators_or_identifiers() -> None:
    assert _normalize_contract("As ofJanuary 10, compare values andNULL.") == (
        "As of January 10, compare values and NULL."
    )
    assert _normalize_contract("Return 10 rows.") != _normalize_contract("Return 100 rows.")
    assert _normalize_contract("amount > 0") != _normalize_contract("amount >= 0")
    assert _normalize_contract("user_id") != _normalize_contract("user id")
    assert _normalize_contract("NULL") != _normalize_contract("0")


def _exercise_section(source: str, *, markdown: bool) -> str:
    if markdown:
        match = re.search(
            r"^## Exercises\b.*?(?=^##\s|\Z)",
            source,
            flags=re.MULTILINE | re.DOTALL,
        )
    else:
        match = re.search(
            r"^\s*-- Exercises\b.*\Z",
            source,
            flags=re.MULTILINE | re.DOTALL,
        )
    assert match is not None, "authoritative Exercises section is missing"
    return match.group(0)


def _prompt_numbers(source: str, *, surface: str) -> tuple[int, ...]:
    if surface == "guide":
        section = _exercise_section(source, markdown=True)
        pattern = _GUIDE_EXERCISE
    elif surface == "learner":
        section = _exercise_section(source, markdown=False)
        pattern = _LEARNER_EXERCISE
    else:
        section = source
        pattern = _SOLUTION_EXERCISE

    numbers = tuple(int(match.group("number")) for match in pattern.finditer(section))
    assert numbers, f"{surface} has no numbered exercises"
    assert numbers == tuple(range(1, len(numbers) + 1)), (
        f"{surface} exercise IDs are missing, duplicated, or out of order: {numbers}"
    )
    return numbers


def _contracts(
    source: str,
    *,
    lesson_id: str,
    surface: str,
) -> dict[int, Contract]:
    section = (
        _exercise_section(source, markdown=surface == "guide") if surface != "solution" else source
    )
    fields_by_exercise: dict[int, dict[str, str]] = {}

    for line_number, line in enumerate(section.splitlines(), start=1):
        marker = _CONTRACT_LABEL.search(line)
        if marker is None:
            continue

        body = _normalize_contract(marker.group("body"))
        prefix = _EXERCISE_PREFIX.match(body)
        if prefix is None:
            # Worked examples also use "Expected result/shape"; only the
            # exercise-specific "For <lesson> Exercise <n>" records are shared.
            continue

        observed_lesson_id = prefix.group("lesson_id")
        assert observed_lesson_id == lesson_id, (
            f"{surface} line {line_number} names {observed_lesson_id}, expected {lesson_id}: {body}"
        )
        exercise_number = int(prefix.group("number"))
        field = _canonical_field(marker.group("label"))
        exercise_fields = fields_by_exercise.setdefault(exercise_number, {})
        assert field not in exercise_fields, (
            f"{surface} repeats {field} for {lesson_id} Exercise {exercise_number}"
        )
        exercise_fields[field] = body

    prompt_numbers = _prompt_numbers(source, surface=surface)
    assert tuple(sorted(fields_by_exercise)) == prompt_numbers, (
        f"{surface} contract exercise IDs {tuple(sorted(fields_by_exercise))} "
        f"do not match prompt IDs {prompt_numbers}"
    )

    contracts: dict[int, Contract] = {}
    for exercise_number in prompt_numbers:
        fields = fields_by_exercise[exercise_number]
        missing = set(_CONTRACT_FIELDS) - fields.keys()
        assert not missing, (
            f"{surface} is missing {sorted(missing)} for {lesson_id} Exercise {exercise_number}"
        )
        contracts[exercise_number] = Contract(
            inputs=fields["inputs"],
            expected=fields["expected"],
            verify=fields["verify"],
        )
    return contracts


def _markdown_solution(catalog: Catalog, lesson: Lesson) -> Path:
    paths = [
        catalog.resolve(relative_path)
        for relative_path in lesson.solution_paths
        if Path(relative_path).suffix.lower() == ".md"
    ]
    assert len(paths) == 1, (
        f"{lesson.id} must catalog exactly one Markdown solution; found "
        f"{[path.relative_to(catalog.repo_root).as_posix() for path in paths]}"
    )
    return paths[0]


def _guide_contract(lesson_id: str, exercise_number: int) -> Contract:
    lesson = CATALOG.get(lesson_id)
    contracts = _contracts(
        CATALOG.resolve(lesson.guide_path).read_text(encoding="utf-8"),
        lesson_id=lesson.id,
        surface="guide",
    )
    return contracts[exercise_number]


def _executable_solution(lesson_id: str, *, preserve_case: bool = False) -> str:
    lesson = CATALOG.get(lesson_id)
    paths = [
        CATALOG.resolve(relative_path)
        for relative_path in lesson.solution_paths
        if Path(relative_path).suffix.lower() == ".sql"
    ]
    assert len(paths) == 1, f"{lesson_id} must catalog exactly one executable SQL solution"
    source = paths[0].read_text(encoding="utf-8")
    return source if preserve_case else source.lower()


def _sql_tokens(source: str) -> list[tuple[str, str]]:
    """Ignore layout, retaining literal values, operators and quoted identities."""
    scan = importlib.import_module("pglast.parser").scan
    result: list[tuple[str, str]] = []
    for token in scan(source):
        if token.name in {"C_COMMENT", "SQL_COMMENT"}:
            continue
        text = source[token.start : token.end + 1]
        if token.kind != "NO_KEYWORD" or (token.name == "IDENT" and not text.startswith('"')):
            text = text.lower()
        result.append((str(token.name), text))
    return result


def _count_sql_fragment(source: str, fragment: str) -> int:
    tokens = _sql_tokens(source)
    expected = _sql_tokens(fragment)
    assert expected, "A SQL contract fragment must contain syntax"
    return sum(
        tokens[index : index + len(expected)] == expected
        for index in range(len(tokens) - len(expected) + 1)
    )


def _contract_text(contract: Contract) -> str:
    return " ".join((contract.inputs, contract.expected, contract.verify)).lower()


def _assert_read_only_contract(contract: Contract) -> None:
    text = _contract_text(contract)
    residue = tuple(fragment for fragment in _DML_CONTRACT_LANGUAGE if fragment in text)
    assert residue == (), f"read-only exercise contains DML contract language: {residue}"


def _assert_statement_within_ranking_identity(contract: Contract) -> None:
    text = _contract_text(contract)
    stable_identity = all(
        field in text for field in ("ranking", "userid", "dbid", "toplevel", "queryid")
    )
    documented_display_fallback = (
        "ranking" in text
        and "query" in text
        and any(phrase in text for phrase in ("display key", "not guaranteed", "non-guaranteed"))
    )
    assert stable_identity or documented_display_fallback, (
        "statement ranking must use (ranking, userid, dbid, toplevel, queryid), "
        "or explicitly label (ranking, query) as a non-guaranteed display key"
    )


@pytest.mark.parametrize(
    "lesson",
    CATALOG.lessons("sql"),
    ids=lambda lesson: lesson.id,
)
def test_sql_exercise_contracts_match_across_all_three_surfaces(lesson: Lesson) -> None:
    surfaces = {
        "guide": CATALOG.resolve(lesson.guide_path),
        "learner": CATALOG.resolve(lesson.lesson_path),
        "solution": _markdown_solution(CATALOG, lesson),
    }
    observed = {
        surface: _contracts(
            path.read_text(encoding="utf-8"),
            lesson_id=lesson.id,
            surface=surface,
        )
        for surface, path in surfaces.items()
    }

    assert observed["learner"] == observed["guide"], (
        f"{lesson.id} learner Inputs/Expected/Verify contracts differ from its guide"
    )
    assert observed["solution"] == observed["guide"], (
        f"{lesson.id} Markdown-solution Inputs/Expected/Verify contracts differ from its guide"
    )


def test_sql_05_exercise_5_preserves_unordered_employee_pair_grain() -> None:
    contract = _guide_contract("sql-05", 5)
    text = _contract_text(contract)

    assert "one row per unordered same-department pair" in contract.expected.lower()
    assert "first_employee_id" in text
    assert "second_employee_id" in text
    assert "first_employee_id < second_employee_id" in contract.verify.lower() or (
        "self-pair" in contract.verify.lower() and "mirror" in contract.verify.lower()
    )
    assert "conflict" not in text
    _assert_read_only_contract(contract)


def test_sql_05_executable_solution_removes_self_and_mirrored_pairs() -> None:
    source = _executable_solution("sql-05")

    assert "left_employee.employee_id as first_employee_id" in source
    assert "right_employee.employee_id as second_employee_id" in source
    assert "left_employee.employee_id < right_employee.employee_id" in source


def test_sql_19_exercise_4_preserves_three_row_window_peer_example() -> None:
    contract = _guide_contract("sql-19", 4)
    text = _contract_text(contract)

    assert "three rows" in contract.expected.lower()
    for field in ("row_id", "sort_value", "amount", "rows_sum", "range_sum"):
        assert field in text
    assert "peer" in contract.verify.lower()
    assert "exactly one summary row" not in text
    assert "require exactly one output row" not in text


def test_sql_19_executable_solution_makes_rows_and_range_peers_observable() -> None:
    source = _executable_solution("sql-19")

    assert all(f"({row})" in source for row in ("1, 1, 10", "2, 1, 20", "3, 2, 5"))
    assert re.search(
        r"order by sort_value,\s*row_id\s+"
        r"rows between unbounded preceding and current row",
        source,
    )
    assert re.search(
        r"order by sort_value\s+range between unbounded preceding and current row",
        source,
    )


def test_sql_44_monitoring_contracts_keep_exact_grains_and_read_only_operations() -> None:
    contracts = {number: _guide_contract("sql-44", number) for number in range(1, 7)}
    for contract in contracts.values():
        _assert_read_only_contract(contract)

    exercise_1 = contracts[1]
    assert "currently active sessions" in exercise_1.expected.lower()
    assert "excluding the monitoring query itself" in exercise_1.expected.lower()
    assert "unique `pid`" in exercise_1.verify.lower()

    exercise_2 = contracts[2]
    assert "pg_stat_statements" in _contract_text(exercise_2)
    assert "mean_exec_time" in exercise_2.expected.lower()
    assert "total_exec_time" in exercise_2.expected.lower()
    assert any(phrase in exercise_2.expected.lower() for phrase in ("up to 20", "up to twenty"))
    assert any(phrase in exercise_2.expected.lower() for phrase in ("at most 10", "at most ten"))
    assert any(
        phrase in exercise_2.expected.lower()
        for phrase in ("per ranking", "for each ranking", "per label")
    )
    assert "notice" in exercise_2.verify.lower()
    assert "empty" in exercise_2.verify.lower()
    assert "mean_exec_time" in exercise_2.verify.lower()
    assert "total_exec_time" in exercise_2.verify.lower()
    assert any(phrase in exercise_2.verify.lower() for phrase in ("at most 10", "at most ten"))
    assert "order" in exercise_2.verify.lower()
    _assert_statement_within_ranking_identity(exercise_2)

    exercise_3 = contracts[3]
    assert "one row per `pid`" in exercise_3.expected.lower()
    assert "transaction_age" in _contract_text(exercise_3)
    assert "statement_age" in _contract_text(exercise_3)

    exercise_4 = contracts[4]
    assert "one row per `datname`, `usename`, and `state`" in exercise_4.expected.lower()
    assert "connections" in _contract_text(exercise_4)

    exercise_5 = contracts[5]
    assert "mean_exec_time" in _contract_text(exercise_5)
    assert "total_exec_time" in _contract_text(exercise_5)
    _assert_statement_within_ranking_identity(exercise_5)
    assert "ranking" in exercise_5.verify.lower()
    assert all(
        field in exercise_5.verify.lower() for field in ("userid", "dbid", "toplevel", "queryid")
    ) or (
        "query" in exercise_5.verify.lower()
        and any(
            phrase in exercise_5.verify.lower()
            for phrase in ("display key", "not guaranteed", "non-guaranteed")
        )
    )
    assert "one row per `ranking`." not in exercise_5.expected.lower()
    assert "require unique `ranking`" not in exercise_5.verify.lower()

    exercise_6 = contracts[6]
    assert "one row per `pid`" in exercise_6.expected.lower()
    assert "idle in transaction" in _contract_text(exercise_6)
    assert "transaction_age" in _contract_text(exercise_6)


def test_sql_44_executable_solution_keeps_two_stable_statement_rankings() -> None:
    source = _executable_solution("sql-44")

    for field in ("rank_position", "userid", "dbid", "toplevel", "queryid"):
        assert re.search(rf"^\s*{field}\s+", source, flags=re.MULTILINE)
    assert source.count("row_number() over") == 2
    assert source.count("limit 10") == 2
    assert "'total_exec_time'" in source
    assert "'mean_exec_time'" in source
    assert _count_sql_fragment(source, "ORDER BY ranking, rank_position;") == 2
    assert "pg_stat_statements_reset" not in source


def test_sql_57_forecast_comparisons_keep_model_grain() -> None:
    exercise_1 = _guide_contract("sql-57", 1)
    _assert_read_only_contract(exercise_1)
    exercise_1_text = _contract_text(exercise_1)
    assert "two model rows" in exercise_1.expected.lower()
    assert "`model`" in exercise_1_text
    assert "`mape`" in exercise_1_text
    assert "two" in exercise_1.verify.lower()
    assert "model" in exercise_1.verify.lower()
    assert "mape" in exercise_1.verify.lower()
    assert "exactly one summary row" not in exercise_1_text
    assert "require exactly one output row" not in exercise_1_text

    exercise_4 = _guide_contract("sql-57", 4)
    _assert_read_only_contract(exercise_4)
    exercise_4_text = _contract_text(exercise_4)
    assert "one row per `model_name`." in exercise_4.expected.lower()
    for field in ("model_name", "scored_rows", "mae", "rmse", "mape", "zero_actual_rows"):
        assert field in exercise_4_text
        assert field in exercise_4.verify.lower()
    assert "by `model_name`" in exercise_4.verify.lower()
    assert "by `model_name`, `mae`" not in exercise_4.verify.lower()


def test_sql_57_executable_solution_compares_models_at_model_grain() -> None:
    source = _executable_solution("sql-57", preserve_case=True)

    assert _count_sql_fragment(source, "SELECT 'MA(7)' AS model") == 1
    assert _count_sql_fragment(source, "SELECT 'seasonal naive (lag 7)'") == 1
    assert _count_sql_fragment(source, "UNION ALL") >= 1
    assert _count_sql_fragment(source, "common_scoring_rows AS (") == 1
    assert (
        _count_sql_fragment(
            source, "FROM common_scoring_rows GROUP BY model_name ORDER BY model_name;"
        )
        == 1
    )


@pytest.mark.parametrize(
    "source,fragment",
    [
        ("SELECT 'ma(7)' AS model", "SELECT 'MA(7)' AS model"),
        ("SELECT amount >= 0", "SELECT amount > 0"),
        ("SELECT 100", "SELECT 10"),
        ('SELECT "ID"', 'SELECT "id"'),
        ("SELECT user_id", "SELECT userid"),
    ],
)
def test_sql_layout_comparison_does_not_relax_meaning(source: str, fragment: str) -> None:
    assert _count_sql_fragment(source, fragment) == 0


def test_sql_layout_comparison_accepts_spacing_but_not_a_comment_only_match() -> None:
    fragment = "SELECT 'MA(7)' AS model"
    assert _count_sql_fragment("select\n  'MA(7)' as\n model;", fragment) == 1
    assert _count_sql_fragment("-- SELECT 'MA(7)' AS model\nSELECT 1;", fragment) == 0
