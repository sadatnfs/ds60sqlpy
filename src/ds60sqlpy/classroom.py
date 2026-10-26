"""One subject directory over the existing catalog and module storage contracts."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.classroom_runs import ClassroomRunStore
from ds60sqlpy.execution import MAX_CODE_BYTES
from ds60sqlpy.lesson_reader import (
    ReaderTarget,
    reader_relative_path,
    reference_relative_path,
    render_artifact,
)
from ds60sqlpy.reader_content import highlight_source

SUBJECT_DESCRIPTIONS = {
    "python": "Build programming foundations, explore data, and develop reliable Python projects.",
    "sql": "Learn PostgreSQL from the first query to analytical models and database engineering.",
    "bridge": "Connect Python and PostgreSQL through tested, reproducible data workflows.",
}


class ClassroomService:
    """Present a unified view without moving drafts or changing execution boundaries."""

    def __init__(
        self,
        catalog: Catalog,
        dispatch: Callable[[dict[str, Any]], dict[str, Any]],
        targets: dict[Path, ReaderTarget],
        *,
        runs_directory: Path | None = None,
    ) -> None:
        self.catalog = catalog
        self.dispatch = dispatch
        self.targets = targets
        self.legacy_ids = frozenset(lesson.id for lesson in catalog)
        self.runs = ClassroomRunStore(
            catalog, runs_directory or catalog.repo_root / ".learning" / "classroom-runs"
        )

    def action(self, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get("action")
        if action == "classroom-index":
            return self.index()
        if action == "classroom-solutions":
            return self.solutions(payload)
        if action in {"classroom-history", "classroom-run-result"}:
            lesson_id, language = payload.get("lesson_id"), payload.get("language")
            mode = payload.get("mode", "snippet")
            if (
                not isinstance(lesson_id, str)
                or not isinstance(language, str)
                or not isinstance(mode, str)
            ):
                raise ValueError("Choose a lesson, language and source mode for saved runs.")
            if action == "classroom-history":
                return {
                    "history": self.runs.history(
                        lesson_id, language, mode, limit=payload.get("limit", 10)
                    )
                }
            receipt_id = payload.get("receipt_id")
            if not isinstance(receipt_id, str):
                raise ValueError("Choose an existing saved run receipt.")
            return {"receipt": self.runs.get(lesson_id, language, mode, receipt_id)}
        if action == "classroom-highlight":
            source, language = payload.get("source"), payload.get("language", "text")
            if not isinstance(source, str) or len(source.encode("utf-8")) > MAX_CODE_BYTES:
                raise ValueError(f"Syntax preview accepts at most {MAX_CODE_BYTES} UTF-8 bytes.")
            if (
                not isinstance(language, str)
                or re.fullmatch(r"[A-Za-z0-9_+#.-]{1,64}", language) is None
            ):
                raise ValueError("Choose a short code language name for syntax preview.")
            return {"html": highlight_source(source, language)}
        raise ValueError("Unknown classroom action.")

    def index(self) -> dict[str, Any]:
        """Derive all subjects from canonical inputs, retaining stable lesson identities."""
        module_index = self.dispatch({"action": "module-index"})
        progress = self.dispatch({"action": "paths"})
        completed = set(progress["completed"])
        tracks: list[dict[str, Any]] = []
        for key, metadata in self.catalog.tracks.items():
            lessons = [
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "level": "beginner" if lesson.level == "foundation" else lesson.level,
                    "source_level": lesson.level,
                    "status": "authored",
                    "engine": "legacy",
                    "outcome": lesson.phase,
                    "prerequisites": list(lesson.prerequisites),
                    "estimated_minutes": lesson.estimated_minutes,
                    "minutes": lesson.estimated_minutes,
                    "concepts": list(lesson.topics),
                    "learning_mode": "practice",
                    "runtime_profile": lesson.runner,
                    "variants": [],
                    "completed": lesson.id in completed,
                }
                for lesson in self.catalog.lessons(key)
            ]
            tracks.append(
                {
                    "id": key,
                    "title": metadata["title"],
                    "description": SUBJECT_DESCRIPTIONS.get(key, metadata["title"]),
                    "summary": SUBJECT_DESCRIPTIONS.get(key, metadata["title"]),
                    "engine": "legacy",
                    "theme_key": key,
                    "lessons": lessons,
                }
            )
        seen_tracks = set(self.catalog.tracks)
        seen_lessons = set(self.legacy_ids)
        variants = 0
        for track in module_index["tracks"]:
            if track["id"] in seen_tracks:
                raise ValueError("A subject ID is registered in both course catalogs.")
            seen_tracks.add(track["id"])
            normalized = []
            for lesson in track["lessons"]:
                if lesson["id"] in seen_lessons:
                    raise ValueError("A lesson ID is registered in more than one subject.")
                seen_lessons.add(lesson["id"])
                options = lesson.get("variants", [])
                variants += sum(option["id"] != lesson["id"] for option in options)
                normalized.append(
                    {
                        **lesson,
                        "engine": "module",
                        "estimated_minutes": lesson.get("minutes", 0),
                        "concepts": lesson.get("concepts", []),
                    }
                )
            tracks.append(
                {
                    **track,
                    "description": track["summary"],
                    "engine": "module",
                    "theme_key": track["id"],
                    "lessons": normalized,
                }
            )
        for track in tracks:
            track["lesson_count"] = len(track["lessons"])
            track["authored_count"] = sum(
                lesson["status"] == "authored" for lesson in track["lessons"]
            )
            track["estimated_minutes"] = sum(
                lesson["estimated_minutes"]
                for lesson in track["lessons"]
                if lesson["status"] == "authored"
            )
        authored = sum(track["authored_count"] for track in tracks)
        lesson_links = dict(module_index.get("lesson_links", {}))
        for lesson in self.catalog:
            lesson_links["/" + reader_relative_path(lesson.id)] = lesson.id
            for path in (lesson.guide_path, lesson.lesson_path):
                lesson_links["/" + reference_relative_path(path)] = lesson.id
                lesson_links["/" + path] = lesson.id
        return {
            "schema_version": 1,
            "tracks": tracks,
            "subject_count": len(tracks),
            "lesson_count": len(seen_lessons),
            "authored_count": authored,
            "planned_count": len(seen_lessons) - authored,
            "variant_count": variants,
            "lesson_links": lesson_links,
            "active_job": module_index["active_job"],
            "completed": progress["completed"],
            "learning_paths": progress["paths"],
            "publication": "Course catalog with saved code, notes and run history.",
        }

    def solutions(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Apply the same explicit reveal boundary to rendered solutions in both catalogs."""
        if payload.get("reveal") is not True:
            raise ValueError("Explicitly reveal solutions after your own attempt.")
        lesson_id = payload.get("lesson_id")
        if not isinstance(lesson_id, str):
            raise ValueError("Choose a cataloged lesson ID.")
        if lesson_id not in self.legacy_ids:
            return self.dispatch(
                {"action": "module-solutions", "lesson_id": lesson_id, "reveal": True}
            )
        lesson = self.catalog.get(lesson_id)
        return {
            "documents": [
                {
                    "path": path,
                    "html": render_artifact(
                        self.catalog.resolve(path),
                        repo_root=self.catalog.repo_root,
                        targets=self.targets,
                        id_prefix=f"classroom-solution-{position}--",
                        output_path="classroom",
                    ),
                }
                for position, path in enumerate(lesson.solution_paths)
            ]
        }
