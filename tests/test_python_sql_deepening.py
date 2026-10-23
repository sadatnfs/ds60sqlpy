"""Finite authoring, offline execution and independent algorithm checks."""
from __future__ import annotations

import itertools
import json
from pathlib import Path
import runpy
import socket

import pytest

from ds60sqlpy.catalog import Catalog, Lesson
from scripts.audit_lesson_depth import measure_lesson
from scripts.audit_practice import count_practice

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "curriculum/extensions/python-sql-deepening.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text())
RECORDS = MANIFEST["lessons"]
LESSONS = [Lesson.from_mapping(record) for record in RECORDS]
CANDIDATE = Catalog(ROOT, LESSONS)


def test_additions_have_unique_ids_orders_and_resolvable_prerequisites():
    existing = json.loads((ROOT / "curriculum/catalog.json").read_text())["lessons"]
    own = {record["id"] for record in RECORDS}
    combined = [record for record in existing if record["id"] not in own] + RECORDS
    assert len({record["id"] for record in combined}) == len(combined)
    assert len({(record["track"], record["day"]) for record in combined}) == len(combined)
    known = {record["id"] for record in combined}
    assert all(set(record["prerequisites"]) <= known for record in RECORDS)
    assert MANIFEST["tracks"] == {}


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.id)
def test_each_authored_surface_meets_depth_and_six_distinct_contracts(lesson):
    assert not measure_lesson(CANDIDATE, lesson).issues
    for relative in [lesson.lesson_path, lesson.guide_path, *lesson.solution_paths]:
        path = ROOT / relative
        assert count_practice(path, solution="solutions/" in relative) == 6
        assert "\u2014" not in path.read_text()
    assert lesson.network == "offline"
    if lesson.runner == "sql":
        for relative in [lesson.lesson_path, *[p for p in lesson.solution_paths if p.endswith(".sql")]]:
            source = (ROOT / relative).read_text()
            assert "current_database()" in source and "advanced_sql_training" in source
            assert "BEGIN;" in source and source.rstrip().endswith("ROLLBACK;")


@pytest.mark.parametrize("lesson", [lesson for lesson in LESSONS if lesson.runner == "python"], ids=lambda lesson: lesson.id)
def test_python_examples_and_reference_contracts_run_without_network(lesson, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("Offline deepening lesson attempted network access")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    runpy.run_path(str(ROOT / lesson.lesson_path), run_name="__main__")
    reference = next(path for path in lesson.solution_paths if path.endswith(".py"))
    runpy.run_path(str(ROOT / reference), run_name="__main__")


def test_dynamic_programs_match_exhaustive_small_oracles():
    namespace = runpy.run_path(str(ROOT / "python/professional/solutions/py_algo_04_solution.py"))
    weights, values = [1, 2, 3, 4], [2, 2, 5, 6]
    for capacity in range(9):
        expected = max(
            sum(value * take for value, take in zip(values, mask))
            for mask in itertools.product([0, 1], repeat=len(weights))
            if sum(weight * take for weight, take in zip(weights, mask)) <= capacity
        )
        assert namespace["knapsack_value"](weights, values, capacity) == expected
    jobs = [(0, 2, 4, "a"), (2, 4, 4, "b"), (1, 4, 7, "c"), (4, 5, 1, "d")]
    feasible = []
    for mask in itertools.product([False, True], repeat=len(jobs)):
        selected = sorted((job for job, take in zip(jobs, mask) if take), key=lambda job: job[0])
        if all(left[1] <= right[0] for left, right in zip(selected, selected[1:])):
            feasible.append(sum(job[2] for job in selected))
    optimum, selected_ids = namespace["weighted_schedule"](jobs)
    assert optimum == max(feasible)
    assert sum(job[2] for job in jobs if job[3] in selected_ids) == optimum


def test_indexed_join_matches_nested_occurrence_oracle():
    namespace = runpy.run_path(str(ROOT / "python/professional/solutions/py_algo_01_solution.py"))
    for left in [[], ["a"], ["a", "a", "b"], ["b", "a", "b"]]:
        for right in [[], ["b"], ["a", "b", "a"]]:
            expected = [(i, j) for i, a in enumerate(left) for j, b in enumerate(right) if a == b]
            assert namespace["indexed_pairs"](left, right) == expected
