"""Beginner explanations derived from real classroom run outputs.

Fixtures are actual worker and pad payloads from deliberately broken programs.
Only random temporary names, Spark ports and the local interpreter prefix were
replaced with stable placeholders. Cases named ``*-shown`` rerun the same
program after the runner began hiding its own lines (JVM notices, worker
traceback frames, build summaries); both forms must explain alike.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.run_explain import (
    GENERIC_TITLE,
    HINT_LIMIT,
    KINDS,
    RAW_LIMIT,
    TITLE_LIMIT,
    explain_pad_run,
    explain_run,
)

FIXTURES = Path(__file__).parent / "fixtures" / "run_explain"
LEGACY = {"python", "sql"}


def fixture_cases() -> list[Any]:
    return [
        pytest.param(path.stem, case, id=f"{path.stem}:{case['case']}")
        for path in sorted(FIXTURES.glob("*.json"))
        for case in json.loads(path.read_text(encoding="utf-8"))
    ]


def explain(profile: str, case: dict[str, Any]) -> dict[str, object] | None:
    if profile in LEGACY:
        return explain_pad_run(profile, case, case["source"])
    return explain_run(
        profile,
        case["output"],
        case["returncode"],
        stopped=case["stopped"],
        status=case["status"],
        source=case["source"],
    )


@pytest.mark.parametrize(("profile", "case"), fixture_cases())
def test_real_runs_get_bounded_plain_language_explanations(
    profile: str, case: dict[str, Any]
) -> None:
    result = explain(profile, case)
    if case["expected_kind"] is None:
        assert result is None
        return
    assert result is not None
    assert list(result) == ["kind", "title", "line", "column", "hint", "raw"]
    assert result["kind"] in KINDS and result["kind"] == case["expected_kind"]
    assert (result["line"], result["column"]) == (case["expected_line"], case["expected_column"])
    title, hint, raw = result["title"], result["hint"], result["raw"]
    assert isinstance(title, str) and isinstance(hint, str) and isinstance(raw, str)
    assert 0 < len(title) <= TITLE_LIMIT and title.endswith(".")
    assert 0 < len(hint) <= HINT_LIMIT and len(raw) <= RAW_LIMIT
    prose = re.sub(r"`[^`]*`", "", f"{title} {hint}")
    assert "!" not in prose and "mistake" not in prose.lower()
    assert not any("\u2014" in text or "\x00" in text for text in (title, hint, raw))
    assert not re.search(r"/job-\w+/|\.submission-|/workspace/|file://|Lesson\.csproj", raw)
    if result["line"] is not None:
        assert 1 <= int(str(result["line"])) <= case["source"].count("\n") + 1
    if result["kind"] == "unknown" and raw:
        assert title == GENERIC_TITLE


def fixture(profile: str, name: str) -> dict[str, Any]:
    cases = json.loads((FIXTURES / f"{profile}.json").read_text(encoding="utf-8"))
    return next(case for case in cases if case["case"] == name)


def test_success_cancellation_and_unconfirmed_outcomes_need_no_explanation() -> None:
    assert explain_run("python-core", "42\n", 0, status="succeeded") is None
    assert explain_run("python-core", "", -15, status="cancelled") is None
    assert explain_run("go", "", None, status="interrupted") is None
    assert explain_run("python-core", "", None, status="failed") is None
    assert explain_run("python", "42\n", 0) is None


def test_legacy_time_limit_and_controller_timeouts_are_reported_as_timeouts() -> None:
    legacy = explain_run("python", "row 1\n", -9, stopped="time limit")
    module = explain_run("java21", "", None, status="timed_out")
    assert legacy is not None and module is not None
    assert legacy["kind"] == module["kind"] == "timeout" and legacy["line"] is None


def test_temp_paths_are_shortened_to_the_learner_file_name() -> None:
    php = explain("php-cli", fixture("php-cli", "undefined-function"))  # /tmp/job-.../main.php
    csharp = explain("csharp-dotnet", fixture("csharp-dotnet", "missing-semicolon"))
    lesson = explain("sql", fixture("sql", "lesson-missing-column"))
    assert php is not None and str(php["raw"]).endswith("in main.php:3")
    assert csharp is not None and csharp["raw"] == "Program.cs(1,24): error CS1002: ; expected"
    assert lesson is not None and str(lesson["raw"]).startswith("psql:lesson.sql:4: ERROR:")


def test_lines_are_withheld_when_they_cannot_match_the_editor_text() -> None:
    case = fixture("go", "undefined")
    shorter = explain_run("go", case["output"], case["returncode"], status="failed", source="x\n")
    compiled = explain(
        "typescript-node", fixture("typescript-node", "runtime-type-error")
    )  # Node reports compiled/main.mjs, not the TypeScript editor text.
    assert shorter is not None and (shorter["line"], shorter["column"]) == (None, None)
    assert compiled is not None and compiled["line"] is None


def test_runner_error_line_is_preferred_and_used_in_the_copy() -> None:
    case = dict(fixture("python", "key-error-in-function"), error_line=5)
    result = explain_pad_run("python", case, case["source"])
    assert result is not None and (result["line"], result["column"]) == (5, None)
    assert "line 5" in str(result["title"])


def test_unrecognized_failures_fall_back_to_the_last_error_line() -> None:
    result = explain_run(
        "python-core", "starting\nfatal: worker quota reached\n", 2, status="failed"
    )
    assert result is not None
    assert (result["kind"], result["title"]) == ("unknown", GENERIC_TITLE)
    assert result["raw"] == "fatal: worker quota reached"
