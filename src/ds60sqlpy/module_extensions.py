"""Additive subject plans and tutorial books without manifest-supplied commands."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ds60sqlpy.curriculum_framework import is_content_link, validate_content_path

LEVELS = ("beginner", "intermediate", "advanced")


def _text(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 10_000:
        raise ValueError(f"Invalid {context}.")
    return value


def _path(root: Path, track: str, value: Any) -> str:
    relative = _text(value, "course path")
    path = Path(relative)
    if (
        path.is_absolute()
        or ".." in path.parts
        or "\\" in relative
        or not relative.startswith(f"courses/{track}/")
    ):
        raise ValueError("Course content must stay in its own subject directory.")
    cursor = root
    for part in path.parts:
        cursor = cursor / part
        if is_content_link(cursor):
            raise ValueError("Course content must not follow symbolic links or junctions.")
    if not cursor.resolve().is_relative_to((root / "courses" / track).resolve()):
        raise ValueError("Course path escaped its subject directory.")
    return relative


def load_tutorial_units(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load additive worked tutorials without changing the original topic contract."""
    path = root / "courses/statistics-ml/tutorials/index.json"
    if not path.exists():
        return [], []
    validate_content_path(root, path.relative_to(root).as_posix(), "Tutorial extension index")
    if path.stat().st_size > 1_000_000:
        raise ValueError("Tutorial index exceeds its size limit.")
    raw = json.loads(path.read_text("utf-8"))
    if (
        not isinstance(raw, dict)
        or type(raw.get("schema_version")) is not int
        or raw["schema_version"] != 1
        or raw.get("mode") != "tutorial"
        or not isinstance(raw.get("units"), list)
        or not 1 <= len(raw["units"]) <= 200
    ):
        raise ValueError("Invalid tutorial extension index.")
    plans, authored = [], []
    seen = set()
    for unit in raw["units"]:
        if not isinstance(unit, dict):
            raise ValueError("Invalid tutorial extension unit.")
        key = _text(unit.get("id"), "tutorial ID")
        if not re.fullmatch(r"statistics-[a-z][a-z0-9-]*-[0-9]{3}", key) or key in seen:
            raise ValueError("Invalid or duplicate tutorial extension ID.")
        seen.add(key)
        if (
            unit.get("profile") not in {"python-core", "bayesian-cpu"}
            or unit.get("mode") != "tutorial"
            or unit.get("network") != "offline"
            or unit.get("level") not in LEVELS
            or type(unit.get("minutes")) is not int
            or not 5 <= unit["minutes"] <= 480
        ):
            raise ValueError("Invalid tutorial extension runtime, stage or duration.")
        for field in ("title", "outcome", "rationale"):
            _text(unit.get(field), field)
        for field in ("prerequisites", "concepts", "dependencies", "expected_outputs"):
            values = unit.get(field)
            if (
                not isinstance(values, list)
                or len(values) > 100
                or any(not isinstance(v, str) or not v.strip() or len(v) > 2000 for v in values)
                or len(values) != len(set(values))
            ):
                raise ValueError(f"Invalid tutorial extension {field}.")
        if not unit["concepts"] or not unit["expected_outputs"]:
            raise ValueError("Tutorial extensions need concepts and observable output.")
        guide = _path(root, "statistics-ml", unit.get("chapter_path"))
        examples = unit.get("example_paths")
        if not isinstance(examples, list) or not 1 <= len(examples) <= 8:
            raise ValueError("Tutorial extensions need bounded examples.")
        sources = [_path(root, "statistics-ml", value) for value in examples]
        if (
            Path(guide).suffix != ".md"
            or any(Path(p).suffix != ".py" for p in sources)
            or len(sources) != len(set(sources))
        ):
            raise ValueError("Tutorial extensions need distinct Markdown and Python sources.")
        plans.append(
            {
                "id": key,
                "title": unit["title"],
                "level": unit["level"],
                "minutes": unit["minutes"],
                "prerequisites": unit["prerequisites"],
                "runtime": unit["profile"],
                "concepts": unit["concepts"],
                "outcome": unit["outcome"],
                "lab": unit["rationale"],
                "verification": (
                    "Worked tutorial with explained output; no exam or mastery grading."
                ),
                "learning_mode": "tutorial",
                "dependencies": unit["dependencies"],
                "expected_outputs": unit["expected_outputs"],
            }
        )
        if not all((root / p).is_file() for p in [guide, *sources]):
            continue
        item = {
            "id": key,
            "status": "authored",
            "language": "python",
            "runtime_profile": unit["profile"],
            "guide_path": guide,
            "source_path": sources[0],
            "solution_paths": [],
            "verification_id": None,
        }
        if len(sources) > 1:
            item["variants"] = [
                {
                    "id": f"example-{i}",
                    "title": f"Example {i}",
                    "language": "python",
                    "runtime_profile": unit["profile"],
                    "source_path": p,
                    "solution_paths": [],
                    "verification_id": None,
                }
                for i, p in enumerate(sources[1:], 2)
            ]
        authored.append(item)
    return plans, authored


def load_book(root: Path) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """Validate metadata even for unwritten chapters; expose only complete file pairs."""
    path = root / "courses/statistics-ml/manifest.json"
    if not path.exists():
        return None
    validate_content_path(root, path.relative_to(root).as_posix(), "Tutorial manifest")
    raw = json.loads(path.read_text("utf-8"))
    if (
        not isinstance(raw, dict)
        or type(raw.get("schema_version")) is not int
        or raw["schema_version"] != 1
        or raw.get("id") != "statistics-ml"
        or raw.get("mode") != "tutorial"
    ):
        raise ValueError("Invalid statistics tutorial manifest.")
    chapters = raw.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        raise ValueError("The tutorial needs chapter metadata.")
    labels: dict[str, str] = {}
    coverage = root / "courses/statistics-ml/coverage.json"
    if coverage.exists():
        validate_content_path(root, coverage.relative_to(root).as_posix(), "Tutorial coverage")
        coverage_data = json.loads(coverage.read_text("utf-8"))
        if not isinstance(coverage_data, dict) or not isinstance(coverage_data.get("topics"), list):
            raise ValueError("Invalid tutorial coverage index.")
        for topic in coverage_data["topics"]:
            if not isinstance(topic, dict):
                raise ValueError("Invalid tutorial topic.")
            topic_id = _text(topic.get("id"), "topic identity")
            if topic_id in labels:
                raise ValueError("Duplicate tutorial topic identity.")
            labels[topic_id] = _text(topic.get("label"), "topic label")
    lessons, authored = [], []
    ids: set[str] = set()
    for chapter in chapters:
        if not isinstance(chapter, dict):
            raise ValueError("Invalid tutorial chapter.")
        key = _text(chapter.get("id"), "chapter ID")
        if not re.fullmatch(r"statistics-[0-9]{3}", key) or key in ids:
            raise ValueError("Invalid or duplicate tutorial chapter ID.")
        ids.add(key)
        title = _text(chapter.get("title"), "chapter title")
        level = {
            "foundation": "beginner",
            "intermediate": "intermediate",
            "advanced": "advanced",
        }.get(str(chapter.get("level")))
        if level is None:
            raise ValueError("Invalid tutorial stage.")
        minutes = chapter.get("minutes")
        prereqs = chapter.get("prerequisites")
        topics = chapter.get("topic_ids")
        if (
            type(minutes) is not int
            or not 5 <= minutes <= 480
            or not isinstance(prereqs, list)
            or not all(isinstance(p, str) for p in prereqs)
            or not isinstance(topics, list)
            or not topics
            or not all(isinstance(t, str) for t in topics)
        ):
            raise ValueError("Invalid tutorial prerequisites, duration or topics.")
        guide = _path(root, "statistics-ml", chapter.get("chapter_path"))
        examples = chapter.get("example_paths")
        if not isinstance(examples, list) or not 1 <= len(examples) <= 8:
            raise ValueError("Each tutorial chapter needs a bounded example list.")
        sources = [_path(root, "statistics-ml", example) for example in examples]
        if (
            Path(guide).suffix != ".md"
            or any(Path(p).suffix != ".py" for p in sources)
            or len(set(sources)) != len(sources)
        ):
            raise ValueError("Tutorial chapters need separate Markdown and Python files.")
        lessons.append(
            {
                "id": key,
                "title": title,
                "level": level,
                "minutes": minutes,
                "prerequisites": prereqs,
                "runtime": "python-core",
                "concepts": [labels.get(topic, topic) for topic in topics],
                "outcome": f"Understand {title.lower()}, assumptions and interpretation.",
                "lab": (
                    "Read the theory and worked examples, then optionally run and adapt "
                    "the Python demonstrations."
                ),
                "verification": (
                    "Tutorial reading and illustrative examples. No exams, problem sets "
                    "or mastery grading."
                ),
                "learning_mode": "tutorial",
            }
        )
        if not all((root / p).is_file() for p in [guide, *sources]):
            continue
        item: dict[str, Any] = {
            "id": key,
            "status": "authored",
            "language": "python",
            "runtime_profile": "python-core",
            "guide_path": guide,
            "source_path": sources[0],
            "solution_paths": [],
            "verification_id": None,
        }
        if len(sources) > 1:
            item["variants"] = [
                {
                    "id": f"example-{i}",
                    "title": f"Example {i}",
                    "language": "python",
                    "runtime_profile": "python-core",
                    "source_path": p,
                    "solution_paths": [],
                    "verification_id": None,
                }
                for i, p in enumerate(sources[1:], 2)
            ]
        authored.append(item)
    extra_plans, extra_authored = load_tutorial_units(root)
    lessons.extend(extra_plans)
    authored.extend(extra_authored)
    plan = {
        "id": "statistics-ml",
        "title": _text(raw.get("title"), "tutorial title"),
        "summary": (
            "A theory and code companion covering statistical reasoning, "
            "modeling, experimentation, causality and machine learning. Includes "
            "worked Python demonstrations and explained "
            "interview questions."
        ),
        "learning_mode": "tutorial",
        "stages": [{"id": level, "title": level.title()} for level in LEVELS],
        "pilot": {"lesson_id": lessons[0]["id"]},
        "lessons": lessons,
    }
    return plan, {"schema_version": 1, "track_id": "statistics-ml", "lessons": authored}


def load_extra_plans(root: Path, profiles: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    plans: list[dict[str, Any]] = []
    manifests: dict[str, Any] = {}
    for path in sorted((root / "courses").glob("*/track.json")):
        validate_content_path(root, path.relative_to(root).as_posix(), "Subject plan")
        plan = json.loads(path.read_text("utf-8"))
        track = path.parent.name
        if (
            not re.fullmatch(r"[a-z][a-z0-9-]{0,60}", track)
            or not isinstance(plan, dict)
            or type(plan.get("schema_version")) is not int
            or plan["schema_version"] != 1
            or plan.get("id") != track
        ):
            raise ValueError("Invalid additive subject plan.")
        for field in ("title", "summary"):
            _text(plan.get(field), field)
        rows = plan.get("lessons")
        if not isinstance(rows, list) or not rows:
            raise ValueError("Subject plans need lessons.")
        for row in rows:
            if not isinstance(row, dict) or not re.fullmatch(
                r"[a-z][a-z0-9-]*-[0-9]{3}", _text(row.get("id"), "lesson ID")
            ):
                raise ValueError("Invalid subject lesson ID.")
            for field in ("title", "outcome", "lab", "verification"):
                _text(row.get(field), field)
            if (
                row.get("level") not in LEVELS
                or row.get("runtime") not in profiles
                or type(row.get("minutes")) is not int
                or not 5 <= row["minutes"] <= 480
            ):
                raise ValueError("Invalid subject lesson stage, runtime or duration.")
            for field in ("prerequisites", "concepts"):
                if (
                    not isinstance(row.get(field), list)
                    or not all(isinstance(v, str) and v for v in row[field])
                    or len(set(row[field])) != len(row[field])
                ):
                    raise ValueError(f"Invalid subject lesson {field}.")
        if {row["level"] for row in rows} != set(LEVELS):
            raise ValueError("Subject plans must cover all three learning stages.")
        plan["stages"] = [{"id": level, "title": level.title()} for level in LEVELS]
        plan["pilot"] = {"lesson_id": rows[0]["id"]}
        mode = plan.get("learning_mode", "practice")
        if not isinstance(mode, str) or mode not in {"practice", "tutorial"}:
            raise ValueError("Invalid subject learning mode.")
        plan["learning_mode"] = mode
        plans.append(plan)
    book = load_book(root)
    if book is not None:
        plan, manifest = book
        plans.append(plan)
        manifests[plan["id"]] = manifest
    return plans, manifests


def validate_graph(plans: list[dict[str, Any]], legacy_ids: set[str]) -> None:
    tracks: set[str] = set()
    graph: dict[str, list[str]] = {}
    for plan in plans:
        if plan["id"] in tracks:
            raise ValueError("Duplicate subject identity.")
        tracks.add(plan["id"])
        for row in plan["lessons"]:
            if row["id"] in graph or row["id"] in legacy_ids:
                raise ValueError("Duplicate lesson identity.")
            graph[row["id"]] = row["prerequisites"]
    complete = set(legacy_ids)
    visiting: set[str] = set()
    for key in graph:
        stack = [(key, False)]
        while stack:
            current, leave = stack.pop()
            if leave:
                visiting.remove(current)
                complete.add(current)
            elif current in complete:
                continue
            elif current in visiting or current not in graph:
                raise ValueError(f"Unknown or cyclic prerequisite {current}.")
            else:
                visiting.add(current)
                stack.append((current, True))
                stack.extend((p, False) for p in reversed(graph[current]))
