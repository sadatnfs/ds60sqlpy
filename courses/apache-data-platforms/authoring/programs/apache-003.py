import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from pyiceberg.catalog import load_catalog

schema = pa.schema([("id", pa.int64()), ("amount", pa.int64())])
with tempfile.TemporaryDirectory(prefix="table-snapshots-") as temporary:
    root = Path(temporary)
    warehouse = root / "warehouse"
    catalog = load_catalog(
        "lesson",
        type="sql",
        uri="sqlite:///" + str(root / "catalog.db"),
        warehouse=warehouse.as_uri(),
    )
    catalog.create_namespace("learning")
    table = catalog.create_table("learning.orders", schema=schema)
    first = pa.Table.from_pylist([{"id": 1, "amount": 4}, {"id": 2, "amount": 9}], schema=schema)
    table.append(first)
    initial = table.current_snapshot()
    assert initial is not None
    table.append(pa.Table.from_pylist([{"id": 3, "amount": 7}], schema=schema))
    current = table.current_snapshot()
    assert current is not None and current.snapshot_id != initial.snapshot_id
    old_rows = sorted(
        table.scan(snapshot_id=initial.snapshot_id).to_arrow().to_pylist(),
        key=lambda row: row["id"],
    )
    now_rows = sorted(table.scan().to_arrow().to_pylist(), key=lambda row: row["id"])
    assert old_rows == [{"id": 1, "amount": 4}, {"id": 2, "amount": 9}]
    assert now_rows == old_rows + [{"id": 3, "amount": 7}]
    orphan = warehouse / "uncommitted.parquet"
    pq.write_table(pa.Table.from_pylist([{"id": 99, "amount": 1000}], schema=schema), orphan)
    assert pq.read_table(orphan).to_pylist() == [{"id": 99, "amount": 1000}]
    assert sorted(table.scan().to_arrow().to_pylist(), key=lambda row: row["id"]) == now_rows
    print("Retained snapshot:", old_rows)
    print("Current snapshot:", now_rows)
    print("Uncommitted file is readable but absent from the table")
