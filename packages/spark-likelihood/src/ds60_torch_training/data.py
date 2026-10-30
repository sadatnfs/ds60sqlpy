# SPDX-License-Identifier: Apache-2.0
"""Bounded immutable JSONL snapshots and explicit logical-rank assignments.

The DataFrame adapter executes writers on Spark workers and collects metadata
only. Importing this module requires neither PySpark nor Torch.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Any

from .contracts import MAX_WORLD_SIZE, TrainingError, canonical_json, finite

KIND = "ds60-torch-row-shards"
ASSIGNMENT_KIND = "ds60-torch-shard-assignment"
MANIFEST = "manifest.json"
FILE_PATTERN = re.compile(r"shards/part-[0-9]{5}\.jsonl\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class DataLimits:
    max_rows: int = 32768
    max_features: int = 64
    max_shards: int = 64
    max_shard_bytes: int = 8 * 1024 * 1024
    max_total_bytes: int = 64 * 1024 * 1024
    max_manifest_bytes: int = 1024 * 1024
    max_id_bytes: int = 256
    max_source_bytes: int = 16384


def _limits(value: DataLimits | None) -> DataLimits:
    value = DataLimits() if value is None else value
    if type(value) is not DataLimits:
        raise TrainingError("limits must be DataLimits")
    ceiling = DataLimits()
    for field in fields(value):
        _integer(getattr(value, field.name), field.name, 1, getattr(ceiling, field.name))
    return value


def _integer(value: Any, name: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise TrainingError(f"{name} must be an exact integer in [{low}, {high}]")
    return value


def _number(value: Any, name: str, *, nonnegative: bool = False) -> float:
    return finite(value, name, minimum=0 if nonnegative else None)


def _json(value: Any, limit: int) -> bytes:
    try:
        raw = canonical_json(value, limit=limit)
    except (ValueError, TypeError, OverflowError, UnicodeError) as error:
        raise TrainingError("Invalid bounded canonical JSON") from error
    if not isinstance(raw, bytes) or len(raw) > limit:
        raise TrainingError("Canonical JSON byte contract violated")
    return raw


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _digest(value: Any, limit: int = 1024 * 1024) -> str:
    return _sha(_json(value, limit))


def _keys(value: Any, expected: set[str], name: str) -> dict:
    if type(value) is not dict or set(value) != expected:
        raise TrainingError(f"Unexpected {name} fields")
    return value


def _decode(raw: bytes) -> Any:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise TrainingError("Duplicate JSON key")
            result[key] = value
        return result

    def invalid(value):
        raise TrainingError("Nonfinite JSON constant: " + value)

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=invalid)
    except (UnicodeError, ValueError, TypeError, RecursionError) as error:
        raise TrainingError("Invalid JSON document") from error


def _schema(feature_names: Any, label_kind: Any, limits: DataLimits) -> list[str]:
    if type(feature_names) is not list or not 1 <= len(feature_names) <= limits.max_features:
        raise TrainingError("feature_names must be a bounded ordered list")
    try:
        invalid = any(
            type(name) is not str or not name or len(name.encode("utf-8")) > 256 or "\x00" in name
            for name in feature_names
        )
    except UnicodeError as error:
        raise TrainingError("Invalid feature Unicode") from error
    if invalid:
        raise TrainingError("Invalid feature name")
    if len(set(feature_names)) != len(feature_names):
        raise TrainingError("Duplicate feature name")
    if label_kind not in ("float", "class_index") or type(label_kind) is not str:
        raise TrainingError("label_kind must be float or class_index")
    return list(feature_names)


def _id(value: Any, limits: DataLimits) -> str | int:
    if type(value) is int:
        return _integer(value, "row ID", -(2**63), 2**63 - 1)
    if type(value) is str and value and "\x00" not in value:
        try:
            if len(value.encode("utf-8")) <= limits.max_id_bytes:
                return value
        except UnicodeError:
            pass
    raise TrainingError("Row ID must be a bounded nonempty string or exact int64")


def _row(value: Any, feature_names: list[str], label_kind: str, limits: DataLimits) -> dict:
    if not isinstance(value, Mapping) or set(value) not in (
        {"id", "features", "label"},
        {"id", "features", "label", "weight"},
    ):
        raise TrainingError("Rows require exactly id, features, label and optional weight")
    features = value["features"]
    if type(features) not in (list, tuple) or len(features) != len(feature_names):
        raise TrainingError("Row features do not match ordered feature_names")
    label = (
        _integer(value["label"], "class label", 0, 2**63 - 1)
        if label_kind == "class_index"
        else _number(value["label"], "label")
    )
    return {
        "id": _id(value["id"], limits),
        "features": [_number(item, "feature") for item in features],
        "label": label,
        "weight": _number(value.get("weight", 1.0), "weight", nonnegative=True),
    }


def _sum(values: Iterable[float]) -> float:
    try:
        value = math.fsum(values)
    except (OverflowError, ValueError) as error:
        raise TrainingError("Weight sum overflows float64") from error
    if not math.isfinite(value):
        raise TrainingError("Weight sum must remain finite")
    return value


def _path(path: Path | str) -> Path:
    value = Path(path).absolute()
    if ".." in value.parts:
        raise TrainingError("Paths may not contain parent traversal")
    for item in (value, *value.parents):
        if item.is_symlink():
            raise TrainingError("Symlink paths are not admitted")
    return value


def _reserve(directory: Path | str) -> Path:
    root = _path(directory)
    if not root.parent.is_dir():
        raise TrainingError("Snapshot parent must already exist")
    try:
        root.mkdir(mode=0o700)
        (root / ".staging").mkdir(mode=0o700)
        (root / "shards").mkdir(mode=0o700)
    except FileExistsError as error:
        raise TrainingError("Snapshot path already exists; use a fresh owned attempt") from error
    return root


def _read(path: Path, limit: int) -> bytes:
    path = _path(path)
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as stream:
            status = os.fstat(stream.fileno())
            if not stat.S_ISREG(status.st_mode) or not 0 < status.st_size <= limit:
                raise TrainingError("File is not a bounded regular file")
            raw = stream.read(limit + 1)
            if len(raw) > limit or len(raw) != status.st_size:
                raise TrainingError("File changed or exceeds its byte bound")
            return raw
    except OSError as error:
        raise TrainingError("Cannot read admitted snapshot file") from error


def _sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_partition(rows, root: Path, index: int, feature_names, label_kind, limits) -> dict:
    filename = f"part-{index:05d}.jsonl"
    path = root / ".staging" / filename
    count = size = 0
    weights = []
    seen = set()
    content = hashlib.sha256()
    ids = hashlib.sha256()
    try:
        with path.open("xb") as stream:
            for raw in rows:
                row = _row(raw, feature_names, label_kind, limits)
                identity = _json(row["id"], 6 * limits.max_id_bytes + 32)
                if identity in seen:
                    raise TrainingError("Duplicate row ID in shard")
                seen.add(identity)
                count += 1
                if count > limits.max_rows:
                    raise TrainingError("Shard exceeds row bound")
                line = _json(row, limits.max_shard_bytes) + b"\n"
                size += len(line)
                if size > limits.max_shard_bytes:
                    raise TrainingError("Shard exceeds byte bound")
                stream.write(line)
                content.update(line)
                ids.update(identity + b"\n")
                weights.append(row["weight"])
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as error:
        raise TrainingError("Shard writer retry or duplicate output refused") from error
    return {
        "path": "shards/" + filename,
        "bytes": size,
        "sha256": content.hexdigest(),
        "rows": count,
        "weight_sum": _sum(weights),
        "ordered_id_sha256": ids.hexdigest(),
    }


def _validate_manifest(value: Any, limits: DataLimits) -> dict:
    _keys(
        value,
        {
            "schema_version",
            "kind",
            "feature_names",
            "label_kind",
            "source_metadata",
            "files",
            "rows",
            "weight_sum",
            "dataset_digest",
        },
        "manifest",
    )
    _integer(value["schema_version"], "schema_version", 1, 1)
    if value["kind"] != KIND:
        raise TrainingError("Unknown row-shard manifest kind")
    _schema(value["feature_names"], value["label_kind"], limits)
    if type(value["source_metadata"]) is not dict:
        raise TrainingError("source_metadata must be an object")
    _json(value["source_metadata"], limits.max_source_bytes)
    files = value["files"]
    if type(files) is not list or not 1 <= len(files) <= limits.max_shards:
        raise TrainingError("Invalid shard file list")
    names = []
    for item in files:
        _keys(
            item,
            {"path", "bytes", "sha256", "rows", "weight_sum", "ordered_id_sha256"},
            "shard metadata",
        )
        if type(item["path"]) is not str or FILE_PATTERN.fullmatch(item["path"]) is None:
            raise TrainingError("Unsafe shard path")
        names.append(item["path"])
        _integer(item["bytes"], "shard bytes", 0, limits.max_shard_bytes)
        _integer(item["rows"], "shard rows", 0, limits.max_rows)
        _number(item["weight_sum"], "shard weight sum", nonnegative=True)
        if (item["rows"] == 0) != (item["bytes"] == 0):
            raise TrainingError("Empty shard count/bytes disagree")
        if item["rows"] == 0 and (
            item["weight_sum"] != 0
            or item["sha256"] != _sha(b"")
            or item["ordered_id_sha256"] != _sha(b"")
        ):
            raise TrainingError("Empty shard identities disagree")
        if any(
            type(item[key]) is not str or HEX.fullmatch(item[key]) is None
            for key in ("sha256", "ordered_id_sha256")
        ):
            raise TrainingError("Invalid shard SHA256")
    if names != sorted(set(names)):
        raise TrainingError("Shard files must be unique and ordered")
    _integer(value["rows"], "dataset rows", 1, limits.max_rows)
    if (
        value["rows"] != sum(x["rows"] for x in files)
        or sum(x["bytes"] for x in files) > limits.max_total_bytes
    ):
        raise TrainingError("Dataset totals exceed bounds or disagree")
    weight = _number(value["weight_sum"], "dataset weight sum", nonnegative=True)
    if weight <= 0 or weight != _sum(x["weight_sum"] for x in files):
        raise TrainingError("Dataset must have the exact positive weight sum")
    body = {key: item for key, item in value.items() if key != "dataset_digest"}
    if value["dataset_digest"] != _digest(body, limits.max_manifest_bytes):
        raise TrainingError("Dataset digest mismatch")
    _json(value, limits.max_manifest_bytes)
    return value


def _commit(root, files, feature_names, label_kind, source_metadata, limits) -> Path:
    files = sorted(files, key=lambda item: item["path"])
    body = {
        "schema_version": 1,
        "kind": KIND,
        "feature_names": feature_names,
        "label_kind": label_kind,
        "source_metadata": source_metadata,
        "files": files,
        "rows": sum(item["rows"] for item in files),
        "weight_sum": _sum(item["weight_sum"] for item in files),
    }
    manifest = {**body, "dataset_digest": _digest(body, limits.max_manifest_bytes)}
    _validate_manifest(manifest, limits)
    for item in files:
        source = _path(root / ".staging" / Path(item["path"]).name)
        if not source.is_file() or source.stat().st_size != item["bytes"]:
            raise TrainingError("Staged shard missing or changed")
        source.chmod(0o444)
        os.link(source, root / item["path"], follow_symlinks=False)
    _sync_directory(root / "shards")
    staged = root / ".staging" / MANIFEST
    with staged.open("xb") as stream:
        stream.write(_json(manifest, limits.max_manifest_bytes))
        stream.flush()
        os.fsync(stream.fileno())
    # Hard-link creation is atomic and refuses any pre-existing destination.
    staged.chmod(0o444)
    os.link(staged, root / MANIFEST, follow_symlinks=False)
    _sync_directory(root)
    for item in files:
        (root / ".staging" / Path(item["path"]).name).unlink()
    staged.unlink()
    (root / ".staging").rmdir()
    return root / MANIFEST


def _metadata(value, limits):
    value = {} if value is None else value
    if type(value) is not dict:
        raise TrainingError("source_metadata must be a JSON object")
    return _decode(_json(value, limits.max_source_bytes))


def prepare_rows(
    rows: Iterable[Mapping],
    directory: Path | str,
    *,
    feature_names: list[str],
    label_kind: str = "float",
    num_shards: int = 1,
    source_metadata: dict | None = None,
    limits: DataLimits | None = None,
) -> Path:
    """Prepare already bounded local fixtures; never use this to collect Spark rows."""
    limits = _limits(limits)
    names = _schema(feature_names, label_kind, limits)
    _integer(num_shards, "num_shards", 1, limits.max_shards)
    metadata = _metadata(source_metadata, limits)
    partitions = [[] for _ in range(num_shards)]
    seen = set()
    for index, raw in enumerate(rows):
        if index >= limits.max_rows:
            raise TrainingError("Fixture exceeds row bound")
        row = _row(raw, names, label_kind, limits)
        identity = _json(row["id"], 6 * limits.max_id_bytes + 32)
        if identity in seen:
            raise TrainingError("Duplicate global row ID")
        seen.add(identity)
        partitions[index % num_shards].append(row)
    root = _reserve(directory)
    files = [
        _write_partition(partition, root, index, names, label_kind, limits)
        for index, partition in enumerate(partitions)
    ]
    return _commit(root, files, names, label_kind, metadata, limits)


def prepare_dataframe(
    frame,
    directory: Path | str,
    *,
    feature_names: list[str],
    label_col: str,
    id_col: str,
    label_kind: str = "float",
    weight_col: str | None = None,
    num_shards: int = 2,
    source_metadata: dict | None = None,
    limits: DataLimits | None = None,
) -> Path:
    """Materialize rank-independent shards in executor tasks; collect metadata only.

    The explicit shared directory must be visible at the same path on every
    executor. Writer retries fail; failed staging remains for investigation.
    """
    limits = _limits(limits)
    names = _schema(feature_names, label_kind, limits)
    _integer(num_shards, "num_shards", 1, limits.max_shards)
    metadata = _metadata(source_metadata, limits)
    if frame.isStreaming:
        raise TrainingError("Streaming frames are not immutable snapshots")
    if getattr(frame, "_jdf", None) is None:
        raise TrainingError("Snapshot preparation requires a Spark Classic DataFrame")
    from pyspark import TaskContext
    from pyspark.sql import functions as F
    from pyspark.sql.types import (
        ByteType,
        DoubleType,
        FloatType,
        IntegerType,
        LongType,
        ShortType,
        StringType,
    )

    columns = [id_col, *names, label_col] + ([] if weight_col is None else [weight_col])
    if any(
        type(name) is not str or not name or name.startswith("__ds60_") for name in columns
    ) or len(set(columns)) != len(columns):
        raise TrainingError("Selected columns must be distinct names without reserved prefix")
    if len(set(frame.columns)) != len(frame.columns) or any(
        name.startswith("__ds60_") for name in frame.columns
    ):
        raise TrainingError("Duplicate or reserved input column")
    schema = {field.name: field.dataType for field in frame.schema.fields}
    if any(name not in schema for name in columns):
        raise TrainingError("Required input column is absent")
    ints = (ByteType, ShortType, IntegerType, LongType)
    numeric = (*ints, FloatType, DoubleType)
    if not isinstance(schema[id_col], (*ints, StringType)):
        raise TrainingError("ID column must be string or integer")
    if (
        isinstance(schema[id_col], StringType)
        and getattr(schema[id_col], "collation", "UTF8_BINARY") != "UTF8_BINARY"
    ):
        raise TrainingError("String IDs require explicit binary collation")
    if any(
        not isinstance(schema[name], numeric)
        for name in names + ([weight_col] if weight_col else [])
    ):
        raise TrainingError("Features/weights must use explicit numeric Spark types")
    if not isinstance(schema[label_col], ints if label_kind == "class_index" else numeric):
        raise TrainingError("Label column has the wrong declared type")

    def col(name):
        return F.col("`" + name.replace("`", "``") + "`")

    selected = frame.select(
        col(id_col).alias("__ds60_id"),
        *[col(name).alias(f"__ds60_feature_{index:04d}") for index, name in enumerate(names)],
        col(label_col).alias("__ds60_label"),
        (F.lit(1.0) if weight_col is None else col(weight_col)).alias("__ds60_weight"),
    )
    # Equal IDs reach the same hash partition, so local duplicate rejection is
    # a global duplicate rejection. Sorting gives a declared stable order.
    selected = selected.repartition(num_shards, "__ds60_id").sortWithinPartitions("__ds60_id")
    # Bound worst-case staged payload bytes even before aggregate row admission.
    per_file_bytes = min(limits.max_shard_bytes, limits.max_total_bytes // num_shards)
    if per_file_bytes < 1:
        raise TrainingError("Total byte budget cannot admit the requested shard count")
    writer_limits = replace(limits, max_shard_bytes=per_file_bytes)
    root = _reserve(directory)

    def write(index, records):
        context = TaskContext.get()
        if context is None or context.attemptNumber() != 0 or context.partitionId() != index:
            raise TrainingError("Snapshot writer retry or task identity mismatch")
        normalized = (
            {
                "id": row[0],
                "features": list(row[1 : 1 + len(names)]),
                "label": row[1 + len(names)],
                "weight": row[2 + len(names)],
            }
            for row in records
        )
        yield _write_partition(normalized, root, index, names, label_kind, writer_limits)

    rdd = selected.rdd
    if rdd.getNumPartitions() != num_shards:
        raise TrainingError("Actual writer partition count differs from requested shards")
    metadata_files = rdd.mapPartitionsWithIndex(write).collect()
    if len(metadata_files) != num_shards or {item["path"] for item in metadata_files} != {
        f"shards/part-{index:05d}.jsonl" for index in range(num_shards)
    }:
        raise TrainingError("Missing or duplicated executor shard receipt")
    return _commit(root, metadata_files, names, label_kind, metadata, limits)


def load_manifest(manifest_path: Path | str, *, limits: DataLimits | None = None) -> dict:
    """Read and validate bounded metadata without reading observation payloads."""
    limits = _limits(limits)
    path = _path(manifest_path)
    if path.name != MANIFEST:
        raise TrainingError("Snapshot manifest must be named manifest.json")
    return _validate_manifest(_decode(_read(path, limits.max_manifest_bytes)), limits)


def assign_shards(
    manifest: dict,
    world_size: int,
    *,
    rank_files: Sequence[Sequence[str]] | None = None,
) -> dict:
    limits = DataLimits()
    manifest = _validate_manifest(manifest, limits)
    _integer(world_size, "world_size", 1, min(limits.max_shards, MAX_WORLD_SIZE))
    files = {item["path"]: item for item in manifest["files"]}
    if rank_files is None:
        rank_files = [list(files)[rank::world_size] for rank in range(world_size)]
    if type(rank_files) not in (list, tuple) or len(rank_files) != world_size:
        raise TrainingError("Rank mapping must have exactly world_size entries")
    ranks = []
    assigned = []
    for rank, paths in enumerate(rank_files):
        if type(paths) not in (list, tuple) or any(
            type(path) is not str or path not in files for path in paths
        ):
            raise TrainingError("Unknown shard in rank assignment")
        count = sum(files[path]["rows"] for path in paths)
        if count <= 0:
            raise TrainingError("Every logical rank must own positive rows")
        ranks.append(
            {
                "rank": rank,
                "files": list(paths),
                "rows": count,
                "weight_sum": _sum(files[path]["weight_sum"] for path in paths),
            }
        )
        assigned.extend(paths)
    if len(assigned) != len(set(assigned)) or set(assigned) != set(files):
        raise TrainingError("Rank assignment duplicates or omits shard files")
    body = {
        "schema_version": 1,
        "kind": ASSIGNMENT_KIND,
        "dataset_digest": manifest["dataset_digest"],
        "world_size": world_size,
        "ranks": ranks,
    }
    return {**body, "assignment_digest": _digest(body)}


def _assignment(value, manifest):
    _keys(
        value,
        {
            "schema_version",
            "kind",
            "dataset_digest",
            "world_size",
            "ranks",
            "assignment_digest",
        },
        "rank assignment",
    )
    _integer(value["schema_version"], "assignment schema_version", 1, 1)
    if value["kind"] != ASSIGNMENT_KIND or value["dataset_digest"] != manifest["dataset_digest"]:
        raise TrainingError("Assignment is not bound to this dataset")
    world = _integer(value["world_size"], "world_size", 1, MAX_WORLD_SIZE)
    if type(value["ranks"]) is not list or len(value["ranks"]) != world:
        raise TrainingError("Invalid rank records")
    paths = []
    for rank, item in enumerate(value["ranks"]):
        _keys(item, {"rank", "files", "rows", "weight_sum"}, "rank record")
        _integer(item["rank"], "rank", rank, rank)
        _integer(item["rows"], "rank rows", 1, DataLimits().max_rows)
        _number(item["weight_sum"], "rank weight sum", nonnegative=True)
        paths.append(item["files"])
    if value != assign_shards(manifest, world, rank_files=paths):
        raise TrainingError("Assignment digest/count/layout mismatch")
    return value


def iter_rank_rows(
    manifest_path: Path | str,
    assignment: dict,
    rank: int,
    *,
    limits: DataLimits | None = None,
) -> Iterator[dict]:
    """Verify all assigned payloads before yielding the first training observation."""
    limits = _limits(limits)
    manifest = load_manifest(manifest_path, limits=limits)
    assignment = _assignment(assignment, manifest)
    _integer(rank, "rank", 0, assignment["world_size"] - 1)
    root = _path(manifest_path).parent
    lookup = {item["path"]: item for item in manifest["files"]}
    verified = []
    seen = set()
    for name in assignment["ranks"][rank]["files"]:
        item = lookup[name]
        if item["bytes"] == 0:
            path = _path(root / name)
            if not path.is_file() or path.stat().st_size != 0:
                raise TrainingError("Empty shard missing or changed")
            continue
        raw = _read(root / name, limits.max_shard_bytes)
        if len(raw) != item["bytes"] or _sha(raw) != item["sha256"]:
            raise TrainingError("Shard byte identity mismatch")
        if not raw.endswith(b"\n"):
            raise TrainingError("Canonical shard must end every row with LF")
        count = 0
        weights = []
        ids = hashlib.sha256()
        for line in raw.splitlines(keepends=True):
            decoded = _decode(line)
            row = _row(decoded, manifest["feature_names"], manifest["label_kind"], limits)
            if _json(row, limits.max_shard_bytes) + b"\n" != line:
                raise TrainingError("Noncanonical or differently typed shard row")
            identity = _json(row["id"], 6 * limits.max_id_bytes + 32)
            if identity in seen:
                raise TrainingError("Repeated row ID across assigned shards")
            seen.add(identity)
            count += 1
            if count > item["rows"] or len(verified) >= limits.max_rows:
                raise TrainingError("Observed rows exceed declared bound")
            ids.update(identity + b"\n")
            weights.append(row["weight"])
            verified.append(row)
        if (
            count != item["rows"]
            or _sum(weights) != item["weight_sum"]
            or ids.hexdigest() != item["ordered_id_sha256"]
        ):
            raise TrainingError("Observed shard rows/weights/ID order differ from manifest")
    if len(verified) != assignment["ranks"][rank]["rows"]:
        raise TrainingError("Observed rank coverage differs from assignment")
    yield from verified
