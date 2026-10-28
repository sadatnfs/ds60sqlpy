"""A local snapshot model with real Parquet and SQLite, not an Iceberg implementation."""

import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


def catalog(path):
    connection = sqlite3.connect(path)
    connection.execute(
        "create table if not exists snapshots(id integer primary key,manifest text not null)"
    )
    connection.execute(
        "create table if not exists current(id integer primary key,snapshot integer not null)"
    )
    connection.execute("insert or ignore into current values(1,0)")
    connection.commit()
    return connection


def data_file(root, name, rows):
    if not name.isalnum():
        raise ValueError("Invalid fixture name")
    path = root / (name + ".parquet")
    if path.exists():
        raise ValueError("The local data-file contract is immutable")
    table = pa.Table.from_pylist(
        rows, schema=pa.schema([("id", pa.string()), ("packages", pa.int64())])
    )
    pq.write_table(table, path)
    return {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def read_files(root, manifest):
    result = {}
    for item in manifest["files"]:
        name = item["file"]
        if Path(name).name != name:
            raise ValueError("Files must be owned basenames")
        path = root / name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Snapshot data identity changed")
        for row in pq.read_table(path).to_pylist():
            if row["id"] in result:
                raise ValueError("Snapshot contains a duplicated row identity")
            result[row["id"]] = row["packages"]
    for key in manifest["deleted_ids"]:
        result.pop(key, None)
    return dict(sorted(result.items()))


def commit(connection, root, snapshot, parent, files, deleted_ids):
    manifest = {"parent": parent, "files": files, "deleted_ids": sorted(set(deleted_ids))}
    read_files(root, manifest)
    with connection:
        connection.execute("begin immediate")
        observed = connection.execute("select snapshot from current where id=1").fetchone()[0]
        if observed != parent:
            raise ValueError("Snapshot parent changed; replan and validate before retrying")
        connection.execute(
            "insert into snapshots values(?,?)", (snapshot, json.dumps(manifest, sort_keys=True))
        )
        connection.execute("update current set snapshot=? where id=1", (snapshot,))
    return manifest


def read_snapshot(connection, root, snapshot):
    value = connection.execute("select manifest from snapshots where id=?", (snapshot,)).fetchone()
    if value is None:
        raise ValueError("Snapshot is not committed")
    return read_files(root, json.loads(value[0]))


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        connection = catalog(root / "catalog.db")
        try:
            original = data_file(
                root,
                "base",
                [
                    {"id": "A", "packages": 2},
                    {"id": "B", "packages": 3},
                    {"id": "C", "packages": 1},
                ],
            )
            commit(connection, root, 1, 0, [original], [])
            before = read_snapshot(connection, root, 1)
            added = data_file(root, "added", [{"id": "D", "packages": 4}])
            commit(connection, root, 2, 1, [original, added], ["B"])
            after = read_snapshot(connection, root, 2)
            assert before == {"A": 2, "B": 3, "C": 1} and after == {"A": 2, "C": 1, "D": 4}
            assert read_snapshot(connection, root, 1) == before
            return {
                "old_snapshot": before,
                "new_snapshot": after,
                "physical_B_still_in_old_file": True,
            }
        finally:
            connection.close()


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        connection = catalog(root / "catalog.db")
        try:
            base = data_file(root, "base", [{"id": "A", "packages": 2}])
            commit(connection, root, 1, 0, [base], [])
            winner = data_file(root, "winner", [{"id": "B", "packages": 3}])
            orphan = data_file(root, "uncommitted", [{"id": "C", "packages": 100}])
            commit(connection, root, 2, 1, [base, winner], [])
            try:
                commit(connection, root, 3, 1, [base, orphan], [])
            except ValueError:
                pass
            else:
                raise AssertionError("A stale writer committed over a newer snapshot")
            referenced = {
                item["file"]
                for (text,) in connection.execute("select manifest from snapshots")
                for item in json.loads(text)["files"]
            }
            unreferenced = sorted(
                path.name for path in root.glob("*.parquet") if path.name not in referenced
            )
            assert unreferenced == ["uncommitted.parquet"]
            assert connection.execute("select snapshot from current").fetchone() == (2,)
            assert read_snapshot(connection, root, 2) == {"A": 2, "B": 3}
            return {
                "accepted_snapshot": 2,
                "uncommitted_files_not_visible": unreferenced,
                "garbage_collection_was_not_performed": True,
            }
        finally:
            connection.close()


def main():
    print("Snapshots and logical deletion:", example_one())
    print("Concurrent-parent conflict and unreferenced files:", example_two())


if __name__ == "__main__":
    main()
