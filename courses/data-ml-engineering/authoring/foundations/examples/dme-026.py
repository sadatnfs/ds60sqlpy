"""Actual Parquet manifests and directional schema evolution through DuckDB."""

import hashlib
import tempfile
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq


def write_file(root, name, table):
    if not name.isalnum():
        raise ValueError("Use a simple owned fixture name")
    path = root / (name + ".parquet")
    if path.exists():
        raise ValueError("Immutable fixture already exists")
    pq.write_table(table, path)
    return {
        "file": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": table.num_rows,
    }


def read_manifest(root, manifest, require_region=False):
    if not isinstance(manifest, list) or not 1 <= len(manifest) <= 5:
        raise ValueError("Use a bounded nonempty file manifest")
    paths = []
    expected_rows = 0
    for item in manifest:
        name = item["file"]
        if not isinstance(name, str) or Path(name).name != name or not name.endswith(".parquet"):
            raise ValueError("Manifest file must be an owned basename")
        path = root / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 100_000:
            raise ValueError("Missing, linked or oversized fixture")
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Manifest digest mismatch")
        schema = pq.read_schema(path)
        if not {"delivery_id", "packages"} <= set(schema.names):
            raise ValueError("Required identity or count field was removed")
        if (
            schema.field("delivery_id").type != pa.string()
            or schema.field("packages").type != pa.int64()
        ):
            raise ValueError("Required identity or count type changed")
        if "region" in schema.names and schema.field("region").type != pa.string():
            raise ValueError("Optional region type changed")
        paths.append(str(path))
        expected_rows += item["rows"]
    if len(set(paths)) != len(paths):
        raise ValueError("Repeated manifest file would duplicate observations")
    with duckdb.connect(":memory:") as connection:
        relation = connection.read_parquet(paths, union_by_name=True)
        columns = relation.columns
        query = (
            "delivery_id,packages,region"
            if "region" in columns
            else "delivery_id,packages,NULL AS region"
        )
        rows = relation.project(query).order("delivery_id").fetchall()
    if len(rows) != expected_rows or len({row[0] for row in rows}) != len(rows):
        raise ValueError("Manifest population or unique delivery grain failed")
    if any(row[0] is None or not row[0] or row[1] is None or row[1] < 0 for row in rows):
        raise ValueError("Required values failed the row contract")
    if require_region and any(row[2] is None for row in rows):
        raise ValueError("The new consumer requires unavailable historical regions")
    return rows


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        old = write_file(root, "old", pa.table({"delivery_id": ["A", "B"], "packages": [2, 3]}))
        new = write_file(
            root, "new", pa.table({"delivery_id": ["C"], "packages": [1], "region": ["north"]})
        )
        rows = read_manifest(root, [old, new])
        assert rows == [("A", 2, None), ("B", 3, None), ("C", 1, "north")]
        assert [(key, count) for key, count, _ in rows] == [("A", 2), ("B", 3), ("C", 1)]
        return {
            "union_by_name": rows,
            "old_projection_total": 6,
            "missing_is_not_invented_region": True,
        }


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        old = write_file(root, "old", pa.table({"delivery_id": ["A"], "packages": [2]}))
        failures = []
        try:
            read_manifest(root, [old], require_region=True)
        except ValueError:
            failures.append("required-region-missing")
        wrong = write_file(root, "wrong", pa.table({"delivery_id": ["B"], "packages": [3.5]}))
        try:
            read_manifest(root, [old, wrong])
        except ValueError:
            failures.append("numeric-type-drift")
        (root / old["file"]).write_bytes(b"corrupted")
        try:
            read_manifest(root, [old])
        except ValueError:
            failures.append("digest-mismatch")
        assert failures == ["required-region-missing", "numeric-type-drift", "digest-mismatch"]
        return {"rejected_changes": failures, "schema_union_is_not_semantic_approval": True}


def main():
    print("Actual mixed-version columnar reads:", example_one())
    print("Compatibility and integrity boundaries:", example_two())


if __name__ == "__main__":
    main()
