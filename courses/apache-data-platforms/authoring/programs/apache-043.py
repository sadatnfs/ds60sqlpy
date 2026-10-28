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
    original_files = {path for path in (root / "warehouse").rglob("*") if path.is_file()}
    table.delete("id = 1")
    current = table.current_snapshot().snapshot_id
    assert current != first
    assert sorted(table.scan().to_arrow()["id"].to_pylist()) == [2, 3]
    assert sum(table.scan().to_arrow()["amount"].to_pylist()) == 16
    assert table.scan(snapshot_id=first).to_arrow().num_rows == 3
    before = {path for path in (root / "warehouse").rglob("*") if path.is_file()}
    table.maintenance.expire_snapshots().by_id(first).commit()
    retained = {snapshot.snapshot_id for snapshot in table.snapshots()}
    assert first not in retained and current in retained
    assert sorted(table.scan().to_arrow()["id"].to_pylist()) == [2, 3]
    assert all(path.is_file() for path in original_files | before)
    print("Current IDs:[2,3]; first snapshot expired; existing file bytes retained.")
    print("This did not run physical orphan cleanup or prove erasure.")
