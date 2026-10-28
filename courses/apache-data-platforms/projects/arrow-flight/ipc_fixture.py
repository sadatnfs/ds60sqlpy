"""Generate or independently verify the fixed cross-language IPC stream."""

from __future__ import annotations

import sys

import pyarrow as pa
import pyarrow.ipc as ipc

EXPECTED = pa.table(
    {
        "id": pa.array([1, 2, 3], type=pa.int64()),
        "region": ["east", "west", "east"],
        "amount": pa.array([4, None, 7], type=pa.int64()),
    }
)
if sys.argv[1:] == ["write"]:
    with ipc.new_stream(sys.stdout.buffer, EXPECTED.schema) as writer:
        writer.write_table(EXPECTED)
elif sys.argv[1:] == ["read"]:
    with ipc.open_stream(sys.stdin.buffer) as reader:
        batches = []
        for batch in reader:
            batches.append(batch)
            if len(batches) > 3 or sum(value.num_rows for value in batches) > 3:
                raise ValueError("Oversized fixture stream")
        table = pa.Table.from_batches(batches, schema=reader.schema)
    assert table.equals(EXPECTED, check_metadata=True)
    print("Python -> Rust Arrow60 -> Python: exact schema, values and nulls passed")
else:
    raise SystemExit("Use write or read")
