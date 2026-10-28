"""One immutable, source-bound synthetic Parquet fixture."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path("/state")
ROWS = [
    {"id": i, "region": "east" if i % 2 == 0 else "west", "amount": i % 17 + 1} for i in range(200)
]
LOGICAL_SHA = hashlib.sha256(
    json.dumps(ROWS, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()


def read() -> pa.Table:
    data, manifest = ROOT / "orders.parquet", ROOT / "manifest.json"
    if any(path.is_symlink() or not path.is_file() for path in (data, manifest)):
        raise ValueError("Expected regular canonical data and manifest")
    if data.stat().st_size > 100_000 or manifest.stat().st_size > 4096:
        raise ValueError("Fixture bounds exceeded")
    metadata = json.loads(manifest.read_text())
    if metadata != {
        "schema_version": 1,
        "logical_sha256": LOGICAL_SHA,
        "file_sha256": hashlib.sha256(data.read_bytes()).hexdigest(),
    }:
        raise ValueError("Fixture identity differs; no reset performed")
    parquet = pq.ParquetFile(data)
    if parquet.metadata.num_rows != 200 or parquet.metadata.num_columns != 3:
        raise ValueError("Fixture must contain exactly 200 rows and three columns")
    if (
        parquet.metadata.num_row_groups > 4
        or sum(
            parquet.metadata.row_group(index).total_byte_size
            for index in range(parquet.metadata.num_row_groups)
        )
        > 1_048_576
    ):
        raise ValueError("Decoded fixture exceeds its metadata budget")
    if not parquet.schema_arrow.equals(pa.Table.from_pylist(ROWS).schema):
        raise ValueError("Fixture schema differs")
    table = parquet.read()
    if table.to_pylist() != ROWS:
        raise ValueError("Fixture values differ")
    return table


def initialize() -> None:
    ROOT.mkdir(exist_ok=True)
    if (ROOT / "orders.parquet").exists() or (ROOT / "manifest.json").exists():
        read()
        print("Existing immutable fixture verified")
        return
    pq.write_table(pa.Table.from_pylist(ROWS), ROOT / "orders.parquet", row_group_size=50)
    (ROOT / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "logical_sha256": LOGICAL_SHA,
                "file_sha256": hashlib.sha256((ROOT / "orders.parquet").read_bytes()).hexdigest(),
            }
        )
        + "\n"
    )
    (ROOT / "receipts").mkdir(mode=0o700)
    for path in [ROOT, *ROOT.iterdir()]:
        if path.is_symlink():
            raise ValueError("Unexpected symbolic link")
        path.chmod(0o700 if path.is_dir() else 0o600)
        if os.geteuid() == 0:
            os.chown(path, 1000, 1000)
    print("Created fixed 200-order fixture")


if __name__ == "__main__":
    initialize()
