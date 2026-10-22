"""Local, opt-in learner progress tracking."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any, cast

from ds60sqlpy.catalog import Catalog, Lesson, Track
from ds60sqlpy.state_files import atomic_json_write, locked_update


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
        self._lock = RLock()

    def _payload(self) -> dict[str, Any]:
        try:
            source = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {"schema_version": 1, "completed": {}}
        payload = cast(dict[str, Any], json.loads(source))
        if not isinstance(payload, dict) or not isinstance(payload.get("completed"), dict):
            raise ValueError(f"Invalid progress file: {self.path}")
        return payload

    def completions(self) -> tuple[Completion, ...]:
        """Return completion records sorted by lesson ID."""

        with self._lock:
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
        with self._lock, locked_update(self.path):
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

    def mark_incomplete(self, lesson_id: str) -> bool:
        """Remove one known lesson from the completion set.

        Returns ``True`` when a saved completion was removed and ``False`` when
        the lesson was already incomplete.
        """

        self.catalog.get(lesson_id)
        with self._lock, locked_update(self.path):
            payload = self._payload()
            removed = payload["completed"].pop(lesson_id, None) is not None
            if removed:
                self._write(payload)
            return removed

    def replace_completions(self, lesson_ids: list[str]) -> tuple[Completion, ...]:
        """Replace completions with a validated, de-duplicated lesson list.

        Existing timestamps and notes are retained. Newly completed lessons use
        the same UTC timestamp so imports remain deterministic within one write.
        """

        unique_ids = list(dict.fromkeys(lesson_ids))
        for lesson_id in unique_ids:
            self.catalog.get(lesson_id)
        if not unique_ids:
            self.reset()
            return ()
        with self._lock, locked_update(self.path):
            payload = self._payload()
            saved = payload["completed"]
            completed_at = datetime.now(UTC).replace(microsecond=0).isoformat()
            payload["completed"] = {
                lesson_id: saved.get(
                    lesson_id,
                    {"completed_at": completed_at, "notes": ""},
                )
                for lesson_id in unique_ids
            }
            self._write(payload)
            return self.completions()

    def next_lesson(self, track: Track) -> Lesson | None:
        """Return the first incomplete lesson in a track."""

        completed = {item.lesson_id for item in self.completions()}
        return next(
            (lesson for lesson in self.catalog.lessons(track) if lesson.id not in completed),
            None,
        )

    def reset(self) -> None:
        """Remove only progress state; retain the cross-process lock anchor."""

        with self._lock, locked_update(self.path):
            self.path.unlink(missing_ok=True)

    def _write(self, payload: dict[str, Any]) -> None:
        atomic_json_write(self.path, payload)
