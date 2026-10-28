"""Create exactly one explicit Parquet fixture; never repair changed state."""

import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

rows = [
    {"id": 1, "region": "east", "amount": 4},
    {"id": 2, "region": "west", "amount": 9},
    {"id": 3, "region": "east", "amount": 7},
]
path = Path("/warehouse/orders/day=2026-01-01/orders.parquet")
if path.exists():
    if path.is_symlink() or pq.read_table(path, partitioning=None).to_pylist() != rows:
        raise ValueError("Retained warehouse differs; no overwrite occurred")
else:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        pa.Table.from_pylist(
            rows,
            schema=pa.schema([("id", pa.int32()), ("region", pa.string()), ("amount", pa.int32())]),
        ),
        path,
    )
print(json.dumps({"rows": 3, "parquet_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}))
