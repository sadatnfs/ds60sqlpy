import tempfile
from pathlib import Path

import pyarrow as pa
from pyiceberg.catalog import load_catalog

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    catalog = load_catalog(
        "lesson",
        type="sql",
        uri="sqlite:///" + str(root / "catalog.db"),
        warehouse=(root / "warehouse").as_uri(),
    )
    catalog.create_namespace("demo")
    data = pa.table({"id": [1, 2, 3], "region": ["east", "west", "east"], "amount": [4, 9, 7]})
    table = catalog.create_table("demo.orders", schema=data.schema)
    table.append(data)

    first = table.current_snapshot().snapshot_id
    old = sorted(table.scan(snapshot_id=first).to_arrow().to_pylist(), key=lambda row: row["id"])
    assert old == data.to_pylist() and sum(row["amount"] for row in old) == 20
    tasks = list(table.scan().plan_files())
    assert tasks and all(
        Path(task.file.file_path.removeprefix("file://")).is_file() for task in tasks
    )
    table.append(pa.table({"id": [4], "region": ["west"], "amount": [2]}))
    second = table.current_snapshot().snapshot_id
    assert first != second
    assert table.scan().to_arrow().num_rows == 4
    assert table.scan(snapshot_id=first).to_arrow().num_rows == 3
    reopened = load_catalog(
        "lesson",
        type="sql",
        uri="sqlite:///" + str(root / "catalog.db"),
        warehouse=(root / "warehouse").as_uri(),
    ).load_table("demo.orders")
    assert reopened.current_snapshot().snapshot_id == second
    assert sum(reopened.scan().to_arrow()["amount"].to_pylist()) == 22
    print("First snapshot rows:3 total:20; current rows:4 total:22")
    print("Actual snapshot identifiers:", first, second)
