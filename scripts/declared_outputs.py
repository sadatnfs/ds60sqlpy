"""Reviewable output contracts for authored references, independent of exit status."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from ds60sqlpy.curriculum_framework import validate_content_path, validate_identifier
from ds60sqlpy.plot_artifacts import validate_artifacts

KINDS = {"png", "plotly", "table", "json"}
MAX_CONTRACT_BYTES = 64_000
UNIT_FIELDS = {
    "id",
    "kind",
    "count",
    "kinds",
    "description_required",
    "table_required",
    "table_rows",
    "origin",
    "limits",
}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject ambiguous JSON instead of allowing a later value to replace a rule."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate output contract JSON field: " + key)
        result[key] = value
    return result


def _normalized_unit(item: dict[str, Any]) -> dict[str, Any]:
    if set(item) - UNIT_FIELDS:
        raise ValueError("Invalid output expectation fields")
    if "kinds" in item:
        if "kind" in item:
            raise ValueError("Choose kind or kinds, not both")
        kinds = item["kinds"]
        if "count" in item and (
            type(item["count"]) is not int
            or not isinstance(kinds, list)
            or item["count"] != len(kinds)
        ):
            raise ValueError("Output count must match the declared kinds")
    else:
        count = item.get("count")
        if type(count) is not int or not 1 <= count <= 2:
            raise ValueError("Output count exceeds the classroom limit")
        kinds = [item.get("kind")] * count
    if (
        not isinstance(kinds, list)
        or not 1 <= len(kinds) <= 2
        or any(not isinstance(kind, str) or kind not in KINDS for kind in kinds)
    ):
        raise ValueError("Invalid expected output kinds")
    for field in ("description_required", "table_required"):
        if type(item.get(field, False)) is not bool:
            raise ValueError("Output requirements must be booleans")
    for field in ("origin", "limits"):
        if field in item and (
            not isinstance(item[field], str) or not item[field].strip() or len(item[field]) > 2000
        ):
            raise ValueError("Output origin and limits must be bounded nonempty text")
    table_required = item.get("table_required", False)
    if "table_rows" in item:
        if type(item["table_rows"]) is not int or not 0 <= item["table_rows"] <= 100:
            raise ValueError("Invalid expected table row count")
        if "table_required" in item and not table_required:
            raise ValueError("A table row expectation cannot disable the table requirement")
        table_required = True
    if table_required and not set(kinds) & {"table", "plotly"}:
        raise ValueError("A table expectation needs a table or Plotly output")
    return {**item, "kinds": kinds, "table_required": table_required}


def load_contracts(root: Path, subject: str, identities: set[str]) -> dict[str, dict[str, Any]]:
    """Load optional version-one contracts for exact admitted lesson/variant IDs.

    A homogeneous ``kind`` plus ``count`` and a heterogeneous ``kinds`` list are
    supported. The list form may retain a matching count and explanatory origin
    or limits metadata. None of that metadata changes the required output kinds.
    """
    validate_identifier(subject, "Output contract subject")
    relative = f"courses/{subject}/figure-contracts.json"
    path = root / relative
    if not path.exists() and not path.is_symlink():
        return {}
    validate_content_path(root, relative, "Reference output contract")
    with path.open("rb") as stream:
        data = stream.read(MAX_CONTRACT_BYTES + 1)
    if len(data) > MAX_CONTRACT_BYTES:
        raise ValueError("Output contract exceeds its metadata limit")
    raw = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object)
    if (
        not isinstance(raw, dict)
        or set(raw) != {"schema_version", "units"}
        or type(raw["schema_version"]) is not int
        or raw["schema_version"] != 1
        or not isinstance(raw["units"], list)
    ):
        raise ValueError("Invalid reference output contract")
    contracts = {}
    for item in raw["units"]:
        if not isinstance(item, dict):
            raise ValueError("Invalid output expectation fields")
        key = item.get("id")
        if not isinstance(key, str) or key not in identities or key in contracts:
            raise ValueError("Output expectation must name one unique authored unit")
        contracts[key] = _normalized_unit(item)
    return contracts


def verify_contract(contract: dict[str, Any] | None, artifacts: Any) -> None:
    if contract is None:
        return
    checked = validate_artifacts(artifacts)
    if Counter(item["kind"] for item in checked) != Counter(contract["kinds"]):
        raise ValueError("Declared reference outputs are missing or changed kind")
    for artifact in checked:
        if contract.get("description_required") and not artifact.get("description", "").strip():
            raise ValueError("Declared output description is missing")
        if contract.get("table_required") and artifact["kind"] in {"table", "plotly"}:
            table = artifact.get("table")
            if not isinstance(table, dict) or not table.get("columns"):
                raise ValueError("Declared accessible output table is missing")
            if "table_rows" in contract and len(table["rows"]) != contract["table_rows"]:
                raise ValueError("Declared table row count changed")
