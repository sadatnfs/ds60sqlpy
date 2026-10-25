"""Authored expansion modules, separate from the published legacy catalog.

The design graph remains visible, but only reviewed authored file manifests can
supply source to the explicit module lab. No manifest can supply a command.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.curriculum_framework import is_content_link, validate_content_path
from ds60sqlpy.journey_design import load_designs
from ds60sqlpy.module_extensions import load_extra_plans, validate_graph
from ds60sqlpy.state_files import atomic_json_write, locked_update

LANGUAGES = {
    "reading": frozenset({"markdown"}),
    "python-core": frozenset({"python"}),
    "tensorflow-cpu": frozenset({"python"}),
    "llm-torch-cpu": frozenset({"python"}),
    "cpp20": frozenset({"cpp"}),
    "c17": frozenset({"c"}),
    "go": frozenset({"go"}),
    "csharp-dotnet": frozenset({"csharp"}),
    "rust-stable": frozenset({"rust"}),
    "swift-linux": frozenset({"swift"}),
    "javascript-browser": frozenset({"javascript"}),
    "html-browser": frozenset({"html"}),
    "php-cli": frozenset({"php"}),
    "cuda-cpp": frozenset({"cpp"}),
    "cuda-python": frozenset({"python"}),
    "pytorch-cuda": frozenset({"python"}),
    "tensorflow-cuda": frozenset({"python"}),
    "java21": frozenset({"java"}),
    "javascript-node": frozenset({"javascript"}),
    "typescript-node": frozenset({"typescript"}),
    "scala-jvm": frozenset({"scala"}),
    "spark-local-scala": frozenset({"scala"}),
    "spark-local-python": frozenset({"python"}),
    "k8s-kind": frozenset({"yaml"}),
}
VERIFIERS = frozenset(
    {
        "tf-gradient-v1",
        "llm-causal-attention-v1",
        "cpp-ownership-v1",
        "spark-rows-v1",
        "k8s-readiness-v1",
    }
)
MAX_SOURCE_BYTES = 48_000


@dataclass(frozen=True)
class ModuleLesson:
    id: str
    track_id: str
    language: str
    runtime_profile: str
    guide_path: str
    source_path: str
    solution_paths: tuple[str, ...]
    verification_id: str | None
    learning_mode: str = "practice"


class ModuleCatalog:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        extra, manifests = load_extra_plans(self.root, set(LANGUAGES))
        self.plans = [*load_designs(self.root), *extra]
        validate_graph(self.plans, {lesson.id for lesson in Catalog.load(self.root).lessons()})
        self.planned = {
            lesson["id"]: {**lesson, "track_id": plan["id"]}
            for plan in self.plans
            for lesson in plan["lessons"]
        }
        self.canonical_ids = frozenset(self.planned)
        self.variant_options: dict[str, list[dict[str, str]]] = {}
        self.lessons: dict[str, ModuleLesson] = {}
        for plan in self.plans:
            track = plan["id"]
            manifest = self.root / "courses" / track / "lessons.json"
            learning_mode = plan.get("learning_mode", "practice")
            if track in manifests:
                payload = manifests[track]
            else:
                if not manifest.exists():
                    continue
                validate_content_path(
                    self.root, manifest.relative_to(self.root).as_posix(), "Module manifest"
                )
                payload = json.loads(manifest.read_text("utf-8"))
            if (
                not isinstance(payload, dict)
                or type(payload.get("schema_version")) is not int
                or payload["schema_version"] != 1
                or payload.get("track_id") != track
                or not isinstance(payload.get("lessons"), list)
            ):
                raise ValueError(f"Invalid module manifest for {track}.")
            expanded: list[dict[str, Any]] = []
            for raw in payload["lessons"]:
                if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
                    raise ValueError("Invalid authored lesson record.")
                base_id = raw["id"]
                if base_id not in self.canonical_ids:
                    raise ValueError("A module manifest must name a planned canonical lesson.")
                base = {key: value for key, value in raw.items() if key != "variants"}
                expanded.append(base)
                language_title = {
                    "scala": "Scala",
                    "python": "Python",
                    "cpp": "C++",
                    "c": "C",
                    "go": "Go",
                    "csharp": "C#",
                    "rust": "Rust",
                    "swift": "Swift",
                    "java": "Java",
                    "javascript": "JavaScript",
                    "html": "HTML and CSS",
                    "php": "PHP",
                    "typescript": "TypeScript",
                    "yaml": "YAML",
                    "markdown": "Reading",
                }.get(str(raw.get("language")), "Source")
                self.variant_options[base_id] = [{"id": base_id, "title": language_title}]
                variants = raw.get("variants", [])
                if not isinstance(variants, list) or len(variants) > 8:
                    raise ValueError("Module variants must be a bounded list.")
                for variant in variants:
                    if not isinstance(variant, dict) or set(variant) != {
                        "id",
                        "title",
                        "language",
                        "runtime_profile",
                        "source_path",
                        "solution_paths",
                        "verification_id",
                    }:
                        raise ValueError("Invalid module variant fields.")
                    label, title = variant["id"], variant["title"]
                    if (
                        not isinstance(label, str)
                        or not re.fullmatch(r"[a-z][a-z0-9-]{0,24}", label)
                        or not isinstance(title, str)
                        or not title.strip()
                        or len(title) > 80
                    ):
                        raise ValueError("Invalid module variant identity or title.")
                    alias = base_id + "@" + label
                    if alias in self.planned:
                        raise ValueError("Duplicate module variant identity.")
                    self.planned[alias] = {
                        **self.planned[base_id],
                        "id": alias,
                        "base_id": base_id,
                        "title": self.planned[base_id]["title"] + " · " + title,
                    }
                    self.variant_options[base_id].append({"id": alias, "title": title})
                    expanded.append(
                        {
                            **base,
                            **{
                                key: value
                                for key, value in variant.items()
                                if key not in {"id", "title"}
                            },
                            "id": alias,
                        }
                    )
            for item in expanded:
                if not isinstance(item, dict) or set(item) != {
                    "id",
                    "status",
                    "language",
                    "runtime_profile",
                    "guide_path",
                    "source_path",
                    "solution_paths",
                    "verification_id",
                }:
                    raise ValueError(f"Unexpected module lesson fields in {track}.")
                key = item["id"]
                if (
                    not isinstance(key, str)
                    or key not in self.planned
                    or self.planned[key]["track_id"] != track
                    or key in self.lessons
                    or item["status"] != "authored"
                ):
                    raise ValueError(f"Invalid or duplicate authored lesson in {track}.")
                profile, language = item["runtime_profile"], item["language"]
                if (
                    not isinstance(profile, str)
                    or profile not in LANGUAGES
                    or not isinstance(language, str)
                    or language not in LANGUAGES[profile]
                ):
                    raise ValueError(f"Invalid language/profile for {key}.")
                verifier = item["verification_id"]
                if verifier is not None and (
                    not isinstance(verifier, str) or verifier not in VERIFIERS
                ):
                    raise ValueError(f"Unknown verifier for {key}.")
                if not isinstance(item["solution_paths"], list) or (
                    learning_mode != "tutorial" and not item["solution_paths"]
                ):
                    raise ValueError(f"Missing explanatory solutions for {key}.")
                paths = [
                    validate_content_path(self.root, item[field], f"{key}.{field}")
                    for field in ("guide_path", "source_path")
                ]
                solutions = tuple(
                    validate_content_path(self.root, value, f"{key}.solution")
                    for value in item["solution_paths"]
                )
                for value in (*paths, *solutions):
                    if not value.startswith(f"courses/{track}/"):
                        raise ValueError(f"{key} must use its own authored course directory.")
                if paths[0] == paths[1] or len({*paths, *solutions}) != len(paths) + len(solutions):
                    raise ValueError(f"{key} source, guide, and solutions must be separate.")
                if Path(paths[0]).suffix != ".md" or (
                    learning_mode != "tutorial"
                    and not any(Path(p).suffix == ".md" for p in solutions)
                ):
                    raise ValueError(f"{key} requires Markdown teaching and explanatory solutions.")
                if learning_mode != "tutorial" and profile != "reading" and len(solutions) < 2:
                    raise ValueError(f"{key} needs executable and explanatory solutions.")
                verifier_profiles = {
                    "tf-gradient-v1": {"tensorflow-cpu"},
                    "llm-causal-attention-v1": {"python-core"},
                    "cpp-ownership-v1": {"cpp20"},
                    "spark-rows-v1": {"spark-local-scala", "spark-local-python"},
                    "k8s-readiness-v1": {"k8s-kind"},
                }
                if verifier is not None and profile not in verifier_profiles[verifier]:
                    raise ValueError(f"{key} verifier does not match its runtime profile.")
                source = self.root / paths[1]
                suffixes = {
                    "python": {".py"},
                    "cpp": {".cpp", ".cc", ".cxx"},
                    "c": {".c"},
                    "go": {".go"},
                    "csharp": {".cs"},
                    "rust": {".rs"},
                    "swift": {".swift"},
                    "scala": {".scala"},
                    "java": {".java"},
                    "javascript": {".mjs", ".js"},
                    "typescript": {".mts", ".ts"},
                    "yaml": {".yaml", ".yml"},
                    "markdown": {".md"},
                    "html": {".html"},
                    "php": {".php"},
                }
                if (
                    source.suffix not in ({".cu"} if profile == "cuda-cpp" else suffixes[language])
                    or source.stat().st_size > MAX_SOURCE_BYTES
                ):
                    raise ValueError(f"Invalid source format/size for {key}.")
                self.lessons[key] = ModuleLesson(
                    key,
                    track,
                    language,
                    profile,
                    paths[0],
                    paths[1],
                    solutions,
                    verifier,
                    learning_mode,
                )

    def content_path(self, relative: str, maximum: int = 1_000_000) -> Path:
        validated = validate_content_path(self.root, relative, "Module content")
        path = self.root / validated
        if path.stat().st_size > maximum:
            raise ValueError("The authored module content exceeds its size limit.")
        return path

    def source(self, lesson: ModuleLesson) -> str:
        path = self.content_path(lesson.source_path, MAX_SOURCE_BYTES)
        with path.open("rb") as stream:
            data = stream.read(MAX_SOURCE_BYTES + 1)
        if len(data) > MAX_SOURCE_BYTES:
            raise ValueError("The module source exceeds its UTF-8 size limit.")
        return data.decode("utf-8")

    def get(self, lesson_id: object) -> ModuleLesson:
        if not isinstance(lesson_id, str) or lesson_id not in self.lessons:
            raise ValueError("Choose an authored module lesson, not a planned placeholder.")
        return self.lessons[lesson_id]

    def index(self) -> dict[str, Any]:
        tracks = []
        for plan in self.plans:
            lessons = []
            for planned in plan["lessons"]:
                authored = self.lessons.get(planned["id"])
                lessons.append(
                    {
                        **planned,
                        "status": "authored" if authored else "planned",
                        "learning_mode": plan.get("learning_mode", "practice"),
                        "variants": self.variant_options.get(planned["id"], []),
                        "runtime_profile": authored.runtime_profile
                        if authored
                        else planned["runtime"],
                    }
                )
            tracks.append(
                {
                    "id": plan["id"],
                    "title": plan["title"],
                    "summary": plan["summary"],
                    "stages": plan["stages"],
                    "pilot_id": plan["pilot"]["lesson_id"],
                    "lessons": lessons,
                }
            )
        return {
            "schema_version": 1,
            "tracks": tracks,
            "authored_count": len(self.canonical_ids.intersection(self.lessons)),
            "planned_count": len(self.canonical_ids),
            "publication": (
                "Authored modules and tutorial books; published legacy catalog remains separate."
            ),
        }


class ModuleState:
    """A versioned sidecar preserves drafts without rewriting legacy progress."""

    def __init__(self, catalog: ModuleCatalog, directory: Path | None = None) -> None:
        self.catalog = catalog
        self.directory = (directory or catalog.root / ".learning" / "modules").absolute()
        self.path = self.directory / "sessions.json"
        self.boundary = self.directory.parent.resolve()

    def safe_path(self, path: Path) -> Path:
        relative = path.relative_to(self.directory)
        cursor = self.directory
        for part in (None, *relative.parts):
            if part is not None:
                cursor = cursor / part
            if is_content_link(cursor):
                raise ValueError("Module state must not follow a symbolic link or junction.")
        if not path.resolve().is_relative_to(self.boundary):
            raise ValueError("Module state escaped its configured learner directory.")
        lock = path.with_name(path.name + ".lock")
        if is_content_link(lock):
            raise ValueError("Module state lock must not be a symbolic link.")
        return path

    def _payload(self) -> dict[str, Any]:
        try:
            value = json.loads(self.safe_path(self.path).read_text("utf-8"))
        except FileNotFoundError:
            return {"schema_version": 1, "lessons": {}}
        if (
            not isinstance(value, dict)
            or value.get("schema_version") != 1
            or not isinstance(value.get("lessons"), dict)
        ):
            raise ValueError("Module progress is invalid. Preserve it and restore a known backup.")
        return value

    @staticmethod
    def validate_record(record: object) -> dict[str, Any]:
        if not isinstance(record, dict) or not set(record) <= {
            "source",
            "prediction",
            "explanation",
            "review",
        }:
            raise ValueError("Invalid module session; preserve it before restoring a backup.")
        for key, value in record.items():
            maximum = MAX_SOURCE_BYTES if key == "source" else 12_000
            if not isinstance(value, str) or len(value.encode("utf-8")) > maximum:
                raise ValueError("Invalid module session text; it was not overwritten.")
        return record

    def read(self, key: str) -> dict[str, Any]:
        self.catalog.get(key)
        result = self._payload()["lessons"].get(key, {})
        return dict(self.validate_record(result))

    def save(self, key: str, fields: object) -> dict[str, Any]:
        self.catalog.get(key)
        if (
            not isinstance(fields, dict)
            or not fields
            or not set(fields) <= {"source", "prediction", "explanation", "review"}
        ):
            raise ValueError("Save source, prediction, explanation, or review text only.")
        for field, text in fields.items():
            cap = MAX_SOURCE_BYTES if field == "source" else 12_000
            if not isinstance(text, str) or len(text.encode("utf-8")) > cap:
                raise ValueError(f"{field} exceeds its text size limit.")
        self.safe_path(self.path)
        with locked_update(self.path):
            payload = self._payload()
            record = payload["lessons"].setdefault(key, {})
            self.validate_record(record)
            record.update(fields)
            atomic_json_write(self.path, payload)
        return dict(record)
