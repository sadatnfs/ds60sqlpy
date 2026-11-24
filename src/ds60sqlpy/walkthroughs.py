"""Authored, hash-bound walkthroughs of module references. Nothing here runs code.

Each `courses/<track>/walkthroughs.json` explains the lesson's executable
reference in line-anchored steps. The steps are written by the course, not
traced from a run, so every payload says `evidence: authored` and
`executed: false`. The reference bytes are bound by SHA-256 and each step
carries the exact excerpt it explains, so a changed reference fails closed.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from ds60sqlpy.browser_runs import BROWSER_PROFILES
from ds60sqlpy.curriculum_framework import REVEAL_MESSAGE, validate_content_path
from ds60sqlpy.gpu_runtime import GPU_PROFILES
from ds60sqlpy.modules import LANGUAGES, MAX_SOURCE_BYTES, ModuleCatalog, ModuleLesson

WALKTHROUGH_LABEL = "Authored steps, not a live trace"
VERIFIED_BY = "Expected output is checked against the reference run in the CI reference corpus."
NO_WALKTHROUGH = "This lesson has no authored walkthrough."
MAX_INDEX_BYTES = 1_000_000
MIN_STEPS, MAX_STEPS = 3, 20
TEXT_LIMITS = {"title": 200, "explanation": 1200, "observe": 600}
MAX_EXPECTED, EXPECTED_LIMIT = 5, 200
# Same expression as scripts/check_module_references.py, so every anchor is a
# lesson the CI reference corpus actually executes.
ORDINARY_PROFILES = (
    frozenset(LANGUAGES)
    - {"reading", "k8s-kind", "dax-offline"}
    - BROWSER_PROFILES.keys()
    - GPU_PROFILES
)
DASHES = ("\u2014", "\u2013")
ENTRY_KEYS = frozenset(
    {"lesson_id", "title", "anchor", "source_path", "source_sha256", "expected_output", "steps"}
)
STEP_KEYS = frozenset({"lines", "excerpt", "title", "explanation", "observe"})
TOP_KEYS = frozenset({"schema_version", "track_id", "evidence", "walkthroughs"})


def executable_reference_path(lesson: ModuleLesson) -> str:
    """The one program the CI corpus runs: tutorial source or the single code solution."""
    paths = (
        [lesson.source_path]
        if lesson.learning_mode == "tutorial"
        else [path for path in lesson.solution_paths if PurePosixPath(path).suffix != ".md"]
    )
    if len(paths) != 1:
        raise ValueError(f"{lesson.id} must declare exactly one executable reference per variant.")
    return paths[0]


def index_path(track: str) -> str:
    return f"courses/{track}/walkthroughs.json"


def _read_index(root: Path, track: str) -> dict[str, Any] | None:
    relative = index_path(track)
    if not (root / relative).exists():
        return None
    validate_content_path(root, relative, "Walkthrough index")
    path = root / relative
    if not path.is_file() or path.stat().st_size > MAX_INDEX_BYTES:
        raise ValueError(f"{relative} is missing or oversized.")
    payload = json.loads(path.read_bytes().decode("utf-8"))
    if not isinstance(payload, dict) or set(payload) - TOP_KEYS:
        raise ValueError(f"{relative} must be an object with only the documented keys.")
    if type(payload.get("schema_version")) is not int or payload["schema_version"] != 1:
        raise ValueError(f"{relative} must declare schema_version 1.")
    if payload.get("track_id") != track:
        raise ValueError(f"{relative} must declare track_id {track!r}.")
    if payload.get("evidence") != "authored":
        raise ValueError("Walkthroughs must not claim runtime evidence.")
    entries = payload.get("walkthroughs")
    if not isinstance(entries, list) or len(entries) > 500:
        raise ValueError(f"{relative} needs a bounded walkthroughs list.")
    return payload


def _text(value: Any, limit: int, where: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: {name} must be non-empty text.")
    if len(value) > limit:
        raise ValueError(f"{where}: {name} exceeds {limit} characters.")
    if any(dash in value for dash in DASHES):
        raise ValueError(f"{where}: {name} must not contain an em or en dash.")
    return value


def _reference_bytes(root: Path, relative: str, lesson_id: str) -> bytes:
    validate_content_path(root, relative, f"{lesson_id} walkthrough source")
    path = root / relative
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError(f"{lesson_id}: walkthrough source is missing or oversized.")
    return path.read_bytes()


def source_lines(text: str) -> list[str]:
    return text.split("\n")[:-1] if text.endswith("\n") else text.split("\n")


def validate_entry(
    root: Path,
    catalog: ModuleCatalog,
    track: str,
    entry: Any,
    *,
    check_hash: bool = True,
) -> dict[str, Any]:
    """Return a clean entry or raise ValueError naming the lesson and step."""
    if not isinstance(entry, dict):
        raise ValueError("Each walkthrough must be an object.")
    lesson_id = entry.get("lesson_id")
    if not isinstance(lesson_id, str):
        raise ValueError("Each walkthrough needs a lesson_id.")
    lesson = catalog.lessons.get(lesson_id)
    if lesson is None or lesson.track_id != track:
        raise ValueError(f"{lesson_id}: not an authored lesson of track {track}.")
    unknown = set(entry) - ENTRY_KEYS
    if unknown:
        raise ValueError(f"{lesson_id}: unknown keys {sorted(unknown)}.")
    if lesson.runtime_profile not in ORDINARY_PROFILES:
        raise ValueError(
            f"{lesson_id}: runtime profile {lesson.runtime_profile} is not run by the "
            "CI reference corpus; choose an ordinary-profile lesson."
        )
    if entry.get("anchor") != "reference":
        raise ValueError(f"{lesson_id}: anchor must be 'reference'.")
    title = _text(entry.get("title"), TEXT_LIMITS["title"], lesson_id, "title")
    source_path = entry.get("source_path")
    if not isinstance(source_path, str) or not source_path.startswith(f"courses/{track}/"):
        raise ValueError(f"{lesson_id}: source_path must stay inside courses/{track}/.")
    validate_content_path(root, source_path, f"{lesson_id} walkthrough source")
    expected_path = executable_reference_path(lesson)
    if source_path != expected_path:
        raise ValueError(
            f"{lesson_id}: source_path must be the executable reference {expected_path}."
        )
    data = _reference_bytes(root, source_path, lesson_id)
    digest = entry.get("source_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError(f"{lesson_id}: source_sha256 must be 64 lowercase hex characters.")
    current = hashlib.sha256(data).hexdigest()
    if check_hash and digest != current:
        raise ValueError(f"Walkthrough for {lesson_id} is stale; rebind or re-author it.")
    try:
        source = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{lesson_id}: walkthrough source is not UTF-8.") from error
    lines = source_lines(source)
    expected = entry.get("expected_output")
    if not isinstance(expected, list) or not 1 <= len(expected) <= MAX_EXPECTED:
        raise ValueError(
            f"{lesson_id}: expected_output needs 1 to {MAX_EXPECTED} strings the reference prints."
        )
    clean_expected = [
        _text(item, EXPECTED_LIMIT, lesson_id, "expected_output") for item in expected
    ]
    steps = entry.get("steps")
    if not isinstance(steps, list) or not MIN_STEPS <= len(steps) <= MAX_STEPS:
        raise ValueError(f"{lesson_id}: needs {MIN_STEPS} to {MAX_STEPS} steps.")
    clean_steps = []
    previous_start = 0
    for number, step in enumerate(steps, start=1):
        where = f"{lesson_id} step {number}"
        if not isinstance(step, dict) or set(step) - STEP_KEYS:
            raise ValueError(f"{where}: must be an object with only the documented keys.")
        span = step.get("lines")
        if (
            not isinstance(span, list)
            or len(span) != 2
            or any(type(value) is not int for value in span)
        ):
            raise ValueError(f"{where}: lines must be [start, end] integers.")
        start, end = span
        if not 1 <= start <= end <= len(lines):
            raise ValueError(f"{where}: lines {start}-{end} are outside 1-{len(lines)}.")
        if start < previous_start:
            raise ValueError(f"{where}: steps must not move backward through the source.")
        previous_start = start
        if step.get("excerpt") != "\n".join(lines[start - 1 : end]):
            raise ValueError(f"{where}: excerpt no longer matches lines {start}-{end}.")
        clean: dict[str, Any] = {"lines": [start, end]}
        for key, limit in TEXT_LIMITS.items():
            clean[key] = _text(step.get(key), limit, where, key)
        clean_steps.append(clean)
    return {
        "lesson_id": lesson_id,
        "title": title,
        "source_path": source_path,
        "source_sha256": digest,
        "current_sha256": current,
        "source": source,
        "expected_output": clean_expected,
        "steps": clean_steps,
        "solution_anchor": source_path != lesson.source_path,
    }


def validate_index(
    root: Path, catalog: ModuleCatalog, track: str, *, check_hash: bool = True
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Validate every entry; return the clean entries and all error messages."""
    try:
        payload = _read_index(root, track)
    except (OSError, ValueError) as error:
        return {}, [str(error)]
    if payload is None:
        return {}, []
    clean: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for entry in payload["walkthroughs"]:
        lesson_id = entry.get("lesson_id") if isinstance(entry, dict) else None
        if isinstance(lesson_id, str) and lesson_id in clean:
            errors.append(f"{lesson_id}: duplicate walkthrough.")
            continue
        try:
            item = validate_entry(root, catalog, track, entry, check_hash=check_hash)
        except (OSError, ValueError) as error:
            errors.append(str(error))
            if isinstance(lesson_id, str):
                clean.setdefault(lesson_id, {})
            continue
        clean[item["lesson_id"]] = item
    return {key: value for key, value in clean.items() if value}, errors


def load_walkthroughs(root: Path, catalog: ModuleCatalog, track: str) -> dict[str, dict[str, Any]]:
    """Return valid walkthroughs keyed by lesson id; raise on the first error."""
    clean, errors = validate_index(root, catalog, track)
    if errors:
        raise ValueError(errors[0])
    return clean


def walkthrough_payload(
    root: Path, catalog: ModuleCatalog, lesson_id: str, reveal: bool
) -> dict[str, Any]:
    lesson = catalog.lessons.get(lesson_id)
    if lesson is None:
        raise ValueError(NO_WALKTHROUGH)
    item = load_walkthroughs(root, catalog, lesson.track_id).get(lesson_id)
    if item is None:
        raise ValueError(NO_WALKTHROUGH)
    if item["solution_anchor"] and reveal is not True:
        raise ValueError(REVEAL_MESSAGE)
    return {
        "lesson_id": lesson_id,
        "kind": "authored",
        "label": WALKTHROUGH_LABEL,
        "evidence": "authored",
        "executed": False,
        "title": item["title"],
        "source_path": item["source_path"],
        "source_sha256": item["source_sha256"],
        "source": item["source"],
        "solution_anchor": item["solution_anchor"],
        "steps": item["steps"],
        "expected_output": item["expected_output"],
        "verified_by": VERIFIED_BY,
    }
