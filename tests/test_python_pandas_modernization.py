"""Independent identity, calendar and parsing oracles for the three pandas units."""

from __future__ import annotations

import itertools
import json
import runpy
from collections import Counter
from collections.abc import Mapping
from datetime import datetime
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pytest

from ds60sqlpy.catalog import Catalog, Lesson
from scripts.audit_lesson_depth import measure_lesson
from scripts.audit_practice import count_practice

pd = pytest.importorskip("pandas")
ROOT = Path(__file__).resolve().parents[1]
PREREQUISITES = {
    5: ("python-pandas-01", "python-19"),
    6: ("python-21", "python-pandas-02", "python-data-02"),
    7: ("python-18", "python-pandas-01", "python-pandas-03"),
}


@lru_cache(maxsize=3)
def reference(number: int) -> dict[str, Any]:
    if number == 7:
        pytest.importorskip("pyarrow")
    return runpy.run_path(
        str(ROOT / f"python/professional/solutions/py_pandas_{number:02d}_solution.py")
    )


@pytest.mark.parametrize("number", [5, 6, 7])
def test_each_complete_surface_preserves_six_teaching_contracts(number: int) -> None:
    stem = f"py_pandas_{number:02d}"
    lesson = Lesson.from_mapping(
        {
            "id": f"python-pandas-{number:02d}",
            "track": "python",
            "day": 88 + number,
            "title": "Pandas data contracts",
            "level": "advanced",
            "phase": "Python data mechanics",
            "estimated_minutes": 180,
            "prerequisites": list(PREREQUISITES[number]),
            "lesson_path": f"python/professional/lessons/{stem}.py",
            "guide_path": f"python/professional/companion-guides/{stem}.md",
            "solution_paths": [
                f"python/professional/solutions/{stem}_solutions.md",
                f"python/professional/solutions/{stem}_solution.py",
            ],
            "dependency_group": "data",
            "network": "offline",
            "runner": "python",
        }
    )
    assert not measure_lesson(Catalog(ROOT, [lesson]), lesson).issues
    for name in (lesson.lesson_path, lesson.guide_path, *lesson.solution_paths):
        assert count_practice(ROOT / name, solution="solutions/" in name) == 6
    learner = runpy.run_path(str(ROOT / lesson.lesson_path))
    learner["worked_examples"]()
    reference(number)["verify_examples"]()


def test_all_small_observation_subsets_roundtrip_with_presence_and_unknowns() -> None:
    functions = reference(5)
    coordinates = [(site, metric) for site in ["a", "b", "c"] for metric in ["x", "y"]]
    for selected in itertools.product([False, True], repeat=len(coordinates)):
        keys = [key for key, keep in zip(coordinates, selected, strict=True) if keep]
        values = [pd.NA if position % 2 else 0 for position in range(len(keys))]
        original = pd.Series(
            pd.array(values, dtype="Float64"),
            index=pd.MultiIndex.from_tuples(keys, names=["site", "metric"]),
            name="value",
        )
        before = original.copy(deep=True)
        grid, presence = functions["observation_grid"](original)
        restored = functions["restore_observations"](grid, presence)
        pd.testing.assert_series_equal(restored, original.sort_index())
        pd.testing.assert_series_equal(original, before)
        for site in grid.index:
            for metric in grid.columns:
                assert bool(presence.loc[site, metric]) == ((site, metric) in keys)
        assert int(presence.to_numpy().sum()) == len(keys)


def test_label_comparison_matches_a_tuple_key_oracle_under_reordering() -> None:
    functions = reference(5)
    left = {("b", "x"): 0, ("a", "x"): None, ("a", "y"): 4}
    right = {("c", "x"): 7, ("a", "y"): 2, ("a", "x"): 9}

    def series(records: Mapping[tuple[str, str], int | None], reverse: bool) -> Any:
        keys = list(records)[:: -1 if reverse else 1]
        return pd.Series(
            pd.array([records[key] for key in keys], dtype="Float64"),
            index=pd.MultiIndex.from_tuples(keys, names=["site", "metric"]),
            name="value",
        )

    for reverse_left, reverse_right in itertools.product([False, True], repeat=2):
        table = functions["aligned_difference"](
            series(left, reverse_left), series(right, reverse_right)
        )
        assert list(table.index) == sorted(left.keys() | right.keys())
        for key, row in table.iterrows():
            assert bool(row.left_present) == (key in left)
            assert bool(row.right_present) == (key in right)
            left_value, right_value = left.get(key), right.get(key)
            if key in left and key in right and left_value is not None and right_value is not None:
                assert row.difference == left_value - right_value
            else:
                assert pd.isna(row.difference)


def test_coordinate_encoding_has_an_independent_json_inverse() -> None:
    keys = [(left, right) for left in ["", "a__b", '"', "λ"] for right in ["c", "b__c", "", "\\"]]
    columns = pd.MultiIndex.from_tuples(keys)
    labels = reference(5)["encode_column_labels"](columns)
    assert labels.is_unique
    assert [tuple(json.loads(label)) for label in labels] == keys


@pytest.mark.parametrize("bad", ["2026-03-08T06:00:00", "2026-02-30T00:00:00Z", "missing", None])
def test_offset_parser_never_guesses_naive_or_invalid_instants(bad: object) -> None:
    with pytest.raises(ValueError):
        reference(6)["parse_instants"]([bad])


def test_local_calendar_counts_match_standard_library_date_assignment() -> None:
    text = [
        "2026-03-08T04:59:59Z",
        "2026-03-08T05:00:00Z",
        "2026-03-09T03:59:59.999999999Z",
        "2026-03-09T04:00:00Z",
        "2026-03-10T04:00:00Z",
    ]
    functions = reference(6)
    instants = functions["parse_instants"](text)
    oracle = Counter(
        datetime.fromisoformat(value).astimezone(ZoneInfo("America/New_York")).date().isoformat()
        for value in text
    )
    result = functions["daily_event_counts"](
        instants[::-1], "America/New_York", "2026-03-07", "2026-03-10"
    )
    assert result.local_day.tolist() == ["2026-03-07", "2026-03-08", "2026-03-09"]
    assert result.event_count.tolist() == [oracle[day] for day in result.local_day]
    assert result.elapsed_hours.tolist() == [24, 23, 24]
    assert result.event_count.sum() == 4


def test_wall_time_default_failures_do_not_silently_repair_and_choices_are_typed() -> None:
    functions = reference(6)
    for text in ["2026-11-01T01:30:00", "2026-03-08T02:30:00"]:
        with pytest.raises(ValueError) as failure:
            functions["localize_wall_times"]([text], "America/New_York")
        assert failure.value.__cause__ is not None
    for choices in [[], [1], ["True"]]:
        with pytest.raises(ValueError):
            functions["localize_wall_times"](["2026-11-01T01:30:00"], "America/New_York", choices)
    with pytest.raises(ValueError):
        functions["localize_wall_times"](["2026-03-08T01:30:00"], "America/New_York", gap=[])


@pytest.mark.parametrize("row", ["id,red,2,3", "id,red", "", "id,,2", ",red,2"])
def test_csv_structure_cannot_shift_into_a_silent_implicit_index(row: str) -> None:
    with pytest.raises(ValueError):
        reference(7)["read_identity_csv"]("record_id,group,amount_cents\n" + row + "\n")


def test_exact_integer_boundaries_and_nullable_identity_roundtrip() -> None:
    functions = reference(7)
    numbers = [-(2**63), -(2**53 + 1), 0, 2**53 + 1, 2**63 - 1]
    text_values = [str(number) for number in numbers] + ["", pd.NA]
    result = functions["strict_int64"](pd.Series(text_values, dtype="string", name="amount"))
    assert result.iloc[:5].tolist() == numbers
    assert result.iloc[5:].isna().all()
    assert str(result.dtype) == "Int64" and result.name == "amount"
    for text in [str(-(2**63) - 1), str(2**63), "1.0", "1e3", " 1", "１"]:
        with pytest.raises(ValueError):
            functions["strict_int64"](pd.Series([text], dtype="string"))


def test_actual_parquet_matches_independent_values_and_rejects_consumer_domain_change() -> None:
    pa = pytest.importorskip("pyarrow")
    pq = pytest.importorskip("pyarrow.parquet")
    functions = reference(7)
    frame = functions["read_identity_csv"](
        'record_id,group,amount_cents\n"00,17",red,9007199254740993\nNA,blue,\n'
    )
    frame["group"] = functions["known_categories"](frame["group"], ("red", "blue", "green"))
    payload = functions["parquet_bytes"](frame)
    decoded = pq.read_table(BytesIO(payload))
    assert decoded.to_pylist() == [
        {"record_id": "00,17", "group": "red", "amount_cents": 9007199254740993},
        {"record_id": "NA", "group": "blue", "amount_cents": None},
    ]
    assert decoded.schema.field("amount_cents").type == pa.int64()
    assert decoded.schema.field("record_id").nullable is False
    with pytest.raises(ValueError, match="domain"):
        functions["read_parquet_payload"](payload, ("red", "green"))


def test_text_states_and_unknown_categories_never_become_indistinguishable() -> None:
    functions = reference(7)
    text = pd.Series(["AB-0007", "xAB-0007x", "AB-０００７", "KA-0007", pd.NA], dtype="string")
    parsed = functions["extract_codes"](text)
    assert parsed.state.tolist() == ["valid", "invalid", "invalid", "invalid", "missing"]
    assert parsed.number.iloc[0] == "0007" and parsed.number.iloc[1:].isna().all()
    with pytest.raises(ValueError):
        functions["known_categories"](
            pd.Series(["red", "purple", pd.NA], dtype="string"), ("red", "blue")
        )
