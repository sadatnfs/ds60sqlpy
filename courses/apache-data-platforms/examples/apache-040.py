import tempfile
from pathlib import Path

import pyarrow as pa
from pyiceberg.catalog import load_catalog
from pyiceberg.types import LongType

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

    field_id = table.schema().find_field("amount").field_id
    paths = {task.file.file_path for task in table.scan().plan_files()}
    with table.update_schema() as update:
        update.rename_column("amount", "revenue")
    assert table.schema().find_field("revenue").field_id == field_id
    assert {task.file.file_path for task in table.scan().plan_files()} == paths
    assert sum(table.scan().to_arrow()["revenue"].to_pylist()) == 20
    with table.update_schema() as update:
        update.add_column("quality", LongType())
    table.append(pa.table({"id": [4], "region": ["west"], "revenue": [2], "quality": [1]}))
    rows = sorted(table.scan().to_arrow().to_pylist(), key=lambda row: row["id"])
    assert [row["quality"] for row in rows] == [None, None, None, 1]
    try:
        with table.update_schema() as update:
            update.add_column("required_new", LongType(), required=True)
    except ValueError as error:
        print("Required addition rejected:", str(error))
    else:
        raise AssertionError("Invalid required evolution accepted")
    assert "required_new" not in table.schema().column_names
    assert table.scan().to_arrow().num_rows == 4
    print("Retained field ID:", field_id, "quality values:", [row["quality"] for row in rows])
