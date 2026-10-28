"""Declarative course extensions and explicit execution capabilities.

Manifests register teaching content. Executable adapters are implemented in
reviewed application code; a JSON document cannot enable a shell command.
"""

from __future__ import annotations

import json
import re
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

DEFAULT_TRACKS: dict[str, dict[str, str]] = {
    "python": {"title": "Python and data science", "plan": "python/PYTHON_TRAINING.md"},
    "sql": {"title": "PostgreSQL", "plan": "sql/ADVANCED_SQL_60DAY_PLAN.md"},
    "bridge": {"title": "Python and PostgreSQL engineering", "plan": "bridge/README.md"},
}


@dataclass(frozen=True, slots=True)
class RunnerDefinition:
    """A language or learning mode, separate from its topic and course track."""

    id: str
    title: str
    file_suffix: str
    kind: str
    executor: str | None


RUNNERS = {
    "python": RunnerDefinition("python", "Python", ".py", "code", "python"),
    "sql": RunnerDefinition("sql", "PostgreSQL", ".sql", "code", "sql"),
    "none": RunnerDefinition("none", "Guided reading and reasoning", ".md", "reading", None),
    "cpp": RunnerDefinition("cpp", "C++", ".cpp", "code", None),
    "scala": RunnerDefinition("scala", "Scala", ".scala", "code", None),
    "kubernetes": RunnerDefinition(
        "kubernetes", "Kubernetes manifests", ".yaml", "operations", None
    ),
}
IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{0,79}$")
TEXT_ARTIFACT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".sql",
    ".hql",
    ".ipynb",
    ".cpp",
    ".cc",
    ".cxx",
    ".h",
    ".hpp",
    ".scala",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".csv",
    ".sh",
}
RUNNER_SOURCE_SUFFIXES = {
    "python": {".py", ".ipynb"},
    "sql": {".sql"},
    "cpp": {".cpp", ".cc", ".cxx", ".h", ".hpp"},
    "scala": {".scala"},
    "kubernetes": {".yaml", ".yml"},
}
NONPORTABLE_PARTS = {
    "cache",
    "__pycache__",
    "credentials",
    "credentials.json",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "pgpass.conf",
}


def is_content_link(path: Path) -> bool:
    """Detect symlinks and Windows junctions on Python 3.11 and 3.12.

    Ordinary cloud-file reparse tags are not directory redirects. Inspect the
    tag rather than rejecting every Windows reparse point or requiring the
    Python 3.12-only Path.is_junction API.
    """
    try:
        information = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(information.st_mode) or getattr(information, "st_reparse_tag", 0) in {
        0xA0000003,
        0xA000000C,
    }


def infer_runner(path: str, track: str = "") -> str:
    """Keep historical lessons compatible while supporting explicit future modes."""
    suffix = PurePosixPath(path).suffix.lower()
    if suffix == ".sql" or track == "sql":
        return "sql"
    if suffix in {".py", ".ipynb"} or track in {"python", "bridge"}:
        return "python"
    if suffix in {".cpp", ".cc", ".cxx", ".h", ".hpp"}:
        return "cpp"
    if suffix == ".scala":
        return "scala"
    if suffix in {".yaml", ".yml"}:
        return "kubernetes"
    return "none"


def validate_identifier(value: object, label: str) -> str:
    """Require stable IDs safe for paths, URLs, progress and manifest references."""
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError(
            f"{label} must be a lowercase identifier using letters, digits and hyphens."
        )
    return value


def validate_content_path(root: Path, value: object, label: str) -> str:
    """Reject absolute, hidden, stateful and escaping extension content paths."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"{label} must be a repository-relative path using forward slashes.")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(
        part == ".." or part.startswith(".") for part in relative.parts
    ):
        raise ValueError(f"{label} must name authored content inside the repository.")
    if any(
        part.casefold() in NONPORTABLE_PARTS
        or part.casefold().endswith((".egg-info", ".dist-info"))
        for part in relative.parts
    ):
        raise ValueError(f"{label} must not name private state or omitted build metadata.")
    target = (root / value).resolve()
    cursor = root
    for part in relative.parts:
        try:
            exact_names = {entry.name for entry in cursor.iterdir()}
        except OSError as exc:
            raise ValueError(f"{label} could not validate the authored path: {value}") from exc
        if part not in exact_names:
            raise ValueError(f"{label} must match the exact filename case: {value}")
        cursor = cursor / part
        if is_content_link(cursor):
            raise ValueError(f"{label} must not traverse a symbolic link or junction.")
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError(f"{label} references missing or escaping content: {value}")
    # A convention keeps future topics inside every source/native/starter bundle.
    if relative.parts[0] not in {"courses", "docs", "python", "sql", "bridge"}:
        raise ValueError(f"{label} must live under courses/, docs/, or an existing course root.")
    return relative.as_posix()


@dataclass(frozen=True)
class ExtensionData:
    """Validated additions read from curriculum/extensions/*.json."""

    tracks: dict[str, dict[str, str]]
    lessons: list[dict[str, Any]]
    learning_paths: dict[str, dict[str, Any]]


def load_extensions(root: Path) -> ExtensionData:
    """Read additive manifests, keeping the original lesson inventory stable."""
    tracks = {key: dict(value) for key, value in DEFAULT_TRACKS.items()}
    lessons: list[dict[str, Any]] = []
    paths: dict[str, dict[str, Any]] = {}
    identifiers: set[str] = set()
    documents: list[tuple[Path, dict[str, Any]]] = []
    extension_root = root / "curriculum/extensions"
    for directory in (root / "curriculum", extension_root):
        if is_content_link(directory):
            raise ValueError("Extension manifests must not traverse a symbolic link or junction.")
    for source in sorted(extension_root.glob("*.json")):
        if is_content_link(source) or not source.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Extension manifests must be regular authored files: {source.name}")
        payload = json.loads(source.read_text(encoding="utf-8-sig"))
        if (
            not isinstance(payload, dict)
            or type(payload.get("schema_version")) is not int
            or payload.get("schema_version") != 1
        ):
            raise ValueError(f"{source.name} must use extension schema_version 1.")
        if set(payload) - {"schema_version", "tracks", "lessons", "learning_paths"}:
            raise ValueError(f"{source.name} has unknown extension fields.")
        raw_tracks = payload.get("tracks", {})
        raw_lessons = payload.get("lessons", [])
        raw_paths = payload.get("learning_paths", {})
        if (
            not isinstance(raw_tracks, dict)
            or not isinstance(raw_lessons, list)
            or not isinstance(raw_paths, dict)
        ):
            raise ValueError(
                f"{source.name} requires tracks/object, lessons/list and learning_paths/object."
            )
        documents.append((source, payload))
        for key, definition in raw_tracks.items():
            track = validate_identifier(key, "Track ID")
            if track == "all":
                raise ValueError("Track ID all is reserved for cross-track searches.")
            if track in tracks:
                raise ValueError(f"Extension must not replace registered track: {track}")
            if not isinstance(definition, dict) or set(definition) != {"title", "plan"}:
                raise ValueError(f"Track {track} requires exactly title and plan.")
            title = definition["title"]
            if not isinstance(title, str) or not title.strip():
                raise ValueError(f"Track {track} requires a nonempty title.")
            plan = validate_content_path(root, definition["plan"], f"Track {track} plan")
            if PurePosixPath(plan).suffix != ".md":
                raise ValueError(f"Track {track} plan must be Markdown.")
            tracks[track] = {"title": title, "plan": plan}
    for source, payload in documents:
        raw_lessons = payload.get("lessons", [])
        raw_paths = payload.get("learning_paths", {})
        for item in raw_lessons:
            if not isinstance(item, dict):
                raise ValueError(f"{source.name} lessons must contain objects.")
            required = {
                "id",
                "track",
                "day",
                "title",
                "level",
                "phase",
                "estimated_minutes",
                "prerequisites",
                "lesson_path",
                "guide_path",
                "solution_paths",
                "dependency_group",
                "network",
                "runner",
            }
            if not required <= item.keys() or set(item) - required - {"topics", "stateful_group"}:
                raise ValueError(
                    f"Extension lesson has missing or unknown fields in {source.name}."
                )
            lesson_id = validate_identifier(item["id"], "Lesson ID")
            if lesson_id in identifiers:
                raise ValueError(f"Duplicate extension lesson ID: {lesson_id}")
            identifiers.add(lesson_id)
            track = validate_identifier(item["track"], f"{lesson_id} track")
            if track not in tracks:
                raise ValueError(f"{lesson_id} uses an unregistered track: {track}")
            if not isinstance(item["runner"], str) or item["runner"] not in RUNNERS:
                raise ValueError(f"{lesson_id} uses an unregistered runner.")
            for field in ("title", "level", "phase", "dependency_group", "network"):
                if not isinstance(item[field], str) or not item[field].strip():
                    raise ValueError(f"{lesson_id} requires nonempty {field}.")
            if (
                type(item["day"]) is not int
                or type(item["estimated_minutes"]) is not int
                or item["estimated_minutes"] <= 0
            ):
                raise ValueError(
                    f"{lesson_id} requires an integer day and positive estimated_minutes."
                )
            if not isinstance(item["prerequisites"], list) or not all(
                isinstance(value, str) for value in item["prerequisites"]
            ):
                raise ValueError(f"{lesson_id} prerequisites must be a list of lesson IDs.")
            topics = item.get("topics", [])
            if item.get("stateful_group") is not None and (
                not isinstance(item["stateful_group"], str) or not item["stateful_group"].strip()
            ):
                raise ValueError(f"{lesson_id} stateful_group must be a nonempty string or null.")
            if not isinstance(topics, list) or not all(
                isinstance(value, str) and value.strip() for value in topics
            ):
                raise ValueError(f"{lesson_id} topics must be a list of nonempty strings.")
            result = dict(item)
            result["topics"] = topics
            for field in ("lesson_path", "guide_path"):
                result[field] = validate_content_path(root, item[field], f"{lesson_id} {field}")
            suffix = PurePosixPath(result["lesson_path"]).suffix.lower()
            if suffix not in TEXT_ARTIFACT_SUFFIXES:
                raise ValueError(f"{lesson_id} requires a supported text learner artifact.")
            if (
                item["runner"] in RUNNER_SOURCE_SUFFIXES
                and suffix not in RUNNER_SOURCE_SUFFIXES[item["runner"]]
            ):
                raise ValueError(f"{lesson_id} learner format does not match its runner.")
            if suffix == ".ipynb" and item["runner"] != "python":
                raise ValueError("Notebook execution currently requires the Python runner.")
            if PurePosixPath(result["guide_path"]).suffix.lower() != ".md":
                raise ValueError(f"{lesson_id} companion guide must be Markdown.")
            solutions = item["solution_paths"]
            if not isinstance(solutions, list) or not solutions:
                raise ValueError(f"{lesson_id} requires a separate explanatory solution.")
            result["solution_paths"] = [
                validate_content_path(root, value, f"{lesson_id} solution") for value in solutions
            ]
            if any(
                PurePosixPath(path).suffix.lower() not in TEXT_ARTIFACT_SUFFIXES
                for path in result["solution_paths"]
            ):
                raise ValueError(f"{lesson_id} solutions must be supported text artifacts.")
            lessons.append(result)
        for key, definition in raw_paths.items():
            path_id = validate_identifier(key, "Learning path ID")
            if (
                path_id in paths
                or not isinstance(definition, dict)
                or set(definition) != {"title", "description", "targets"}
            ):
                raise ValueError(f"Duplicate or malformed learning path: {path_id}")
            if not all(
                isinstance(definition[field], str) and definition[field].strip()
                for field in ("title", "description")
            ):
                raise ValueError(f"Learning path {path_id} requires a title and description.")
            if (
                not isinstance(definition["targets"], list)
                or not definition["targets"]
                or not all(isinstance(value, str) for value in definition["targets"])
            ):
                raise ValueError(f"Learning path {path_id} requires target lesson IDs.")
            paths[path_id] = dict(definition)
    return ExtensionData(tracks, lessons, paths)
