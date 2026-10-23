"""Validate design-only course plans and compile an offline teaching preview.

This format deliberately cannot register active lessons, runners, or commands.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from ds60sqlpy.catalog import Catalog

TRACK_IDS = ("kubernetes", "deep-learning-tensorflow", "llm-theory", "cpp", "scala-spark")
LEVELS = ("beginner", "intermediate", "advanced")
PROFILES = frozenset(
    {
        "reading",
        "python-core",
        "cpp20",
        "k8s-kind",
        "tensorflow-cpu",
        "llm-torch-cpu",
        "scala-jvm",
        "spark-local-scala",
        "spark-local-python",
    }
)
DATA_MARKER = "/*__JOURNEY_DATA__*/null"


def _text(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context} must be nonempty text.")
    return value


def _object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be an object.")
    return value


def _items(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{context} must be a list.")
    return value


def _texts(value: Any, context: str, *, nonempty: bool = False) -> list[str]:
    result = [_text(item, context) for item in _items(value, context)]
    if nonempty and not result:
        raise ValueError(f"{context} must not be empty.")
    if len(result) != len(set(result)):
        raise ValueError(f"{context} contains duplicate values.")
    return result


def _sample(root: Path, value: Any, context: str) -> str:
    relative = _text(value, context)
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.suffix != ".md":
        raise ValueError(f"{context} must be a relative Markdown sample path.")
    target = (root / path).resolve()
    sample_root = (root / "docs/expansion/samples").resolve()
    if not target.is_relative_to(sample_root) or not target.is_file():
        raise ValueError(f"{context} must name an existing expansion sample.")
    return relative


def load_designs(root: Path) -> list[dict[str, Any]]:
    """Load all five plans and validate references against the real active catalog."""
    catalog = Catalog.load(root)
    active = {lesson.id: lesson for lesson in catalog.lessons()}
    plans: list[dict[str, Any]] = []
    graph = {key: list(lesson.prerequisites) for key, lesson in active.items()}
    plan_dir = root / "docs/expansion/plans"
    if {p.stem for p in plan_dir.glob("*.json")} != set(TRACK_IDS):
        raise ValueError("The design directory must contain exactly the five named track plans.")
    for track_id in TRACK_IDS:
        plan = _object(json.loads((plan_dir / f"{track_id}.json").read_text("utf-8")), track_id)
        if type(plan.get("schema_version")) is not int or plan["schema_version"] != 1:
            raise ValueError(f"{track_id}: unsupported design schema version.")
        if plan.get("id") != track_id or plan.get("status") != "planned":
            raise ValueError(f"{track_id}: designs must retain their ID and planned status.")
        for field in ("title", "summary", "north_star"):
            _text(plan.get(field), f"{track_id}.{field}")
        entry = _texts(plan.get("entry_prerequisites"), f"{track_id}.entry_prerequisites")
        if any(key not in active for key in entry):
            raise ValueError(f"{track_id}: entry prerequisites must name active lessons.")
        profiles = _texts(
            plan.get("runtime_profiles"), f"{track_id}.runtime_profiles", nonempty=True
        )
        if not set(profiles) <= PROFILES:
            raise ValueError(f"{track_id}: unknown planned runtime profile.")
        stages = _items(plan.get("stages"), f"{track_id}.stages")
        if [s.get("id") if isinstance(s, dict) else None for s in stages] != list(LEVELS):
            raise ValueError(
                f"{track_id}: define beginner, intermediate, and advanced stages in order."
            )
        for stage in stages:
            for field in ("title", "outcome"):
                _text(stage.get(field), f"{track_id}.stage.{field}")
        lessons = _items(plan.get("lessons"), f"{track_id}.lessons")
        local_ids: set[str] = set()
        represented: set[str] = set()
        for raw in lessons:
            lesson = _object(raw, f"{track_id}.lesson")
            key = _text(lesson.get("id"), f"{track_id}.lesson.id")
            if not re.fullmatch(r"[a-z][a-z0-9-]*-[0-9]{3}", key) or key in graph:
                raise ValueError(f"{track_id}: invalid or duplicate lesson ID {key!r}.")
            for field in ("title", "outcome", "lab", "verification"):
                _text(lesson.get(field), f"{key}.{field}")
            level = lesson.get("level")
            if level not in LEVELS:
                raise ValueError(f"{key}: unknown level.")
            represented.add(level)
            minutes = lesson.get("minutes")
            if type(minutes) is not int or not 5 <= minutes <= 480:
                raise ValueError(f"{key}: lesson minutes must be an integer from 5 to 480.")
            if lesson.get("runtime") not in profiles:
                raise ValueError(f"{key}: runtime must be declared by its track.")
            _texts(lesson.get("concepts"), f"{key}.concepts", nonempty=True)
            graph[key] = _texts(lesson.get("prerequisites"), f"{key}.prerequisites")
            local_ids.add(key)
        if represented != set(LEVELS):
            raise ValueError(f"{track_id}: all three stages need lessons.")
        capstones = _items(plan.get("capstones"), f"{track_id}.capstones")
        capstone_levels = [
            _text(_object(c, f"{track_id}.capstone").get("level"), f"{track_id}.capstone.level")
            for c in capstones
        ]
        if len(capstones) != 3 or set(capstone_levels) != set(LEVELS):
            raise ValueError(f"{track_id}: capstones must cover all three stages.")
        for raw in capstones:
            capstone = _object(raw, f"{track_id}.capstone")
            for field in ("id", "title", "brief"):
                _text(capstone.get(field), f"{track_id}.capstone.{field}")
            for field in ("deliverables", "acceptance"):
                _texts(capstone.get(field), f"{track_id}.capstone.{field}", nonempty=True)
        pilot = _object(plan.get("pilot"), f"{track_id}.pilot")
        if _text(pilot.get("lesson_id"), f"{track_id}.pilot.lesson_id") not in local_ids:
            raise ValueError(f"{track_id}: pilot must reference a lesson in its track.")
        sample_targets = [
            (root / _sample(root, pilot.get(field), f"{track_id}.pilot.{field}")).resolve()
            for field in ("guide_path", "solution_path")
        ]
        if sample_targets[0] == sample_targets[1]:
            raise ValueError(f"{track_id}: pilot guide and solution must be separate.")
        for field in ("language", "code", "transfer_prompt"):
            _text(pilot.get(field), f"{track_id}.pilot.{field}")
        concept = _object(pilot.get("concept"), f"{track_id}.pilot.concept")
        for field in ("title", "explanation", "worked_example"):
            _text(concept.get(field), f"{track_id}.pilot.concept.{field}")
        prediction = _object(pilot.get("prediction"), f"{track_id}.pilot.prediction")
        for field in ("prompt", "explanation"):
            _text(prediction.get(field), f"{track_id}.pilot.prediction.{field}")
        choices = _texts(prediction.get("choices"), f"{track_id}.prediction.choices", nonempty=True)
        answer = prediction.get("correct_index")
        if len(choices) < 2 or type(answer) is not int or not 0 <= answer < len(choices):
            raise ValueError(f"{track_id}: prediction answer must index at least two choices.")
        if len(_texts(pilot.get("hint_steps"), f"{track_id}.hints")) != 3:
            raise ValueError(f"{track_id}: pilot needs three progressive hints.")
        _texts(pilot.get("rubric"), f"{track_id}.rubric", nonempty=True)
        sources = _items(plan.get("sources"), f"{track_id}.sources")
        if not sources:
            raise ValueError(f"{track_id}: primary references are required.")
        for raw in sources:
            source = _object(raw, f"{track_id}.source")
            for field in ("title", "supports"):
                _text(source.get(field), f"{track_id}.source.{field}")
            parsed = urlsplit(_text(source.get("url"), f"{track_id}.source.url"))
            if parsed.scheme != "https" or not parsed.netloc or parsed.username is not None:
                raise ValueError(f"{track_id}: sources require public HTTPS URLs.")
            try:
                date.fromisoformat(_text(source.get("checked"), f"{track_id}.source.checked"))
            except ValueError as exc:
                raise ValueError(f"{track_id}: sources require valid review dates.") from exc
        plans.append(plan)
    # Iterative DFS avoids recursion limits as the curriculum grows.
    completed: set[str] = set()
    visiting: set[str] = set()
    for start in graph:
        pending = [(start, False)]
        while pending:
            key, leaving = pending.pop()
            if leaving:
                visiting.remove(key)
                completed.add(key)
                continue
            if key in completed:
                continue
            if key in visiting:
                raise ValueError(f"Prerequisite cycle at {key}.")
            if key not in graph:
                raise ValueError(f"Unknown prerequisite {key}.")
            visiting.add(key)
            pending.append((key, True))
            pending.extend((dependency, False) for dependency in reversed(graph[key]))
    return plans


def compile_preview(root: Path) -> str:
    """Return deterministic HTML with JSON safely embedded in a nonexecuting script."""
    plans = load_designs(root)
    template = (root / "src/ds60sqlpy/assets/journey_preview.template.html").read_text("utf-8")
    if template.count(DATA_MARKER) != 1:
        raise ValueError("Journey template must contain exactly one data marker.")
    payload = json.dumps({"schema_version": 1, "tracks": plans}, ensure_ascii=False)
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    payload = payload.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return template.replace(DATA_MARKER, payload)
