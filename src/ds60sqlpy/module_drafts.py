"""Offline DAX editing and bounded, source-bound worked tables, never execution."""

from __future__ import annotations

import datetime
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from ds60sqlpy.curriculum_framework import validate_content_path

DRAFT_PROFILES = frozenset({"dax-offline"})


def draft_capability(profile: str) -> dict[str, Any]:
    if profile not in DRAFT_PROFILES:
        raise ValueError("Unknown offline editing profile.")
    return {
        "profile": profile,
        "ready": True,
        "can_run": False,
        "mode": "draft",
        "detail": "Offline DAX pad: save, compare and export code. Worked tables are "
        "hand-derived from the named reference and model, not your edited draft.",
    }


def _file(root: Path, value: Any, suffix: str, limit: int = 2_000_000) -> tuple[str, bytes]:
    if (
        not isinstance(value, str)
        or not value.startswith("courses/dax/")
        or Path(value).suffix != suffix
    ):
        raise ValueError("Worked reference must stay in the DAX course.")
    validate_content_path(root, value, "DAX worked reference")
    path = root / value
    if not path.is_file() or path.stat().st_size > limit:
        raise ValueError("Missing or oversized DAX reference.")
    return value, path.read_bytes()


def _bound_text(value: Any, maximum: int = 4000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError("Invalid DAX explanatory text.")
    return value


def _hashed_file(root: Path, item: dict[str, Any], name: str, suffix: str) -> bytes:
    _, data = _file(root, item.get(name + "_path"), suffix)
    digest = item.get(name + "_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Invalid DAX source digest.")
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("DAX worked reference is stale; regenerate its source binding.")
    return data


def worked_examples(root: Path, lesson_id: str) -> dict[str, Any]:
    """Return hand-derived evidence only after checking the reference and model bytes."""
    _, data = _file(root, "courses/dax/reference-results.json", ".json", 4_000_000)
    payload = json.loads(data)
    if (
        not isinstance(payload, dict)
        or type(payload.get("schema_version")) is not int
        or payload["schema_version"] != 1
        or payload.get("track_id") != "dax"
        or not isinstance(payload.get("lessons"), list)
        or len(payload["lessons"]) > 200
    ):
        raise ValueError("Invalid DAX worked reference index.")
    ids = [item.get("lesson_id") if isinstance(item, dict) else None for item in payload["lessons"]]
    if any(not isinstance(key, str) for key in ids) or len(ids) != len(set(ids)):
        raise ValueError("Duplicate or invalid DAX reference identity.")
    entries = [item for item in payload["lessons"] if item["lesson_id"] == lesson_id]
    if len(entries) != 1:
        raise ValueError("No worked reference for this DAX lesson.")
    item = entries[0]
    if item.get("evidence") != "hand-derived":
        raise ValueError("DAX worked references must not claim runtime evidence.")
    # The schema names the reference's source digest separately from its path.
    reference = _hashed_file(
        root,
        {
            "reference_path": item.get("reference_path"),
            "reference_sha256": item.get("source_sha256"),
        },
        "reference",
        ".dax",
    )
    model_bytes = _hashed_file(root, item, "model", ".json")
    model = json.loads(model_bytes)
    if (
        not isinstance(model, dict)
        or type(model.get("schema_version")) is not int
        or model["schema_version"] != 1
        or not isinstance(model.get("tables"), list)
        or not 1 <= len(model["tables"]) <= 20
    ):
        raise ValueError("Invalid DAX model.")
    for table in model["tables"]:
        if not isinstance(table, dict):
            raise ValueError("Invalid DAX model table.")
        _hashed_file(
            root,
            {"table_path": table.get("path"), "table_sha256": table.get("sha256")},
            "table",
            ".csv",
        )
    cases = item.get("cases")
    if not isinstance(cases, list) or not 1 <= len(cases) <= 6:
        raise ValueError("DAX needs a bounded worked-case list.")
    safe_cases = []
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Invalid DAX worked case.")
        clean: dict[str, Any] = {
            key: _bound_text(case.get(key)) for key in ("id", "title", "context", "note")
        }
        trace, columns, rows = case.get("trace"), case.get("columns"), case.get("rows")
        if not isinstance(trace, list) or not 1 <= len(trace) <= 30:
            raise ValueError("Invalid DAX context trace.")
        clean["trace"] = [_bound_text(step) for step in trace]
        if (
            not isinstance(columns, list)
            or not 1 <= len(columns) <= 12
            or not isinstance(rows, list)
            or len(rows) > 100
        ):
            raise ValueError("DAX worked table exceeds bounds.")
        safe_columns = []
        for column in columns:
            if not isinstance(column, dict) or column.get("type") not in {
                "number",
                "integer",
                "text",
                "boolean",
                "date",
            }:
                raise ValueError("Invalid DAX table column.")
            safe_columns.append(
                {"name": _bound_text(column.get("name"), 200), "type": column["type"]}
            )
        if len({c["name"] for c in safe_columns}) != len(safe_columns):
            raise ValueError("Duplicate DAX table column.")
        for row in rows:
            if not isinstance(row, list) or len(row) != len(columns):
                raise ValueError("Invalid DAX table row.")
            for column, value in zip(safe_columns, row, strict=True):
                kind = column["type"]
                if value is None:
                    continue
                if kind in {"number", "integer"}:
                    if (
                        type(value) not in ({int} if kind == "integer" else {int, float})
                        or abs(value) > 1e308
                        or not math.isfinite(value)
                    ):
                        raise ValueError("Invalid DAX numeric value.")
                elif kind == "boolean":
                    if type(value) is not bool:
                        raise ValueError("Invalid DAX boolean value.")
                elif not isinstance(value, str) or len(value) > 2000:
                    raise ValueError("Invalid DAX text value.")
                elif kind == "date":
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                        raise ValueError("Invalid DAX date value.")
                    datetime.date.fromisoformat(value)
        clean.update(columns=safe_columns, rows=rows)
        safe_cases.append(clean)
    return {
        "lesson_id": lesson_id,
        "evidence": "hand-derived",
        "executed": False,
        "reference_path": item["reference_path"],
        "source_sha256": item["source_sha256"],
        "reference_source": reference.decode("utf-8"),
        "model_path": item["model_path"],
        "model_sha256": item["model_sha256"],
        "cases": safe_cases,
    }
