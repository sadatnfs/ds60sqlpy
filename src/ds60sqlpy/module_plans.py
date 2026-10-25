"""Validate the five founding subject plans used by the unified classroom.

These plans describe stable lesson identities and prerequisites. Authored files
and executable profiles are admitted separately by ModuleCatalog.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.curriculum_framework import validate_content_path

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


def load_core_plans(root: Path) -> list[dict[str, Any]]:
    """Load the founding plans and validate their prerequisites against the legacy catalog."""
    catalog = Catalog.load(root)
    active = {lesson.id: lesson for lesson in catalog.lessons()}
    plans: list[dict[str, Any]] = []
    graph = {key: list(lesson.prerequisites) for key, lesson in active.items()}
    plan_dir = root / "docs/expansion/plans"
    if {p.stem for p in plan_dir.glob("*.json")} != set(TRACK_IDS):
        raise ValueError(
            "The founding-plan directory must contain exactly its five named subjects."
        )
    for track_id in TRACK_IDS:
        validate_content_path(root, f"docs/expansion/plans/{track_id}.json", "Core subject plan")
        plan = _object(json.loads((plan_dir / f"{track_id}.json").read_text("utf-8")), track_id)
        if type(plan.get("schema_version")) is not int or plan["schema_version"] != 1:
            raise ValueError(f"{track_id}: unsupported subject-plan schema version.")
        if plan.get("id") != track_id:
            raise ValueError(f"{track_id}: subject identity must match its filename.")
        for field in ("title", "summary", "north_star"):
            _text(plan.get(field), f"{track_id}.{field}")
        entry = _texts(plan.get("entry_prerequisites"), f"{track_id}.entry_prerequisites")
        if any(key not in active for key in entry):
            raise ValueError(f"{track_id}: entry prerequisites must name active lessons.")
        profiles = _texts(
            plan.get("runtime_profiles"), f"{track_id}.runtime_profiles", nonempty=True
        )
        if not set(profiles) <= PROFILES:
            raise ValueError(f"{track_id}: unknown runtime profile.")
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
