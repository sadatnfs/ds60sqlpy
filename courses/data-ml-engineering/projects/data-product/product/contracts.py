"""Fixed data, identity and bounded-file contracts for the owned workshop."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import uuid
from pathlib import Path
from typing import Any

MAX_BODY = 65_536
MAX_RECORDS = 64
MAX_SNAPSHOTS = 64
MAX_PUBLICATIONS = 128
MAX_PRODUCT_BYTES = 1_000_000
FORMAT = "delivery-snapshot-v1"
ROUTES = {10: "north", 20: "south"}
IDENTITY = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,47}")
HEX = re.compile(r"[0-9a-f]{64}")
OWNER = re.compile(r"[0-9a-f]{32}")
VERSION = re.compile(r"g[0-9]{7}-[0-9a-f]{12}-[0-9a-f]{12}-[0-9a-f]{12}")


class ContractError(ValueError):
    """Input does not satisfy the declared contract."""


class ConflictError(RuntimeError):
    """An immutable identity or monotone operation conflicts with saved state."""


class StateError(RuntimeError):
    """Owned stored state is incomplete, incompatible or cannot be verified."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("Duplicate JSON field")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ContractError("Nonfinite JSON constants are unsupported")


def strict_json(data: bytes, *, limit: int = MAX_BODY) -> Any:
    if not 1 <= len(data) <= limit:
        raise ContractError("JSON body is empty or exceeds its byte limit")
    try:
        return json.loads(
            data.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=reject_constant
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ContractError("Invalid strict UTF-8 JSON") from error


def bounded_integer(value: Any, low: int, high: int, name: str) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ContractError(f"{name} must be a bounded integer, not a boolean")
    return value


def identifier(value: Any, name: str = "Identity") -> str:
    if type(value) is not str or IDENTITY.fullmatch(value) is None:
        raise ContractError(f"{name} must contain 1 through 48 ASCII identity characters")
    return value


def validate_snapshot(value: Any) -> dict[str, Any]:
    if type(value) is not dict or set(value) != {
        "format",
        "batch_id",
        "generation",
        "expected_rows",
        "records",
    }:
        raise ContractError("Use the exact complete-snapshot request fields")
    if value["format"] != FORMAT:
        raise ContractError("Unsupported snapshot format")
    identifier(value["batch_id"], "Batch identity")
    bounded_integer(value["generation"], 1, 1_000_000, "Source generation")
    count = bounded_integer(value["expected_rows"], 1, MAX_RECORDS, "Expected row count")
    records = value["records"]
    if type(records) is not list or len(records) != count:
        raise ContractError("Record count does not match the declared complete snapshot")
    for record in records:
        if type(record) is not dict or set(record) != {"delivery_id", "route_id", "packages"}:
            raise ContractError("Use the exact delivery record fields")
        identity = identifier(record["delivery_id"], "Delivery identity")
        if len(identity) > 32:
            raise ContractError("Delivery identities allow at most 32 characters")
        bounded_integer(record["route_id"], 1, 1_000_000, "Route identity")
        # Meaning checks are deliberately separate from raw typed acceptance.
        bounded_integer(record["packages"], -1_000_000, 1_000_000, "Package count")
    return value


def read_regular(path: Path, limit: int) -> bytes:
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or not 1 <= info.st_size <= limit:
                raise StateError("Stored file is not a bounded regular file: " + path.name)
            data = stream.read(limit + 1)
    except OSError as error:
        raise StateError("Stored file cannot be read safely: " + path.name) from error
    if not 1 <= len(data) <= limit:
        raise StateError("Stored file exceeds its byte limit: " + path.name)
    return data


def sync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def replace_bytes(path: Path, data: bytes) -> None:
    if path.is_symlink() or not path.parent.is_dir():
        raise StateError("Atomic replacement requires an owned regular-file directory")
    temporary = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
        sync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def owner_identity(value: str) -> str:
    if OWNER.fullmatch(value) is None:
        raise StateError("Invalid saved workshop owner")
    return value
