"""Verify evaluation answers through read-only tutor operations, without a model."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.coaching import CoachingService
from ds60sqlpy.mcp_server import TutorAdapter
from ds60sqlpy.progress import ProgressStore

pytest.importorskip("jsonschema", reason="Install the optional MCP extra for adapter validation")
ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "docs" / "mcp-tutor-evaluation.xml"


@pytest.fixture
def tutor(tmp_path: Path) -> Iterator[TutorAdapter]:
    catalog = Catalog.load(ROOT)
    state = tmp_path / "must-not-be-created"
    service = CoachingService(catalog, ProgressStore(catalog, state / "progress.json"))
    yield TutorAdapter(service)
    assert not state.exists(), "read-only evaluation must not create progress or lock files"


def _plan(tutor: TutorAdapter, goal: str) -> dict[str, object]:
    return tutor.invoke("course_plan", {"targets": [goal]})


def _guide(tutor: TutorAdapter, lesson_id: str) -> str:
    guide, mime = tutor.read_resource(f"ds60://course/lesson/{lesson_id}")
    assert mime == "text/markdown"
    return guide


def _find(tutor: TutorAdapter, query: str, track: str) -> str:
    result = tutor.invoke("course_lessons", {"query": query, "track": track, "limit": 5})
    assert result["total"] == 1
    return str(result["lessons"][0]["id"])


def _route_ids(tutor: TutorAdapter, goal: str) -> set[str]:
    result = tutor.invoke("course_plan", {"targets": [goal]})
    return {str(item["id"]) for item in result["lessons"]}


def _verified_answer(tutor: TutorAdapter, index: int) -> str:
    if index == 0:
        paths = tutor.invoke("course_paths", {})
        assert paths["paths"]["sql-foundations"]["targets"] == ("sql-15",)
        plan = tutor.invoke("course_plan", {"targets": ["sql-foundations"]})
        lesson_id = str(plan["lessons"][0]["id"])
        guide = _guide(tutor, lesson_id)
        assert "North" in guide and "one observation" in guide
        assert "prediction" in tutor.prompt(lesson_id)
        return lesson_id
    if index == 1:
        assert "sql-16" in _route_ids(tutor, "sql-16")
        windows = tutor.invoke("course_lesson", {"lesson_id": "sql-16"})
        assert len(windows["prerequisites"]) == 1
        lesson_id = str(windows["prerequisites"][0])
        guide = _guide(tutor, lesson_id).lower()
        assert "primary key" in guide and "sql-15" in guide
        return lesson_id
    if index == 2:
        day_one = tutor.invoke("course_lesson", {"lesson_id": "sql-01"})
        lesson_id = str(day_one["prerequisites"][0])
        assert lesson_id in _route_ids(tutor, "sql-01")
        guide = _guide(tutor, lesson_id)
        assert "Blue blocked" in guide and "42703" in guide
        assert "solutions/" in tutor.prompt(lesson_id)
        lesson = tutor.invoke("course_lesson", {"lesson_id": lesson_id})
        return Path(lesson["lesson_path"]).name
    if index in (3, 4):
        paths = tutor.invoke("course_paths", {})
        lesson_id = str(paths["paths"]["data-product"]["targets"][0])
        route = _route_ids(tutor, "data-product")
        assert {"sql-quality-01", "python-pro-03", lesson_id} <= route
        guide = _guide(tutor, lesson_id)
        if index == 3:
            match = re.search(r"Exactly (\w+) diagnostics", guide)
            assert match is not None
            assert "C missing" in guide and "D unexpected" in guide
            return {"three": "3"}[match[1]]
        assert "Two A lines sum to 10000" in guide and "C" in guide
        digest = re.search(r"\b[a-f0-9]{64}\b", guide)
        assert digest is not None
        return digest[0]
    if index == 5:
        lesson_id = _find(tutor, "cursor", "sql")
        assert lesson_id in _route_ids(tutor, "database-engineering")
        guide = _guide(tutor, lesson_id)
        assert "09:00+00,5" in guide
        match = re.search(r"ID (\d+) with NULL", guide)
        assert match is not None
        return match[1]
    if index == 6:
        lesson_id = _find(tutor, "concurrency", "sql")
        assert lesson_id in _route_ids(tutor, "database-engineering")
        guide = _guide(tutor, lesson_id)
        assert "second SELECT remains `(A,5,1)`" in guide
        assert "prediction" in tutor.prompt(lesson_id)
        match = re.search(r"with `BEGIN ISOLATION LEVEL ([A-Z ]+);`", guide)
        assert match is not None
        return match[1]
    if index == 7:
        day_one = tutor.invoke("course_lesson", {"lesson_id": "sql-01"})
        lesson_id = str(day_one["prerequisites"][0])
        assert lesson_id in _route_ids(tutor, "sql-foundations")
        guide = _guide(tutor, lesson_id)
        assert "effrot" in guide and "prediction" in tutor.prompt(lesson_id)
        match = re.search(r"SQLSTATE (\d{5})", guide)
        assert match is not None
        return match[1]
    if index == 8:
        lesson_id = _find(tutor, "restartable", "python")
        assert lesson_id in _route_ids(tutor, "data-product")
        guide = _guide(tutor, lesson_id).lower()
        assert "checkpoint" in guide and "transaction" in guide
        assert "solutions/" in tutor.prompt(lesson_id)
        return lesson_id
    lesson_id = _find(tutor, "group time", "python")
    assert lesson_id in _route_ids(tutor, "machine-learning")
    guide = _guide(tutor, lesson_id).lower()
    assert "held-out groups" in guide and "forward time windows" in guide
    assert "prediction" in tutor.prompt(lesson_id)
    return lesson_id


def test_evaluation_has_ten_independent_read_only_question_answer_pairs() -> None:
    pairs = ET.parse(EVALUATION).getroot().findall("qa_pair")
    assert len(pairs) == 10
    questions = [pair.findtext("question", "") for pair in pairs]
    assert len(set(questions)) == 10
    assert all(len(question.split()) >= 35 for question in questions)
    assert all(pair.findtext("answer", "").strip() for pair in pairs)


@pytest.mark.parametrize("index", range(10))
def test_evaluation_answers_are_reproducible_through_read_only_adapter(
    tutor: TutorAdapter, index: int
) -> None:
    pairs = ET.parse(EVALUATION).getroot().findall("qa_pair")
    assert _verified_answer(tutor, index) == pairs[index].findtext("answer")
