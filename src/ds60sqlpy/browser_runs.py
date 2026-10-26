"""Bounded browser observations, kept separate from trusted worker job receipts."""

from __future__ import annotations

import hashlib
import json
import math
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ds60sqlpy.modules import MAX_SOURCE_BYTES, ModuleState
from ds60sqlpy.state_files import atomic_json_write, locked_update

MAX_BROWSER_OUTPUT_BYTES = 32_000
MAX_BROWSER_RECORD_BYTES = 512 * 1024
BROWSER_HISTORY_LIMIT = 20
BROWSER_STATUSES = frozenset({"succeeded", "failed", "cancelled"})
BROWSER_PROFILES = {
    "javascript-browser": ("javascript", "d3@7.9.0+plotly@4.1.2"),
    "html-browser": ("html", "html-css-dom"),
}


def browser_capability(profile: str = "javascript-browser") -> dict[str, Any]:
    if profile not in BROWSER_PROFILES:
        raise ValueError("Unknown browser profile.")
    return {
        "profile": profile,
        "ready": True,
        "detail": (
            "Renders HTML, inline CSS and inline JavaScript in the isolated offline preview."
            if profile == "html-browser"
            else "Runs in the isolated browser preview with bundled D3 7.9.0 and Plotly 4.1.2."
        ),
        "execution_location": "browser",
        "verification_kind": "browser_observation",
    }


class BrowserRunStore:
    """Store client observations without claiming server execution or verified checks."""

    def __init__(self, state: ModuleState) -> None:
        self.state = state

    def _directory(self, lesson_id: object) -> Path:
        lesson = self.state.catalog.get(lesson_id)
        if lesson.runtime_profile not in BROWSER_PROFILES:
            raise ValueError("Browser observations require a browser lesson.")
        return self.state.safe_path(self.state.directory / "browser-runs" / lesson.id)

    @staticmethod
    def _validate_inputs(fields: object) -> dict[str, Any]:
        if not isinstance(fields, dict) or set(fields) != {
            "source",
            "output",
            "status",
            "elapsed_seconds",
        }:
            raise ValueError("Supply browser source, output, status and elapsed seconds only.")
        for key, limit in (("source", MAX_SOURCE_BYTES), ("output", MAX_BROWSER_OUTPUT_BYTES)):
            if not isinstance(fields[key], str) or len(fields[key].encode("utf-8")) > limit:
                raise ValueError(f"Browser {key} exceeds its UTF-8 size limit.")
        if not isinstance(fields["status"], str) or fields["status"] not in BROWSER_STATUSES:
            raise ValueError("Choose a terminal browser observation status.")
        elapsed = fields["elapsed_seconds"]
        if (
            type(elapsed) not in (int, float)
            or not math.isfinite(elapsed)
            or not 0 <= elapsed <= 3600
        ):
            raise ValueError("Browser elapsed seconds must be finite and bounded.")
        return fields

    def _read(self, path: Path, lesson_id: str) -> dict[str, Any]:
        lesson = self.state.catalog.get(lesson_id)
        expected_language, expected_library = BROWSER_PROFILES[lesson.runtime_profile]
        historical_libraries = {expected_library}
        if lesson.runtime_profile == "javascript-browser":
            historical_libraries.add("d3@7.9.0")
        safe = self.state.safe_path(path)
        if safe.stat().st_size > MAX_BROWSER_RECORD_BYTES:
            raise ValueError("Browser history contains an oversized record; preserve it.")
        record = json.loads(safe.read_text(encoding="utf-8"))
        if not isinstance(record, dict) or set(record) != {
            "schema_version",
            "kind",
            "job_id",
            "lesson_id",
            "profile",
            "language",
            "library",
            "created_at",
            "source",
            "source_sha256",
            "output",
            "status",
            "elapsed_seconds",
            "verification_kind",
            "verified",
            "checks",
            "returncode",
        }:
            raise ValueError("Browser observation history is malformed; it was not overwritten.")
        if (
            type(record["schema_version"]) is not int
            or record["schema_version"] != 1
            or record["kind"] != "browser_observation"
            or not isinstance(record["job_id"], str)
            or record["job_id"] + ".json" != path.name
            or re.fullmatch(r"[0-9a-f]{32}", str(record["job_id"])) is None
            or record["lesson_id"] != lesson_id
            or record["profile"] != lesson.runtime_profile
            or record["language"] != expected_language
            or not isinstance(record["library"], str)
            or record["library"] not in historical_libraries
            or record["verification_kind"] != "browser_observation"
            or record["verified"] is not False
            or record["checks"] != []
            or record["returncode"] is not None
            or not isinstance(record["created_at"], str)
        ):
            raise ValueError("Browser observation identity or evidence kind is invalid.")
        self._validate_inputs(
            {key: record[key] for key in ("source", "output", "status", "elapsed_seconds")}
        )
        if record["source_sha256"] != hashlib.sha256(record["source"].encode("utf-8")).hexdigest():
            raise ValueError("Browser observation source does not match its recorded hash.")
        try:
            parsed_time = datetime.fromisoformat(record["created_at"])
        except ValueError as error:
            raise ValueError("Browser observation time is invalid.") from error
        if parsed_time.tzinfo is None:
            raise ValueError("Browser observation time must include its timezone.")
        return record

    def _records(self, lesson_id: str) -> list[dict[str, Any]]:
        directory = self._directory(lesson_id)
        if not directory.exists():
            return []
        paths = list(directory.glob("*.json"))
        if len(paths) > 100:
            raise ValueError("Browser history exceeds its record limit; preserve and inspect it.")
        rows = []
        for path in paths:
            try:
                rows.append(self._read(path, lesson_id))
            except FileNotFoundError:
                # A concurrent successful save can prune an older receipt after
                # this reader lists it. Missing rows are not corrupt history;
                # every remaining row still receives the full validation above.
                continue
        return sorted(rows, key=lambda row: row["created_at"], reverse=True)

    def history(self, lesson_id: str) -> list[dict[str, Any]]:
        return self._records(lesson_id)[:BROWSER_HISTORY_LIMIT]

    def get(self, lesson_id: str, receipt_id: object) -> dict[str, Any]:
        if not isinstance(receipt_id, str) or re.fullmatch(r"[0-9a-f]{32}", receipt_id) is None:
            raise ValueError("Choose an existing browser observation ID.")
        return self._read(self._directory(lesson_id) / (receipt_id + ".json"), lesson_id)

    def record(self, lesson_id: str, fields: object) -> dict[str, Any]:
        values = self._validate_inputs(fields)
        directory = self._directory(lesson_id)
        lesson = self.state.catalog.get(lesson_id)
        language, library = BROWSER_PROFILES[lesson.runtime_profile]
        record = {
            "schema_version": 1,
            "kind": "browser_observation",
            "job_id": uuid.uuid4().hex,
            "lesson_id": lesson_id,
            "profile": lesson.runtime_profile,
            "language": language,
            "library": library,
            "created_at": datetime.now(UTC).isoformat(),
            **values,
            "source_sha256": hashlib.sha256(values["source"].encode("utf-8")).hexdigest(),
            "verification_kind": "browser_observation",
            "verified": False,
            "checks": [],
            "returncode": None,
        }
        lock = self.state.safe_path(directory / ".history")
        with locked_update(lock):
            # Validate existing records before writing or pruning any history.
            previous = self._records(lesson_id)
            path = self.state.safe_path(directory / (record["job_id"] + ".json"))
            atomic_json_write(path, record)
            for old in previous[BROWSER_HISTORY_LIMIT - 1 :]:
                self.state.safe_path(directory / (old["job_id"] + ".json")).unlink()
        return record
