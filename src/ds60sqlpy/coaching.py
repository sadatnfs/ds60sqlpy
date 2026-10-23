"""Shared offline coaching operations for the application and MCP adapter."""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from threading import RLock
from typing import Any

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.curriculum_framework import RUNNERS
from ds60sqlpy.lesson_reader import tutor_coaching_prompt
from ds60sqlpy.progress import ProgressStore
from ds60sqlpy.state_files import atomic_json_write, locked_update
from ds60sqlpy.study_plan import build_study_plan, learning_paths

PHASES = ("read", "predict", "attempt", "compare", "explain")
MAX_NOTE_CHARACTERS = 12_000


class CoachingService:
    """Expose catalog-bound teaching content without executing learner code."""

    def __init__(self, catalog: Catalog, progress: ProgressStore | None = None) -> None:
        self.catalog = catalog
        self.progress = progress or ProgressStore(catalog)
        self.path = self.progress.path.with_name("coaching.json")
        self._lock = RLock()

    def paths(self) -> dict[str, Any]:
        """Describe available goals and saved completion IDs without writing."""

        return {
            "paths": {name: asdict(path) for name, path in learning_paths(self.catalog).items()},
            "tracks": self.catalog.tracks,
            "runners": {name: asdict(runner) for name, runner in RUNNERS.items()},
            "completed": [item.lesson_id for item in self.progress.completions()],
            "lesson_count": len(self.catalog.lessons()),
        }

    def plan(self, targets: list[str], weekly_hours: float = 5) -> dict[str, Any]:
        """Return the pending prerequisite closure using explicit local progress."""

        completed = [item.lesson_id for item in self.progress.completions()]
        plan = build_study_plan(
            self.catalog, targets, completed=completed, weekly_hours=weekly_hours
        )
        return {**asdict(plan), "estimated_weeks": plan.estimated_weeks}

    def lesson(self, lesson_id: str) -> dict[str, Any]:
        """Read a guide and learner artifact; never include official solutions."""

        lesson = self.catalog.get(lesson_id)
        guide = self.catalog.resolve(lesson.guide_path).read_text(encoding="utf-8")
        learner = self.catalog.resolve(lesson.lesson_path).read_text(encoding="utf-8")
        learner_code = learner
        notebook_cells: list[dict[str, Any]] = []
        if Path(lesson.lesson_path).suffix == ".ipynb":
            notebook = json.loads(learner)
            fragments: list[str] = []
            next_line = 1
            for index, cell in enumerate(notebook["cells"], 1):
                if cell["cell_type"] != "code":
                    continue
                source = (
                    "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
                )
                if fragments:
                    next_line += 2
                notebook_cells.append({"index": index, "code": source, "start_line": next_line + 1})
                fragment = "# %%\n" + source
                fragments.append(fragment)
                next_line += fragment.count("\n")
            learner_code = "\n\n".join(fragments)
            learner = "\n\n".join(
                "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
                for cell in notebook["cells"]
            )
        completed = {item.lesson_id for item in self.progress.completions()}
        return {
            **asdict(lesson),
            "guide": guide,
            "learner": learner,
            "learner_code": learner_code,
            "notebook_cells": notebook_cells,
            "coaching_prompt": tutor_coaching_prompt(self.catalog, lesson),
            "missing_prerequisites": [p for p in lesson.prerequisites if p not in completed],
            "session": self.session(lesson_id),
        }

    def session(self, lesson_id: str) -> dict[str, Any]:
        """Read one learner session, without creating a file."""

        self.catalog.get(lesson_id)
        with self._lock:
            return dict(self._payload()["lessons"].get(lesson_id, {}))

    def save(self, lesson_id: str, phase: str, note: str) -> dict[str, Any]:
        """Save learner-authored evidence for one phase, preserving other notes."""

        self.catalog.get(lesson_id)
        if phase not in PHASES:
            raise ValueError(f"Choose a coaching phase: {', '.join(PHASES)}.")
        if not isinstance(note, str) or len(note) > MAX_NOTE_CHARACTERS:
            raise ValueError(f"Notes must be text of at most {MAX_NOTE_CHARACTERS} characters.")
        with self._lock, locked_update(self.path):
            payload = self._payload()
            record = payload["lessons"].setdefault(lesson_id, {})
            record[phase] = note
            record["phase"] = phase
            atomic_json_write(self.path, payload)
            return dict(record)

    def hint(self, lesson_id: str, number: int = 1) -> dict[str, Any]:
        """Return one existing guide hint, with a general evidence prompt as fallback."""

        if not 1 <= number <= 50:
            raise ValueError("Hint number must be between 1 and 50.")
        guide = self.catalog.resolve(self.catalog.get(lesson_id).guide_path).read_text(
            encoding="utf-8"
        )
        hints = re.findall(
            r"(?im)^\s*(?:[-*]\s+)?\*\*(?:progressive\s+)?hint(?:\s+\d+)?\s*:\*\*\s*(.+)",
            guide,
        )
        if not hints:
            hints = [
                "State the expected output before changing code. Which smallest input tests it?",
                "Compare the first differing value with the worked example and inspect that step.",
                "Test an empty, missing, or boundary input. Explain the result using your rule.",
            ]
        if number > len(hints):
            return {
                "hint": "No further hints. Compare your attempt with the worked example.",
                "number": number,
                "total": len(hints),
            }
        return {"hint": hints[number - 1], "number": number, "total": len(hints)}

    def solution(self, lesson_id: str, *, reveal: bool = False) -> dict[str, Any]:
        """Read the explanatory solution only after an explicit reveal request."""

        lesson = self.catalog.get(lesson_id)
        if reveal is not True:
            raise ValueError("An explicit reveal request is required to open a solution.")
        path = next((p for p in lesson.solution_paths if p.endswith(".md")), None)
        if path is None:
            raise ValueError("This lesson has no Markdown solution. Use its cataloged reader.")
        return {
            "lesson_id": lesson_id,
            "path": path,
            "content": self.catalog.resolve(path).read_text(encoding="utf-8"),
        }

    def complete(self, lesson_id: str, *, confirmed: bool = False) -> dict[str, Any]:
        """Record self-reported mastery after the learner confirms saved evidence."""

        lesson = self.catalog.get(lesson_id)
        if confirmed is not True:
            raise ValueError("The learner must confirm that their evidence demonstrates the goal.")
        session = self.session(lesson_id)
        for phase in ("predict", "attempt", "explain"):
            if not str(session.get(phase, "")).strip():
                raise ValueError(f"Save your {phase} evidence before completing the lesson.")
        completed = {item.lesson_id for item in self.progress.completions()}
        missing = set(lesson.prerequisites) - completed
        if missing:
            raise ValueError(f"Record prerequisite evidence first: {', '.join(sorted(missing))}.")
        record = self.progress.mark_complete(lesson_id, "Self-reported evidence in coaching.json")
        return {**asdict(record), "evidence_type": "learner-confirmed; not automatically graded"}

    def _payload(self) -> dict[str, Any]:
        try:
            source = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {"schema_version": 1, "lessons": {}}
        payload = json.loads(source)
        if not isinstance(payload, dict) or not isinstance(payload.get("lessons"), dict):
            raise ValueError(
                "Invalid coaching.json. Preserve the file before repairing its format."
            )
        return payload
