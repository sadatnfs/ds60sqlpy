"""Load and query the machine-readable course catalog."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ds60sqlpy.curriculum_framework import (
    DEFAULT_TRACKS,
    RUNNERS,
    infer_runner,
    validate_identifier,
)

Track = str
TRACK_ORDER: dict[Track, int] = {"python": 0, "sql": 1, "bridge": 2}
LESSON_ORDER_OVERRIDES: dict[str, float] = {
    "python-foundations-01": 1.5,
    "python-foundations-02": 3.5,
    "python-foundations-03": 8.5,
    "python-foundations-04": 10.5,
    "sql-found-01": 15.5,
    "sql-found-02": 39.5,
}


def catalog_order_key(
    track: Track,
    day: int,
    lesson_id: str,
    track_order: dict[str, int] | None = None,
) -> tuple[int, float, str]:
    """Return the learner-facing order without changing a stable lesson ID."""

    return (
        (track_order or TRACK_ORDER).get(track, len(track_order or TRACK_ORDER)),
        LESSON_ORDER_OVERRIDES.get(lesson_id, float(day)),
        lesson_id,
    )


@dataclass(frozen=True, slots=True)
class Lesson:
    """One cataloged course lesson."""

    id: str
    track: Track
    day: int
    title: str
    level: str
    phase: str
    estimated_minutes: int
    prerequisites: tuple[str, ...]
    lesson_path: str
    guide_path: str
    solution_paths: tuple[str, ...]
    dependency_group: str
    network: str
    stateful_group: str | None = None
    runner: str = ""
    topics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.runner:
            object.__setattr__(self, "runner", infer_runner(self.lesson_path, self.track))
        if self.runner not in RUNNERS:
            raise ValueError(f"Unsupported lesson runner: {self.runner}")

    @classmethod
    def from_mapping(cls, value: dict[str, Any], *, known_tracks: set[str] | None = None) -> Lesson:
        """Create a lesson from a decoded catalog mapping."""

        raw_track = str(value["track"])
        if raw_track not in (known_tracks if known_tracks is not None else DEFAULT_TRACKS):
            raise ValueError(f"Unsupported lesson track: {raw_track}")

        return cls(
            id=str(value["id"]),
            track=raw_track,
            day=int(value["day"]),
            title=str(value["title"]),
            level=str(value["level"]),
            phase=str(value["phase"]),
            estimated_minutes=int(value["estimated_minutes"]),
            prerequisites=tuple(map(str, value.get("prerequisites", []))),
            lesson_path=str(value["lesson_path"]),
            guide_path=str(value["guide_path"]),
            solution_paths=tuple(map(str, value.get("solution_paths", []))),
            dependency_group=str(value["dependency_group"]),
            network=str(value.get("network", "offline")),
            stateful_group=(
                str(value["stateful_group"]) if value.get("stateful_group") is not None else None
            ),
            runner=str(value.get("runner", infer_runner(str(value["lesson_path"]), raw_track))),
            topics=tuple(map(str, value.get("topics", []))),
        )


def find_repo_root(start: Path | None = None) -> Path:
    """Find the repository root from an explicit path, environment, or current directory."""

    configured = os.environ.get("DS60_REPO_ROOT")
    candidate = (start or (Path(configured) if configured else Path.cwd())).resolve()
    if candidate.is_file():
        candidate = candidate.parent

    for directory in (candidate, *candidate.parents):
        if (
            (directory / "pyproject.toml").is_file()
            and (directory / "python" / "ds-60day").is_dir()
            and (directory / "sql" / "postgres-60day").is_dir()
        ):
            return directory

    raise FileNotFoundError(
        "Could not find the ds60sqlpy repository root. Run from the repository "
        "or set DS60_REPO_ROOT."
    )


class Catalog:
    """In-memory view of ``curriculum/catalog.json``."""

    def __init__(
        self,
        repo_root: Path,
        lessons: Iterable[Lesson],
        *,
        tracks: dict[str, dict[str, str]] | None = None,
        learning_paths: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.tracks = {
            key: dict(value)
            for key, value in (DEFAULT_TRACKS if tracks is None else tracks).items()
        }
        for track, metadata in self.tracks.items():
            validate_identifier(track, "Track ID")
            if not all(
                isinstance(metadata.get(field), str) and metadata[field].strip()
                for field in ("title", "plan")
            ):
                raise ValueError(f"Track {track} needs title and plan metadata.")
        self.learning_paths = dict(learning_paths or {})
        track_order = {track: index for index, track in enumerate(self.tracks)}
        self._lessons = tuple(
            sorted(
                lessons,
                key=lambda lesson: catalog_order_key(
                    lesson.track,
                    lesson.day,
                    lesson.id,
                    track_order,
                ),
            )
        )
        lesson_ids = [lesson.id for lesson in self._lessons]
        if len(lesson_ids) != len(set(lesson_ids)):
            raise ValueError("Catalog contains duplicate lesson IDs.")
        track_days = [(lesson.track, lesson.day) for lesson in self._lessons]
        if len(track_days) != len(set(track_days)):
            raise ValueError("Catalog contains duplicate track/day pairs.")
        self._by_id = {lesson.id: lesson for lesson in self._lessons}
        unknown = {lesson.track for lesson in self._lessons} - self.tracks.keys()
        if unknown:
            raise ValueError(f"Catalog contains unregistered lesson tracks: {sorted(unknown)}")

    @classmethod
    def load(cls, repo_root: Path | None = None) -> Catalog:
        """Load the checked-in catalog."""

        root = find_repo_root(repo_root)
        path = root / "curriculum" / "catalog.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "curriculum/catalog.json is missing. Run python scripts/build_catalog.py."
            ) from exc

        raw_lessons = payload.get("lessons")
        if not isinstance(raw_lessons, list):
            raise ValueError("Catalog field 'lessons' must be a list.")
        tracks = payload.get("tracks", DEFAULT_TRACKS)
        if not isinstance(tracks, dict) or not all(
            isinstance(key, str) and isinstance(value, dict) for key, value in tracks.items()
        ):
            raise ValueError("Catalog tracks must contain registered track metadata.")
        learning_paths = payload.get("learning_paths", {})
        if not isinstance(learning_paths, dict):
            raise ValueError("Catalog learning_paths must be an object.")
        return cls(
            root,
            (Lesson.from_mapping(item, known_tracks=set(tracks)) for item in raw_lessons),
            tracks=tracks,
            learning_paths=learning_paths,
        )

    def __iter__(self) -> Iterator[Lesson]:
        return iter(self._lessons)

    def lessons(self, track: Track | None = None) -> tuple[Lesson, ...]:
        """Return all lessons, optionally restricted to a track."""

        if track is None:
            return self._lessons
        if track not in self.tracks:
            raise ValueError(f"Unknown registered track: {track}")
        return tuple(lesson for lesson in self._lessons if lesson.track == track)

    def get(self, lesson_id: str) -> Lesson:
        """Return a lesson by canonical ID."""

        try:
            return self._by_id[lesson_id]
        except KeyError as exc:
            raise KeyError(f"Unknown lesson ID: {lesson_id}") from exc

    def by_day(self, track: Track, day: int) -> Lesson:
        """Return a lesson by track and ordering number."""

        try:
            return next(
                lesson for lesson in self._lessons if lesson.track == track and lesson.day == day
            )
        except StopIteration as exc:
            raise KeyError(f"Unknown lesson day: {track} {day}") from exc

    def resolve(self, relative_path: str) -> Path:
        """Resolve a catalog path inside the repository."""

        resolved = (self.repo_root / relative_path).resolve()
        if not resolved.is_relative_to(self.repo_root):
            raise ValueError(f"Catalog path escapes repository root: {relative_path}")
        return resolved
