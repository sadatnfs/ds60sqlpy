"""The publisher's bounded observation journal, separate from the active pointer."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .contracts import (
    MAX_PUBLICATIONS,
    ConflictError,
    ContractError,
    StateError,
    canonical,
    owner_identity,
    strict_json,
)


class Journal:
    def __init__(self, directory: Path, owner: str) -> None:
        if directory.is_symlink() or not directory.is_dir():
            raise StateError("Publication control requires its owned existing directory")
        self.path = directory / "publications.sqlite"
        self.owner = owner_identity(owner)
        self.initializing = True
        try:
            with self.connect() as connection:
                connection.execute("BEGIN IMMEDIATE")
                version = connection.execute("PRAGMA user_version").fetchone()[0]
                if version == 0:
                    if connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall():
                        raise StateError("Refuse to replace an unknown publication journal")
                    connection.execute("CREATE TABLE metadata (owner TEXT NOT NULL)")
                    connection.execute("INSERT INTO metadata VALUES (?)", (self.owner,))
                    connection.execute(
                        "CREATE TABLE operations (id TEXT PRIMARY KEY, kind TEXT NOT NULL, "
                        "version_id TEXT NOT NULL, generation INTEGER NOT NULL, "
                        "body BLOB NOT NULL, phase TEXT NOT NULL, receipt BLOB)"
                    )
                    connection.execute(
                        "CREATE UNIQUE INDEX published_identity ON operations(version_id) "
                        "WHERE kind='publish'"
                    )
                    connection.execute("PRAGMA user_version=1")
                self.verify_owner(connection)
        finally:
            self.initializing = False

    def verify_owner(self, connection: sqlite3.Connection) -> None:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        owners = connection.execute("SELECT owner FROM metadata").fetchall()
        if version != 1 or len(owners) != 1 or owners[0][0] != self.owner:
            raise StateError("Publication journal schema or owner does not match")

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        if self.path.is_symlink() or (self.path.exists() and not self.path.is_file()):
            raise StateError("Publication journal must be a regular file")
        if self.path.exists() and self.path.stat().st_size > 16 * 1024 * 1024:
            raise StateError("Publication journal exceeds its state limit")
        connection = None
        try:
            connection = sqlite3.connect(self.path, timeout=2)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA busy_timeout=2000")
            connection.execute("PRAGMA journal_mode=DELETE")
            connection.execute("PRAGMA synchronous=FULL")
            if not self.initializing:
                self.verify_owner(connection)
            with connection:
                yield connection
        except sqlite3.Error as error:
            raise StateError("Publication journal operation could not be completed") from error
        finally:
            if connection is not None:
                connection.close()

    @staticmethod
    def record(row: sqlite3.Row) -> dict[str, Any]:
        try:
            body = strict_json(bytes(row["body"]))
            receipt = None if row["receipt"] is None else strict_json(bytes(row["receipt"]))
        except (ContractError, TypeError) as error:
            raise StateError("Publication journal JSON is malformed") from error
        if type(body) is not dict or (receipt is not None and type(receipt) is not dict):
            raise StateError("Publication journal record is malformed")
        return {
            "id": row["id"],
            "kind": row["kind"],
            "version_id": row["version_id"],
            "generation": row["generation"],
            "phase": row["phase"],
            "body": body,
            "receipt": receipt,
        }

    def get(self, identity: str) -> dict[str, Any]:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM operations WHERE id=?", (identity,)).fetchone()
        if row is None:
            raise StateError("Active operation has no matching journal record")
        return self.record(row)

    def for_publication(self, version_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM operations WHERE kind='publish' AND version_id=?", (version_id,)
            ).fetchone()
        return None if row is None else self.record(row)

    def prepare(
        self,
        identity: str,
        kind: str,
        version_id: str,
        generation: int,
        body: dict[str, Any],
        *,
        rejected: bool = False,
    ) -> dict[str, Any]:
        if kind not in {"publish", "rollback"}:
            raise StateError("Unknown controlled publication operation")
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            count = connection.execute("SELECT count(*) FROM operations").fetchone()[0]
            if count >= MAX_PUBLICATIONS:
                raise ConflictError("Publication history is full; existing evidence is retained")
            connection.execute(
                "INSERT INTO operations VALUES (?,?,?,?,?,?,?)",
                (
                    identity,
                    kind,
                    version_id,
                    generation,
                    canonical(body),
                    "rejected" if rejected else "prepared",
                    canonical(body) if rejected else None,
                ),
            )
        return self.get(identity)

    def observe(self, identity: str, receipt: dict[str, Any]) -> dict[str, Any]:
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM operations WHERE id=?", (identity,)).fetchone()
            if row is None:
                raise StateError("Cannot complete an unknown operation")
            record = self.record(row)
            if record["phase"] == "observed":
                if canonical(record["receipt"]) != canonical(receipt):
                    raise ConflictError("A completed observation is immutable")
                return record
            if record["phase"] != "prepared":
                raise StateError("Only a prepared operation can be observed as complete")
            connection.execute(
                "UPDATE operations SET phase='observed',receipt=? WHERE id=?",
                (canonical(receipt), identity),
            )
        return self.get(identity)

    def records(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM operations ORDER BY rowid").fetchall()
        if len(rows) > MAX_PUBLICATIONS:
            raise StateError("Publication history exceeds its declared limit")
        return [self.record(row) for row in rows]
