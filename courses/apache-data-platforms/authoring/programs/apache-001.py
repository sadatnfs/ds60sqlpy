import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.ipc as ipc
import pyarrow.parquet as pq
from datafusion import SessionConfig, SessionContext

records = [
    {"id": 1, "region": "east", "amount_minor": 400, "paid": True},
    {"id": 2, "region": "west", "amount_minor": 900, "paid": False},
    {"id": 3, "region": "east", "amount_minor": 700, "paid": True},
]
schema = pa.schema(
    [
        ("id", pa.int64()),
        ("region", pa.string()),
        ("amount_minor", pa.int64()),
        ("paid", pa.bool_()),
    ]
)
table = pa.Table.from_pylist(records, schema=schema)
sink = pa.BufferOutputStream()
with ipc.new_stream(sink, schema) as writer:
    writer.write_table(table)
restored = ipc.open_stream(sink.getvalue()).read_all()
assert restored.equals(table)
with tempfile.TemporaryDirectory(prefix="platform-contract-") as temporary:
    path = Path(temporary) / "orders.parquet"
    pq.write_table(restored, path)
    context = SessionContext(SessionConfig().with_target_partitions(2))
    context.register_parquet("orders", str(path))
    paid = (
        context.sql(
            "SELECT region, SUM(amount_minor) AS total, COUNT(*) AS orders "
            "FROM orders WHERE paid GROUP BY region ORDER BY region"
        )
        .to_arrow_table()
        .to_pylist()
    )
    expected = [
        {
            "region": "east",
            "total": sum(r["amount_minor"] for r in records if r["paid"]),
            "orders": sum(r["paid"] for r in records),
        }
    ]
    assert paid == expected == [{"region": "east", "total": 1100, "orders": 2}]
    unfiltered = (
        context.sql(
            "SELECT region, SUM(amount_minor) AS total FROM orders GROUP BY region ORDER BY region"
        )
        .to_arrow_table()
        .to_pylist()
    )
    assert unfiltered == [{"region": "east", "total": 1100}, {"region": "west", "total": 900}]
    print("Paid population:", paid)
    print("Different question without the filter:", unfiltered)
