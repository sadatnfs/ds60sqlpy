"""Controlled immutable publication with separate pointer and observation phases."""

from __future__ import annotations

import fcntl
import os
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .contracts import (
    HEX,
    MAX_BODY,
    MAX_PRODUCT_BYTES,
    MAX_PUBLICATIONS,
    MAX_RECORDS,
    OWNER,
    ROUTES,
    VERSION,
    ConflictError,
    ContractError,
    StateError,
    bounded_integer,
    canonical,
    digest,
    identifier,
    owner_identity,
    read_regular,
    replace_bytes,
    strict_json,
    sync_directory,
)
from .journal import Journal
from .raw_store import RawStore

POINTER_FIELDS = {
    "schema_version",
    "owner",
    "version_id",
    "generation",
    "high_water_generation",
    "epoch",
    "operation_id",
    "operation_kind",
}
MANIFEST_FIELDS = {
    "schema_version",
    "owner",
    "version_id",
    "generation",
    "batch_id",
    "request_sha256",
    "code_sha256",
    "runtime_image_id",
    "parquet_file",
    "parquet_sha256",
    "parquet_bytes",
    "source_rows",
    "source_packages",
    "product_rows",
    "encoding",
}


def image_identity(value: str) -> str:
    if (
        type(value) is not str
        or not value.startswith("sha256:")
        or HEX.fullmatch(value[7:]) is None
    ):
        raise StateError("Use the resolved prepared native image identity")
    return value


def producer_identity() -> str:
    root = Path(__file__).parent
    hashes = {
        name: digest(read_regular(root / name, 200_000))
        for name in ("contracts.py", "analysis.py", "journal.py", "publication.py")
    }
    return digest(canonical(hashes))


def version_identity(generation: int, source: str, code: str, image: str) -> str:
    return f"g{generation:07d}-{source[:12]}-{code[:12]}-{image[7:19]}"


def read_pointer(directory: Path, owner: str) -> tuple[dict[str, Any], bytes]:
    if directory.is_symlink() or not directory.is_dir():
        raise StateError("Publication directory is not an owned regular directory")
    path = directory / "active.json"
    if path.is_symlink():
        raise StateError("Active pointer cannot be a symbolic link")
    if not path.exists():
        raise FileNotFoundError("No analytical product has been published")
    data = read_regular(path, MAX_BODY)
    try:
        pointer = strict_json(data)
        if type(pointer) is not dict or set(pointer) != POINTER_FIELDS:
            raise ContractError("Unexpected pointer fields")
        if (
            type(pointer["schema_version"]) is not int
            or pointer["schema_version"] != 1
            or pointer["owner"] != owner
        ):
            raise ContractError("Incompatible pointer version or owner")
        if (
            type(pointer["version_id"]) is not str
            or VERSION.fullmatch(pointer["version_id"]) is None
        ):
            raise ContractError("Invalid active version identity")
        generation = bounded_integer(pointer["generation"], 1, 1_000_000, "Published generation")
        bounded_integer(
            pointer["high_water_generation"], generation, 1_000_000, "High-water generation"
        )
        bounded_integer(pointer["epoch"], 1, MAX_PUBLICATIONS, "Pointer epoch")
        if (
            type(pointer["operation_id"]) is not str
            or OWNER.fullmatch(pointer["operation_id"]) is None
        ):
            raise ContractError("Invalid pointer operation identity")
        if pointer["operation_kind"] not in {"publish", "rollback"}:
            raise ContractError("Invalid pointer operation kind")
    except (ContractError, TypeError, KeyError) as error:
        raise StateError("Active pointer failed its stored-state contract") from error
    return pointer, data


def read_version(
    directory: Path, owner: str, version_id: str
) -> tuple[dict[str, Any], list[dict[str, int]], str]:
    if VERSION.fullmatch(version_id) is None:
        raise StateError("Invalid retained version identity")
    versions = directory / "versions"
    version = versions / version_id
    if versions.is_symlink() or version.is_symlink() or not version.is_dir():
        raise StateError("Retained product version is not an owned directory")
    manifest_data = read_regular(version / "manifest.json", MAX_BODY)
    try:
        manifest = strict_json(manifest_data)
        if type(manifest) is not dict or set(manifest) != MANIFEST_FIELDS:
            raise ContractError("Unexpected product manifest fields")
        if (
            type(manifest["schema_version"]) is not int
            or manifest["schema_version"] != 1
            or manifest["owner"] != owner
            or manifest["version_id"] != version_id
        ):
            raise ContractError("Product version or ownership mismatch")
        generation = bounded_integer(manifest["generation"], 1, 1_000_000, "Generation")
        identifier(manifest["batch_id"], "Batch identity")
        for field in ("request_sha256", "code_sha256", "parquet_sha256"):
            if type(manifest[field]) is not str or HEX.fullmatch(manifest[field]) is None:
                raise ContractError("Invalid product content identity")
        image_identity(manifest["runtime_image_id"])
        if (
            version_identity(
                generation,
                manifest["request_sha256"],
                manifest["code_sha256"],
                manifest["runtime_image_id"],
            )
            != version_id
        ):
            raise ContractError("Version identity disagrees with its provenance")
        if (
            manifest["parquet_file"] != "routes.parquet"
            or manifest["encoding"] != "uncompressed-no-dictionary-v1"
        ):
            raise ContractError("Unsupported product file contract")
        size = bounded_integer(manifest["parquet_bytes"], 1, MAX_PRODUCT_BYTES, "Parquet size")
        source_rows = bounded_integer(manifest["source_rows"], 1, MAX_RECORDS, "Source rows")
        product_rows = bounded_integer(manifest["product_rows"], 1, len(ROUTES), "Product rows")
        source_packages = bounded_integer(
            manifest["source_packages"], 1, MAX_RECORDS * 1_000_000, "Source package total"
        )
    except (ContractError, TypeError, KeyError) as error:
        raise StateError("Product manifest failed its stored-state contract") from error
    data = read_regular(version / "routes.parquet", MAX_PRODUCT_BYTES)
    if len(data) != size or digest(data) != manifest["parquet_sha256"]:
        raise StateError("Published Parquet byte identity does not match")
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq

        parquet = pq.ParquetFile(pa.BufferReader(data))  # type: ignore[no-untyped-call]
        expected_schema = pa.schema(
            [("route_id", pa.int64()), ("deliveries", pa.int64()), ("packages", pa.int64())]
        )
        if not parquet.schema_arrow.equals(expected_schema, check_metadata=False):
            raise StateError("Published Parquet schema is incompatible")
        metadata = parquet.metadata
        if (
            metadata.num_rows != product_rows
            or metadata.num_row_groups != 1
            or metadata.num_columns != 3
        ):
            raise StateError("Published Parquet shape is incompatible")
        for index in range(3):
            column = metadata.row_group(0).column(index)
            if (
                column.compression != "UNCOMPRESSED"
                or column.dictionary_page_offset is not None
                or column.file_path not in {None, ""}
                or not 0 < column.total_uncompressed_size <= MAX_PRODUCT_BYTES
            ):
                raise StateError("Published Parquet encoding exceeds the bounded contract")
        rows = parquet.read().to_pylist()  # type: ignore[no-untyped-call]
    except StateError:
        raise
    except Exception as error:
        raise StateError("Published Parquet could not be decoded") from error
    expected_routes = []
    for row in rows:
        if set(row) != {"route_id", "deliveries", "packages"} or any(
            type(value) is not int for value in row.values()
        ):
            raise StateError("Published rows have incompatible types")
        if (
            row["route_id"] not in ROUTES
            or not 1 <= row["deliveries"] <= MAX_RECORDS
            or not 1 <= row["packages"] <= MAX_RECORDS * 1_000_000
        ):
            raise StateError("Published row values are outside the product contract")
        expected_routes.append(row["route_id"])
    if (
        expected_routes != sorted(set(expected_routes))
        or sum(row["deliveries"] for row in rows) != source_rows
        or sum(row["packages"] for row in rows) != source_packages
    ):
        raise StateError("Published population reconciliation failed")
    return manifest, rows, digest(manifest_data)


def read_product(directory: Path, owner: str) -> dict[str, Any]:
    pointer, _ = read_pointer(directory, owner)
    manifest, rows, _ = read_version(directory, owner, pointer["version_id"])
    if manifest["generation"] != pointer["generation"]:
        raise StateError("Active pointer and verified manifest generation disagree")
    return {"pointer": pointer, "manifest": manifest, "rows": rows}


class Publisher:
    def __init__(self, raw: Path, published: Path, control: Path, owner: str, image: str) -> None:
        for directory in (published, control):
            if directory.is_symlink() or not directory.is_dir():
                raise StateError("Use the explicit existing workshop state directories")
        self.owner, self.image = owner_identity(owner), image_identity(image)
        self.published, self.control = published, control
        self.raw = RawStore(raw, owner)
        self.journal = Journal(control, owner)

    @contextmanager
    def writer(self) -> Iterator[None]:
        descriptor = os.open(
            self.control / "publisher.lock", os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600
        )
        try:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise ConflictError("Another controlled publisher owns this state") from error
            yield
        finally:
            os.close(descriptor)

    def current(self) -> tuple[dict[str, Any] | None, str | None]:
        try:
            pointer, data = read_pointer(self.published, self.owner)
            return pointer, digest(data)
        except FileNotFoundError:
            return None, None

    def observe(self, pointer: dict[str, Any], *, recovered: bool) -> dict[str, Any]:
        operation = self.journal.get(pointer["operation_id"])
        if (
            operation["body"].get("pointer") != pointer
            or operation["version_id"] != pointer["version_id"]
            or operation["kind"] != pointer["operation_kind"]
        ):
            raise StateError("Active pointer does not match its prepared observation")
        manifest, _, manifest_sha = read_version(self.published, self.owner, pointer["version_id"])
        if manifest_sha != operation["body"].get("manifest_sha256"):
            raise StateError("Prepared observation names different immutable product bytes")
        if operation["phase"] == "observed":
            return operation
        receipt = {
            "operation_id": operation["id"],
            "kind": operation["kind"],
            "version_id": pointer["version_id"],
            "generation": pointer["generation"],
            "request_sha256": manifest["request_sha256"],
            "manifest_sha256": manifest_sha,
            "pointer_sha256": digest(canonical(pointer)),
            "completed_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "completion_observation": "recovered_after_pointer" if recovered else "normal",
            "raw_reingested": False,
            "immutable_product_rewritten": False,
        }
        return self.journal.observe(operation["id"], receipt)

    def reconcile(self) -> dict[str, Any] | None:
        pointer, _ = self.current()
        if pointer is None:
            return None
        return self.observe(pointer, recovered=True)

    def recover(self) -> dict[str, Any]:
        with self.writer():
            observed = self.reconcile()
            pointer, _ = self.current()
            pending = [
                {
                    "operation_id": record["id"],
                    "version_id": record["version_id"],
                    "generation": record["generation"],
                }
                for record in self.journal.records()
                if record["phase"] == "prepared"
                and (pointer is None or record["id"] != pointer["operation_id"])
            ]
            return {
                "status": "reconciled",
                "observation": observed,
                "pointer": pointer,
                "prepared_not_active": pending,
                "raw_reingested": False,
                "immutable_product_rewritten": False,
            }

    def prepare_version(self, packet: dict[str, Any], version_id: str, code: str) -> dict[str, Any]:
        import pyarrow.parquet as pq

        from .analysis import transform

        snapshot = packet["snapshot"]
        table, reasons, statistics = transform(snapshot)
        if reasons:
            return {"rejected": reasons, **statistics}
        assert table is not None
        versions, staging = self.published / "versions", self.published / ".staging"
        for directory in (versions, staging):
            if directory.is_symlink():
                raise StateError("Product directories cannot be symbolic links")
            directory.mkdir(exist_ok=True)
        destination = versions / version_id
        if destination.exists():
            manifest, _, _ = read_version(self.published, self.owner, version_id)
            return manifest
        candidate = staging / version_id
        if candidate.exists() or candidate.is_symlink():
            raise StateError("An incomplete staging version is retained for explicit investigation")
        candidate.mkdir()
        parquet = candidate / "routes.parquet"
        pq.write_table(  # type: ignore[no-untyped-call]
            table, parquet, compression=None, use_dictionary=False, row_group_size=2
        )
        with parquet.open("rb") as stream:
            os.fsync(stream.fileno())
        data = read_regular(parquet, MAX_PRODUCT_BYTES)
        manifest = {
            "schema_version": 1,
            "owner": self.owner,
            "version_id": version_id,
            "generation": snapshot["generation"],
            "batch_id": snapshot["batch_id"],
            "request_sha256": packet["receipt"]["request_sha256"],
            "code_sha256": code,
            "runtime_image_id": self.image,
            "parquet_file": "routes.parquet",
            "parquet_sha256": digest(data),
            "parquet_bytes": len(data),
            "source_rows": statistics["source_rows"],
            "source_packages": statistics["source_packages"],
            "product_rows": table.num_rows,
            "encoding": "uncompressed-no-dictionary-v1",
        }
        replace_bytes(candidate / "manifest.json", canonical(manifest))
        candidate.rename(destination)
        sync_directory(versions)
        checked, _, _ = read_version(self.published, self.owner, version_id)
        return checked

    def activate(
        self, operation: dict[str, Any], *, failpoint: str | None = None
    ) -> dict[str, Any]:
        expected = operation["body"]["pointer"]
        _, actual_previous = self.current()
        if actual_previous != operation["body"]["previous_pointer_sha256"]:
            raise ConflictError(
                "The prepared operation's base pointer changed; no automatic replay"
            )
        _, _, fresh_manifest_sha = read_version(self.published, self.owner, operation["version_id"])
        if fresh_manifest_sha != operation["body"].get("manifest_sha256"):
            raise StateError("Prepared immutable manifest changed; active pointer was retained")
        if failpoint == "before-pointer":
            os._exit(71)
        try:
            replace_bytes(self.published / "active.json", canonical(expected))
        except OSError as error:
            actual, _ = self.current()
            if actual == expected:
                return {
                    "status": "active",
                    "pointer": actual,
                    "reconciliation_required": True,
                    "storage_warning": "Pointer is readable; storage durability is uncertain",
                }
            raise StateError(
                "Pointer activation outcome is unknown; reconcile before another publication"
            ) from error
        if failpoint == "after-pointer":
            os._exit(72)
        try:
            observation = self.observe(expected, recovered=False)
        except StateError:
            return {
                "status": "active",
                "pointer": expected,
                "reconciliation_required": True,
                "storage_warning": "Pointer is active; its completion observation was not saved",
            }
        return {
            "status": "active",
            "pointer": expected,
            "observation": observation,
            "reconciliation_required": False,
        }

    def publish(self, batch_id: str, *, failpoint: str | None = None) -> dict[str, Any]:
        if failpoint not in {None, "before-pointer", "after-pointer"}:
            raise ContractError("Unknown controlled failure point")
        with self.writer():
            self.reconcile()
            pointer, previous_sha = self.current()
            packet = self.raw.get(batch_id)
            snapshot = packet["snapshot"]
            code = producer_identity()
            version = version_identity(
                snapshot["generation"], packet["receipt"]["request_sha256"], code, self.image
            )
            existing = self.journal.for_publication(version)
            if pointer is not None and pointer["version_id"] == version:
                return {"status": "already_current", "pointer": pointer, "observation": existing}
            high_water = 0 if pointer is None else pointer["high_water_generation"]
            if snapshot["generation"] <= high_water:
                raise ConflictError(
                    "Ordinary publication cannot downgrade the source high-water generation"
                )
            if existing is not None:
                if existing["phase"] == "rejected":
                    return {"status": "rejected", "observation": existing, "pointer": pointer}
                if existing["phase"] != "prepared":
                    raise ConflictError("Retained publication is not a new activation")
                return self.activate(existing, failpoint=failpoint)
            manifest = self.prepare_version(packet, version, code)
            identity = uuid.uuid4().hex
            if "rejected" in manifest:
                operation = self.journal.prepare(
                    identity,
                    "publish",
                    version,
                    snapshot["generation"],
                    {
                        "batch_id": batch_id,
                        "request_sha256": packet["receipt"]["request_sha256"],
                        "quality_reasons": manifest["rejected"],
                    },
                    rejected=True,
                )
                return {"status": "rejected", "observation": operation, "pointer": pointer}
            _, _, manifest_sha = read_version(self.published, self.owner, version)
            new_pointer = {
                "schema_version": 1,
                "owner": self.owner,
                "version_id": version,
                "generation": snapshot["generation"],
                "high_water_generation": snapshot["generation"],
                "epoch": 1 if pointer is None else pointer["epoch"] + 1,
                "operation_id": identity,
                "operation_kind": "publish",
            }
            operation = self.journal.prepare(
                identity,
                "publish",
                version,
                snapshot["generation"],
                {
                    "pointer": new_pointer,
                    "previous_pointer_sha256": previous_sha,
                    "manifest_sha256": manifest_sha,
                },
            )
            return self.activate(operation, failpoint=failpoint)

    def rollback(self, version_id: str, reason: str) -> dict[str, Any]:
        if type(reason) is not str or not reason.strip() or len(reason) > 200:
            raise ContractError("Explicit rollback requires a bounded nonempty reason")
        with self.writer():
            self.reconcile()
            pointer, previous_sha = self.current()
            if pointer is None:
                raise ConflictError("No active pointer exists to roll back")
            manifest, _, manifest_sha = read_version(self.published, self.owner, version_id)
            accepted = self.journal.for_publication(version_id)
            if accepted is None or accepted["phase"] != "observed":
                raise ConflictError("Rollback requires a retained completed publication")
            if pointer["version_id"] == version_id:
                return {"status": "already_current", "pointer": pointer}
            identity = uuid.uuid4().hex
            new_pointer = {
                "schema_version": 1,
                "owner": self.owner,
                "version_id": version_id,
                "generation": manifest["generation"],
                "high_water_generation": pointer["high_water_generation"],
                "epoch": pointer["epoch"] + 1,
                "operation_id": identity,
                "operation_kind": "rollback",
            }
            operation = self.journal.prepare(
                identity,
                "rollback",
                version_id,
                manifest["generation"],
                {
                    "pointer": new_pointer,
                    "previous_pointer_sha256": previous_sha,
                    "manifest_sha256": manifest_sha,
                    "reason": reason,
                },
            )
            return self.activate(operation)
