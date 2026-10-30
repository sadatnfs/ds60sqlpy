# SPDX-License-Identifier: Apache-2.0
"""Small data-only guards for bounded executor training."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

from ds60_spark_likelihood.contracts import ObjectiveError


class TrainingError(ObjectiveError):
    """The explicit training/data/checkpoint contract was not satisfied."""


MAX_JSON = 1_000_000
MAX_RECEIPT = 65_536
MAX_WORLD_SIZE = 8
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def canonical_json(value: Any, *, limit: int = MAX_JSON) -> bytes:
    try:
        raw = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as error:
        raise TrainingError("Value must be bounded finite JSON data") from error
    if len(raw) > limit:
        raise TrainingError("JSON byte limit exceeded")
    return raw


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def sha256_file(path: str | Path, *, max_bytes: int | None = None) -> str:
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise TrainingError("Expected an owned regular file")
    result = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            count += len(chunk)
            if max_bytes is not None and count > max_bytes:
                raise TrainingError("File byte limit exceeded")
            result.update(chunk)
    return result.hexdigest()


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise TrainingError("Duplicate JSON key")
        result[key] = value
    return result


def _constant(value):
    raise TrainingError("Nonfinite JSON token: " + value)


def read_json(path: str | Path, *, limit: int = MAX_JSON):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise TrainingError("Expected an owned JSON file")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise TrainingError("JSON byte limit exceeded")
    try:
        value = json.loads(raw, object_pairs_hook=_unique, parse_constant=_constant)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise TrainingError("Malformed bounded JSON") from error
    canonical_json(value, limit=limit)
    return value


def write_new_json(path: str | Path, value: Any, *, limit: int = MAX_JSON) -> None:
    path = Path(path)
    if type(limit) is not int or limit < 1:
        raise TrainingError("JSON byte limit must be positive")
    raw = canonical_json(value, limit=limit - 1) + b"\n"
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def exact_keys(value, required, optional=(), *, name="object"):
    if (
        not isinstance(value, dict)
        or not set(required) <= set(value)
        or set(value) - set(required) - set(optional)
    ):
        raise TrainingError(name + " has missing or unknown fields")
    return value


def integer(value, name="integer", minimum=0, maximum=2**53 - 1):
    if type(value) is not int or not minimum <= value <= maximum:
        raise TrainingError(name + " must be an exact bounded integer")
    return value


def finite(value, name="number", *, minimum=None, maximum=None):
    if type(value) not in (int, float):
        raise TrainingError(name + " must be numeric without coercion")
    try:
        number = float(value)
    except (OverflowError, ValueError) as error:
        raise TrainingError(name + " exceeds finite range") from error
    if not math.isfinite(number) or (type(value) is int and int(number) != value):
        raise TrainingError(name + " must be exactly representable and finite")
    if minimum is not None and number < minimum or maximum is not None and number > maximum:
        raise TrainingError(name + " is outside its declared bounds")
    return number


def safe_relative(value: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 4096
        or Path(value).is_absolute()
        or Path(value).as_posix() != value
        or ".." in Path(value).parts
        or "\\" in value
        or any(ord(character) < 32 for character in value)
    ):
        raise TrainingError("Expected a safe relative artifact path")
    return value


def resolve_owned_file(root: str | Path, relative: str, *, must_exist=True, max_bytes=None) -> Path:
    root = Path(root)
    relative = safe_relative(relative)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise TrainingError("Artifact root must be an explicit owned directory")
    target = root / relative
    for item in (target, *target.parents):
        if item.is_symlink():
            raise TrainingError("Artifact paths cannot traverse symlinks")
        if item == root:
            break
    if must_exist:
        if not target.is_file():
            raise TrainingError("Missing artifact file")
        if max_bytes is not None and target.stat().st_size > max_bytes:
            raise TrainingError("Artifact file exceeds its byte limit")
    return target


def require_sha(value, name="digest"):
    if not isinstance(value, str) or SHA256.fullmatch(value) is None:
        raise TrainingError(name + " must be SHA256")
    return value
