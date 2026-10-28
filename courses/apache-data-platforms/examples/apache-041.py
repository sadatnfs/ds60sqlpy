import tempfile
from pathlib import Path

import pyarrow as pa
from pyiceberg.catalog import load_catalog
from pyiceberg.transforms import IdentityTransform

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

    original_spec = table.spec().spec_id
    with table.update_spec() as update:
        update.add_field("region", IdentityTransform(), "region_partition")
    region_spec = table.spec().spec_id
    table.append(pa.table({"id": [4, 5], "region": ["east", "west"], "amount": [3, 8]}))
    selected = table.scan(row_filter="region = 'east'")
    assert sorted(selected.to_arrow()["id"].to_pylist()) == [1, 3, 4]
    planned = list(selected.plan_files())
    assert {task.file.spec_id for task in planned} == {original_spec, region_spec}
    print("East candidate spec IDs:", sorted(task.file.spec_id for task in planned))
    with table.update_spec() as update:
        update.remove_field("region_partition")
        update.add_field("id", IdentityTransform(), "id_partition")
    table.append(pa.table({"id": [6], "region": ["east"], "amount": [5]}))
    assert len(table.specs()) == 3
    ids = sorted(table.scan(row_filter="region = 'east'").to_arrow()["id"].to_pylist())
    assert ids == [1, 3, 4, 6]
    assert table.scan().to_arrow().num_rows == 6
    print("Three historical specifications; logical east IDs:", ids)
