"""Immutable bounded receipts for completed Python and SQL classroom executions.

Reading a history never creates learner files. Receipts keep the actual response
and its submitted source together; recording does not run or replay any code.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.curriculum_framework import IDENTIFIER, RUNNERS, is_content_link
from ds60sqlpy.execution import MAX_CODE_BYTES, MAX_OUTPUT_BYTES
from ds60sqlpy.state_files import (
    atomic_json_write,
    locked_update,
)
from ds60sqlpy.state_files import (
    resolve_existing_ancestor as _resolve_existing_ancestor,
)

MAX_FIGURES = 4
MAX_FIGURE_BYTES = 2_000_000
# Four 2 MB PNGs need about 10.7 MB as base64. The remaining allowance covers
# bounded transcript/control-character escaping, SQL tables and result metadata.
MAX_RESULT_BYTES = 12_000_000
MAX_RECEIPT_BYTES = 16_000_000
MAX_NON_FIGURE_BYTES = 2_000_000
_ID = re.compile(r"[0-9a-f]{32}\Z")
_FILENAME = re.compile(r"(?P<stamp>\d{8}T\d{12}Z)_(?P<id>[0-9a-f]{32})\.json\Z")
_PNG_PREFIX = "data:image/png;base64,"
_RECEIPT_FIELDS = {
    "schema_version",
    "id",
    "lesson_id",
    "language",
    "mode",
    "saved_at",
    "source",
    "source_sha256",
    "result",
}


def _json_tree(value: object, depth: int = 0) -> None:
    """Reject non-JSON values, non-string keys and excessive nesting."""
    if depth > 32:
        raise ValueError("Run result nesting exceeds its limit.")
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Run result numbers must be finite.")
        return
    if isinstance(value, list):
        for item in value:
            _json_tree(item, depth + 1)
        return
    if isinstance(value, dict) and all(isinstance(key, str) for key in value):
        for item in value.values():
            _json_tree(item, depth + 1)
        return
    raise ValueError("Run result must contain ordinary JSON values and string keys.")


def _encoded(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2).encode("utf-8")


class ClassroomRunStore:
    """Store append-only receipts under a validated lesson/language/mode context."""

    def __init__(self, catalog: Catalog, directory: Path) -> None:
        if ".." in directory.parts:
            raise ValueError("Run history directory must not contain parent traversal.")
        self.catalog = catalog
        self.directory = directory.absolute()
        self.boundary = _resolve_existing_ancestor(self.directory.parent)

    def _safe_path(self, path: Path) -> Path:
        relative = path.relative_to(self.directory)
        if ".." in relative.parts:
            raise ValueError("Run history path must not contain parent traversal.")
        cursor = self.directory
        components = [cursor]
        for part in relative.parts:
            cursor = cursor / part
            components.append(cursor)
        if any(is_content_link(component) for component in components):
            raise ValueError("Run history must not follow symbolic links or junctions.")
        if not _resolve_existing_ancestor(path).is_relative_to(self.boundary):
            raise ValueError("Run history escaped its configured learner directory.")
        # A missing component may have appeared while its ancestor was resolved.
        # Reject a newly introduced reparse point before returning the path.
        if any(is_content_link(component) for component in components):
            raise ValueError("Run history must not follow symbolic links or junctions.")
        if is_content_link(path.with_name(path.name + ".lock")):
            raise ValueError("Run history lock must not be a symbolic link or junction.")
        return path

    def _context(self, lesson_id: str, language: str, mode: str) -> Path:
        if not isinstance(lesson_id, str) or IDENTIFIER.fullmatch(lesson_id) is None:
            raise ValueError("Choose a known lesson for its run history.")
        lesson = self.catalog.get(lesson_id)
        if not isinstance(language, str) or IDENTIFIER.fullmatch(language) is None:
            raise ValueError("Choose a registered Python or SQL executor.")
        runner = RUNNERS.get(language)
        if runner is None or runner.executor not in {"python", "sql"}:
            raise ValueError("Run history requires an implemented Python or SQL executor.")
        if not isinstance(mode, str) or mode not in {"snippet", "lesson"}:
            raise ValueError("Choose snippet or whole SQL lesson mode.")
        if mode == "lesson" and (runner.executor != "sql" or lesson.runner != "sql"):
            raise ValueError("Whole lesson history is available only for SQL lessons.")
        context = self._safe_path(self.directory / lesson_id / language / mode)
        if context.exists() and not context.is_dir():
            raise ValueError("Run history context must be a directory; existing data was retained.")
        return context

    @staticmethod
    def _source(source: object) -> tuple[str, str]:
        if not isinstance(source, str) or len(source.encode("utf-8")) > MAX_CODE_BYTES:
            raise ValueError(
                f"Recorded source must be text of at most {MAX_CODE_BYTES} UTF-8 bytes."
            )
        return source, hashlib.sha256(source.encode("utf-8")).hexdigest()

    @staticmethod
    def _result(
        result: object, language: str, mode: str, source_hash: str, *, saved: bool = False
    ) -> dict[str, Any]:
        if not isinstance(result, dict):
            raise ValueError("A completed run must have a result object.")
        _json_tree(result)
        if "withheld_artifacts" in result:
            raise ValueError("Saved results cannot contain derived figure-readback metadata.")
        if result.get("language") != RUNNERS[language].executor:
            raise ValueError("Run result language does not match its history context.")
        if (
            type(result.get("returncode")) is not int
            or not -(2**31) <= result["returncode"] < 2**32
        ):
            raise ValueError("Run result must include an integer return code.")
        output = result.get("output")
        if not isinstance(output, str) or len(output.encode("utf-8")) > MAX_OUTPUT_BYTES:
            raise ValueError("Run transcript exceeds its execution output limit.")
        elapsed = result.get("elapsed_seconds")
        if (
            isinstance(elapsed, bool)
            or not isinstance(elapsed, (int, float))
            or not 0 <= elapsed <= 86_400
            or not math.isfinite(elapsed)
        ):
            raise ValueError("Run result must include finite nonnegative elapsed time.")
        stopped = result.get("stopped")
        if stopped is not None and (
            not isinstance(stopped, str) or stopped not in {"time limit", "output limit"}
        ):
            raise ValueError("Run result has an unknown stop reason.")
        if "output_truncated" in result and not isinstance(result["output_truncated"], bool):
            raise ValueError("Run truncation metadata must be a boolean.")
        if "source_sha256" in result and result["source_sha256"] != source_hash:
            raise ValueError("Run result source fingerprint does not match the submitted source.")
        if "mode" in result and result["mode"] != mode:
            raise ValueError("Run result mode does not match its history context.")
        figures = result.get("figures", [])
        if not isinstance(figures, list) or len(figures) > MAX_FIGURES:
            raise ValueError("Run figures exceed their execution count limit.")
        max_base64 = 4 * ((MAX_FIGURE_BYTES + 2) // 3)
        for figure in figures:
            if (
                not isinstance(figure, str)
                or not figure.startswith(_PNG_PREFIX)
                or len(figure) > len(_PNG_PREFIX) + max_base64
            ):
                raise ValueError("A run figure must be a bounded PNG data URL.")
            try:
                data = base64.b64decode(figure[len(_PNG_PREFIX) :], validate=True)
            except ValueError as exc:
                raise ValueError("A run figure has invalid base64 content.") from exc
            if len(data) > MAX_FIGURE_BYTES or not data.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("A run figure has invalid PNG content or exceeds its size limit.")
        visible: list[dict[str, Any]] = []
        withheld: list[dict[str, Any]] = []
        if "artifacts" in result:
            from ds60sqlpy.plot_artifacts import read_saved_artifacts, validate_artifacts

            if saved:
                visible, withheld = read_saved_artifacts(result["artifacts"])
            else:
                validate_artifacts(result["artifacts"])
        metadata = {
            key: value for key, value in result.items() if key not in {"figures", "artifacts"}
        }
        if len(_encoded(metadata)) > MAX_NON_FIGURE_BYTES:
            raise ValueError("Run result metadata exceeds its stored size limit.")
        encoded = _encoded(result)
        if len(encoded) > MAX_RESULT_BYTES:
            raise ValueError("Run result exceeds its stored size limit.")
        # Snapshot callers' mutable lists/dicts so later UI annotation cannot
        # rewrite the receipt returned by this operation or written to disk.
        snapshot: dict[str, Any] = json.loads(encoded)
        # Original receipt budgets above apply before the bounded display-only
        # metadata is added. Never write this projection back to its source file.
        if saved and withheld:
            snapshot["artifacts"] = visible
            snapshot["withheld_artifacts"] = withheld
        return snapshot

    @staticmethod
    def _metadata(receipt: dict[str, Any]) -> dict[str, Any]:
        result = receipt["result"]
        status = (
            "timed_out"
            if result.get("stopped") == "time limit"
            else (
                "succeeded"
                if result["returncode"] == 0 and result.get("stopped") is None
                else "failed"
            )
        )
        return {
            "id": receipt["id"],
            "lesson_id": receipt["lesson_id"],
            "language": receipt["language"],
            "mode": receipt["mode"],
            "saved_at": receipt["saved_at"],
            "returncode": result["returncode"],
            "status": status,
            "source_sha256": receipt["source_sha256"],
        }

    def record(
        self, lesson_id: str, language: str, mode: str, source: str, result: dict[str, Any]
    ) -> dict[str, Any]:
        """Append one immutable receipt, never replacing an existing receipt ID."""
        context = self._context(lesson_id, language, mode)
        source, fingerprint = self._source(source)
        result = self._result(result, language, mode, fingerprint)
        now = datetime.now(UTC)
        identifier = uuid.uuid4().hex
        if _ID.fullmatch(identifier) is None:
            raise ValueError("Run receipt identity is invalid.")
        receipt = {
            "schema_version": 1,
            "id": identifier,
            "lesson_id": lesson_id,
            "language": language,
            "mode": mode,
            "saved_at": now.isoformat(),
            "source": source,
            "source_sha256": fingerprint,
            "result": result,
        }
        if len(_encoded(receipt)) + 1 > MAX_RECEIPT_BYTES:
            raise ValueError("Run receipt exceeds its stored size limit.")
        anchor = self._safe_path(context / ".write")
        with locked_update(anchor):
            self._safe_path(context)
            if list(context.glob(f"*_{identifier}.json")):
                raise ValueError(
                    "This run receipt ID already exists; its original data was retained."
                )
            path = self._safe_path(
                context / f"{now.strftime('%Y%m%dT%H%M%S%fZ')}_{identifier}.json"
            )
            if path.exists():
                raise ValueError("This run receipt already exists; its original data was retained.")
            atomic_json_write(path, receipt)
        return receipt

    def _read(self, path: Path, lesson_id: str, language: str, mode: str) -> dict[str, Any]:
        self._safe_path(path)
        match = _FILENAME.fullmatch(path.name)
        if match is None or not path.is_file() or path.stat().st_size > MAX_RECEIPT_BYTES:
            raise ValueError("Invalid or oversized run receipt; preserve it before recovery.")
        with path.open("rb") as stream:
            encoded = stream.read(MAX_RECEIPT_BYTES + 1)
        if len(encoded) > MAX_RECEIPT_BYTES:
            raise ValueError("Run receipt exceeds its stored size limit.")
        try:
            receipt = json.loads(encoded)
        except (ValueError, RecursionError) as exc:
            raise ValueError("Run receipt is corrupt; it was not removed or overwritten.") from exc
        if (
            not isinstance(receipt, dict)
            or set(receipt) != _RECEIPT_FIELDS
            or type(receipt.get("schema_version")) is not int
            or receipt["schema_version"] != 1
        ):
            raise ValueError("Run receipt has an unsupported or corrupt schema.")
        if (receipt["lesson_id"], receipt["language"], receipt["mode"], receipt["id"]) != (
            lesson_id,
            language,
            mode,
            match.group("id"),
        ):
            raise ValueError("Run receipt does not match its requested context or identity.")
        timestamp = receipt["saved_at"]
        if not isinstance(timestamp, str) or len(timestamp) > 40:
            raise ValueError("Run receipt timestamp is invalid.")
        try:
            saved = datetime.fromisoformat(timestamp)
        except ValueError as exc:
            raise ValueError("Run receipt timestamp is invalid.") from exc
        if (
            saved.tzinfo is None
            or saved.utcoffset() != UTC.utcoffset(saved)
            or saved.strftime("%Y%m%dT%H%M%S%fZ") != match.group("stamp")
        ):
            raise ValueError("Run receipt timestamp must match its UTC filename.")
        _, fingerprint = self._source(receipt["source"])
        if receipt["source_sha256"] != fingerprint:
            raise ValueError("Run receipt source fingerprint is inconsistent.")
        receipt["result"] = self._result(receipt["result"], language, mode, fingerprint, saved=True)
        return dict(receipt)

    def history(
        self, lesson_id: str, language: str, mode: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Return newest metadata without loading unbounded historical payloads."""
        if type(limit) is not int or not 1 <= limit <= 50:
            raise ValueError("Run history limit must be an integer from 1 through 50.")
        context = self._context(lesson_id, language, mode)
        if not context.exists():
            return []
        paths = sorted(context.glob("*.json"), key=lambda path: path.name, reverse=True)
        seen: set[str] = set()
        for path in paths:
            self._safe_path(path)
            match = _FILENAME.fullmatch(path.name)
            if match is None:
                raise ValueError("Run history contains an unrecognized receipt filename.")
            if match.group("id") in seen:
                raise ValueError("Run history contains duplicate receipt identities.")
            seen.add(match.group("id"))
        return [
            self._metadata(self._read(path, lesson_id, language, mode)) for path in paths[:limit]
        ]

    def get(self, lesson_id: str, language: str, mode: str, receipt_id: str) -> dict[str, Any]:
        """Read only the requested receipt inside its validated context."""
        context = self._context(lesson_id, language, mode)
        if not isinstance(receipt_id, str) or _ID.fullmatch(receipt_id) is None:
            raise ValueError("Choose a valid saved run receipt ID.")
        paths = list(context.glob(f"*_{receipt_id}.json"))
        if len(paths) != 1:
            raise ValueError("Run receipt was not found uniquely in this lesson workspace.")
        return self._read(paths[0], lesson_id, language, mode)
