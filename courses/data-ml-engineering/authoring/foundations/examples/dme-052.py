"""Actual SQLite online backup and restore with explicit recovery-point evidence."""

import hashlib
import sqlite3
import tempfile
import time
from pathlib import Path


def database(path):
    connection = sqlite3.connect(path)
    connection.execute("pragma journal_mode=wal")
    connection.execute(
        "create table if not exists events(id text primary key not null,"
        "packages integer not null,committed_hour integer not null)"
    )
    connection.commit()
    return connection


def rows(connection):
    return connection.execute(
        "select id,packages,committed_hour from events order by id"
    ).fetchall()


def backup(source, path, backup_hour):
    if path.exists():
        raise ValueError("Backup target must be a fresh owned file")
    destination = sqlite3.connect(path)
    try:
        source.backup(destination)
        assert destination.execute("pragma integrity_check").fetchone() == ("ok",)
        snapshot = rows(destination)
    finally:
        destination.close()
    return {
        "schema_version": 1,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "backup_hour": backup_hour,
        "row_count": len(snapshot),
        "packages": sum(row[1] for row in snapshot),
    }


def restore(path, manifest, destination):
    if manifest["schema_version"] != 1 or destination.exists():
        raise ValueError("Unknown backup contract or nonempty restore destination")
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("Backup digest mismatch")
    source = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        if source.execute("pragma integrity_check").fetchone() != ("ok",):
            raise ValueError("Backup integrity check failed")
        snapshot = rows(source)
        if (
            len(snapshot) != manifest["row_count"]
            or sum(row[1] for row in snapshot) != manifest["packages"]
        ):
            raise ValueError("Backup population differs from its manifest")
        target = sqlite3.connect(destination)
        try:
            source.backup(target)
            assert rows(target) == snapshot
        finally:
            target.close()
    finally:
        source.close()
    return snapshot


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = database(root / "source.db")
        try:
            with source:
                source.executemany("insert into events values(?,?,?)", [("A", 2, 1), ("B", 3, 2)])
            manifest = backup(source, root / "backup.db", backup_hour=2)
            with source:
                source.execute("insert into events values('C',1,3)")
            started = time.perf_counter()
            recovered = restore(root / "backup.db", manifest, root / "restored.db")
            elapsed = time.perf_counter() - started
            assert recovered == [("A", 2, 1), ("B", 3, 2)] and len(rows(source)) == 3
            return {
                "restored_rows": recovered,
                "restored_packages": 5,
                "source_packages_before_loss": 6,
                "source_events_after_backup": 1,
                "declared_failure_hour": 4,
                "observed_recovery_point_gap_hours": 4 - manifest["backup_hour"],
                "measured_local_restore_seconds": elapsed,
                "local_timing_is_not_a_production_recovery_objective": True,
            }
        finally:
            source.close()


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = database(root / "accepted.db")
        try:
            with source:
                source.execute("insert into events values('A',2,1)")
            manifest = backup(source, root / "backup.db", backup_hour=1)
            original = rows(source)
            try:
                restore(
                    root / "backup.db", {**manifest, "schema_version": 2}, root / "unsupported.db"
                )
            except ValueError:
                pass
            else:
                raise AssertionError("An unknown backup schema was accepted")
            (root / "backup.db").write_bytes(b"changed-owned-backup")
            try:
                restore(root / "backup.db", manifest, root / "corrupt-restore.db")
            except ValueError:
                pass
            else:
                raise AssertionError("Changed backup bytes were accepted")
            assert (
                not (root / "unsupported.db").exists()
                and not (root / "corrupt-restore.db").exists()
            )
            assert rows(source) == original
            return {
                "unsupported_and_corrupt_backups_rejected": True,
                "accepted_database_unchanged": original,
                "failed_restore_targets_not_created": True,
            }
        finally:
            source.close()


def main():
    print("A real restored snapshot and its recovery gap:", example_one())
    print("Reject unusable backup candidates before replacing accepted state:", example_two())


if __name__ == "__main__":
    main()
