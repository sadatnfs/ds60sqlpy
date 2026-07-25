"""Local, opt-in learner progress tracking."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from ds60sqlpy.catalog import Catalog, Lesson, Track


@dataclass(frozen=True, slots=True)
class Completion:
    """A completed lesson record."""

    lesson_id: str
    completed_at: str
    notes: str = ""


class ProgressStore:
    """Read and atomically update ``.learning/progress.json``."""

    def __init__(self, catalog: Catalog, path: Path | None = None) -> None:
        self.catalog = catalog
        self.path = path or catalog.repo_root / ".learning" / "progress.json"

    def _payload(self) -> dict[str, Any]:
        if not self.path.is_file():
            return {"schema_version": 1, "completed": {}}
        payload = cast(
            dict[str, Any],
            json.loads(self.path.read_text(encoding="utf-8")),
        )
        if not isinstance(payload.get("completed"), dict):
            raise ValueError(f"Invalid progress file: {self.path}")
        return payload

    def completions(self) -> tuple[Completion, ...]:
        """Return completion records sorted by lesson ID."""

        payload = self._payload()
        known_lesson_ids = {lesson.id for lesson in self.catalog}
        completions: list[Completion] = []
        for lesson_id, value in sorted(payload["completed"].items()):
            if not isinstance(lesson_id, str) or not isinstance(value, dict):
                raise ValueError(f"Invalid completion record in {self.path}")
            if lesson_id not in known_lesson_ids:
                raise ValueError(f"Unknown lesson in progress file: {lesson_id}")
            completed_at = value.get("completed_at")
            notes = value.get("notes", "")
            if not isinstance(completed_at, str) or not isinstance(notes, str):
                raise ValueError(f"Invalid completion record for {lesson_id}")
            completions.append(
                Completion(
                    lesson_id=lesson_id,
                    completed_at=completed_at,
                    notes=notes,
                )
            )
        return tuple(completions)

    def mark_complete(self, lesson_id: str, notes: str = "") -> Completion:
        """Mark a known lesson complete."""

        self.catalog.get(lesson_id)
        payload = self._payload()
        record = Completion(
            lesson_id=lesson_id,
            completed_at=datetime.now(UTC).replace(microsecond=0).isoformat(),
            notes=notes,
        )
        payload["completed"][lesson_id] = {
            "completed_at": record.completed_at,
            "notes": record.notes,
        }
        self._write(payload)
        return record

    def next_lesson(self, track: Track) -> Lesson | None:
        """Return the first incomplete lesson in a track."""

        completed = {item.lesson_id for item in self.completions()}
        return next(
            (lesson for lesson in self.catalog.lessons(track) if lesson.id not in completed),
            None,
        )

    def reset(self) -> None:
        """Remove only this repository's progress file."""

        if self.path.is_file():
            self.path.unlink()
        if self.path.parent.is_dir() and not any(self.path.parent.iterdir()):
            self.path.parent.rmdir()

    def _write(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.path)
