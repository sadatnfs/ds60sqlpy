"""Transactional raw snapshot acceptance, deliberately separate from publication."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .contracts import (
    MAX_SNAPSHOTS,
    ConflictError,
    ContractError,
    StateError,
    canonical,
    digest,
    identifier,
    owner_identity,
    strict_json,
    validate_snapshot,
)


class RawStore:
    def __init__(self, directory: Path, owner: str, *, writable: bool = False) -> None:
        if directory.is_symlink() or not directory.is_dir():
            raise StateError("Raw state requires its owned existing directory")
        self.path = directory / "snapshots.sqlite"
        self.owner, self.writable = owner_identity(owner), writable
        self._initializing = writable
        if self.path.is_symlink():
            raise StateError("Raw database cannot be a symbolic link")
        try:
            if writable:
                self.initialize()
            else:
                with self.connect():
                    pass
        finally:
            self._initializing = False

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        if self.path.is_symlink() or (self.path.exists() and not self.path.is_file()):
            raise StateError("Raw database must be a regular file")
        if self.path.exists() and self.path.stat().st_size > 16 * 1024 * 1024:
            raise StateError("Raw database exceeds the workshop state limit")
        uri = (
            "file:"
            + quote(str(self.path), safe="/")
            + ("?mode=rwc" if self.writable else "?mode=ro")
        )
        connection = None
        try:
            connection = sqlite3.connect(uri, uri=True, timeout=2)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA busy_timeout=2000")
            if self.writable:
                connection.execute("PRAGMA journal_mode=DELETE")
                connection.execute("PRAGMA synchronous=FULL")
            else:
                connection.execute("PRAGMA query_only=ON")
            if not self._initializing:
                self.verify_owner(connection)
            with connection:
                yield connection
        except sqlite3.Error as error:
            raise StateError("Raw SQLite operation could not be completed") from error
        finally:
            if connection is not None:
                connection.close()

    def verify_owner(self, connection: sqlite3.Connection) -> None:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        owner = connection.execute("SELECT owner FROM metadata").fetchall()
        if version != 1 or len(owner) != 1 or owner[0][0] != self.owner:
            raise StateError("Raw database schema or workshop ownership does not match")

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version == 0:
                tables = connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
                if tables:
                    raise StateError("Refuse to replace an unknown raw database schema")
                connection.execute("CREATE TABLE metadata (owner TEXT NOT NULL)")
                connection.execute(
                    "CREATE TABLE snapshots (batch_id TEXT PRIMARY KEY, "
                    "generation INTEGER UNIQUE NOT NULL, "
                    "request_sha256 TEXT NOT NULL, body BLOB NOT NULL, receipt BLOB NOT NULL)"
                )
                connection.execute("INSERT INTO metadata(owner) VALUES (?)", (self.owner,))
                connection.execute("PRAGMA user_version=1")
            elif version != 1:
                raise StateError("Unsupported raw database version")
            owner = connection.execute("SELECT owner FROM metadata").fetchall()
            if len(owner) != 1 or owner[0][0] != self.owner:
                raise StateError("Raw database belongs to another workshop")

    def accept(self, value: Any) -> tuple[dict[str, Any], bool]:
        if not self.writable:
            raise StateError("This raw-store view is read-only")
        request = validate_snapshot(value)
        body = canonical(request)
        identity = digest(body)
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            previous = connection.execute(
                "SELECT body,request_sha256,receipt FROM snapshots WHERE batch_id=?",
                (request["batch_id"],),
            ).fetchone()
            if previous is not None:
                if previous["request_sha256"] != identity:
                    raise ConflictError("Batch identity already names different canonical content")
                return self.packet(previous)["receipt"], False
            occupied = connection.execute(
                "SELECT batch_id FROM snapshots WHERE generation=?", (request["generation"],)
            ).fetchone()
            if occupied is not None:
                raise ConflictError("Source generation already belongs to another batch")
            count, maximum = connection.execute(
                "SELECT count(*),coalesce(max(generation),0) FROM snapshots"
            ).fetchone()
            if count >= MAX_SNAPSHOTS:
                raise ConflictError("Raw snapshot history is full; existing records are retained")
            if request["generation"] <= maximum:
                raise ConflictError("A new raw snapshot must advance the source generation")
            receipt = {
                "batch_id": request["batch_id"],
                "generation": request["generation"],
                "request_sha256": identity,
                "rows": len(request["records"]),
                "received_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "raw_accepted": True,
                "analytical_publication": "not_attempted",
            }
            connection.execute(
                "INSERT INTO snapshots VALUES (?,?,?,?,?)",
                (request["batch_id"], request["generation"], identity, body, canonical(receipt)),
            )
        return receipt, True

    def get(self, batch_id: str) -> dict[str, Any]:
        identifier(batch_id, "Batch identity")
        with self.connect() as connection:
            row = connection.execute(
                "SELECT body,receipt,request_sha256 FROM snapshots WHERE batch_id=?", (batch_id,)
            ).fetchone()
        if row is None:
            raise KeyError("Unknown raw snapshot")
        return self.packet(row)

    @staticmethod
    def packet(row: sqlite3.Row) -> dict[str, Any]:
        try:
            body = bytes(row["body"])
            if digest(body) != row["request_sha256"]:
                raise StateError("Raw snapshot failed its stored content identity")
            snapshot = validate_snapshot(strict_json(body))
            receipt = strict_json(bytes(row["receipt"]))
            expected = {
                "batch_id",
                "generation",
                "request_sha256",
                "rows",
                "received_at",
                "raw_accepted",
                "analytical_publication",
            }
            if type(receipt) is not dict or set(receipt) != expected:
                raise StateError("Raw receipt has incompatible fields")
            if (
                receipt["batch_id"] != snapshot["batch_id"]
                or type(receipt["generation"]) is not int
                or receipt["generation"] != snapshot["generation"]
                or type(receipt["rows"]) is not int
                or receipt["rows"] != len(snapshot["records"])
                or receipt["request_sha256"] != digest(body)
                or receipt["raw_accepted"] is not True
                or receipt["analytical_publication"] != "not_attempted"
                or type(receipt["received_at"]) is not str
            ):
                raise StateError("Raw receipt disagrees with its immutable snapshot")
            return {"snapshot": snapshot, "receipt": receipt}
        except (ContractError, TypeError, KeyError) as error:
            raise StateError("Stored raw snapshot or receipt is malformed") from error

    def receipts(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT body,request_sha256,receipt FROM snapshots ORDER BY generation"
            ).fetchall()
        if len(rows) > MAX_SNAPSHOTS:
            raise StateError("Raw snapshot history exceeds its declared bound")
        return [self.packet(row)["receipt"] for row in rows]
