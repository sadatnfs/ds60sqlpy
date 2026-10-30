"""Bounded, data-only JSON used at the Python/JVM boundary."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_DEPTH = 32
MAX_OBJECT_FIELDS = 1024
MAX_ARRAY_ITEMS = 8192
MAX_KEY_CHARACTERS = 256
MAX_STRING_CHARACTERS = 1_000_000


class ContractError(ValueError):
    """A model, runtime, or operation does not satisfy the public contract."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise ContractError(f"Nonfinite JSON number: {value}")


def _check(value: Any, depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        raise ContractError("JSON exceeds the maximum nesting depth")
    if isinstance(value, str):
        if len(value) > MAX_STRING_CHARACTERS:
            raise ContractError("JSON string exceeds the maximum character count")
        try:
            value.encode("utf-8")
        except UnicodeError as exc:
            raise ContractError("JSON strings must contain valid Unicode characters") from exc
        return
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if abs(value) > 2**53 - 1:
            raise ContractError("JSON integer exceeds the exact interchange range")
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractError("JSON numbers must be finite")
        return
    if isinstance(value, dict):
        if len(value) > MAX_OBJECT_FIELDS:
            raise ContractError("JSON object exceeds the maximum field count")
        for key, item in value.items():
            if not isinstance(key, str):
                raise ContractError("JSON object keys must be strings")
            if len(key) > MAX_KEY_CHARACTERS:
                raise ContractError("JSON key exceeds the maximum character count")
            _check(key, depth + 1)
            _check(item, depth + 1)
        return
    if isinstance(value, list):
        if len(value) > MAX_ARRAY_ITEMS:
            raise ContractError("JSON array exceeds the maximum element count")
        for item in value:
            _check(item, depth + 1)
        return
    raise ContractError(f"Unsupported JSON value type: {type(value).__name__}")


def dumps(value: Mapping[str, Any]) -> str:
    """Serialize a JSON object without executable or lossy Python coercions."""
    if not isinstance(value, Mapping):
        raise ContractError("Expected a JSON object")
    obj = dict(value)
    _check(obj)
    raw = json.dumps(
        obj, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=False
    )
    if len(raw.encode("utf-8")) > MAX_JSON_BYTES:
        raise ContractError("JSON exceeds the maximum encoded size")
    return raw


def loads(raw: str | bytes) -> dict[str, Any]:
    if not isinstance(raw, (str, bytes)):
        raise ContractError("Expected UTF-8 JSON text")
    try:
        encoded = raw.encode("utf-8") if isinstance(raw, str) else raw
        if len(encoded) > MAX_JSON_BYTES:
            raise ContractError("JSON exceeds the maximum encoded size")
        obj = json.loads(
            encoded.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_constant
        )
        if not isinstance(obj, dict):
            raise ContractError("Expected a JSON object")
        _check(obj)
        return obj
    except ContractError:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ContractError("Invalid UTF-8 JSON object") from exc


def read(path: str | Path) -> dict[str, Any]:
    """Read a local bounded JSON document, without importing any model code."""
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_JSON_BYTES + 1)
    return loads(raw)


def copy_object(value: Mapping[str, Any]) -> dict[str, Any]:
    """Defensively copy and validate a mapping through its wire representation."""
    return loads(dumps(value))
