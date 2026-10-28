import tempfile
from pathlib import Path

import pyarrow as pa
from pyiceberg.catalog import load_catalog
from pyiceberg.exceptions import CommitFailedException
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

    stale = catalog.load_table("demo.orders")
    with table.update_schema() as update:
        update.add_column("note", LongType())
    try:
        with stale.update_schema() as update:
            update.add_column("stale_field", LongType())
    except CommitFailedException as error:
        print("Actual stale commit rejected:", type(error).__name__)
    else:
        raise AssertionError("Stale schema commit accepted")
    current = catalog.load_table("demo.orders")
    assert "note" in current.schema().column_names
    assert "stale_field" not in current.schema().column_names
    with current.update_schema() as update:
        update.add_column("reviewed", LongType())
    final = catalog.load_table("demo.orders")
    assert {"note", "reviewed"} <= set(final.schema().column_names)
    ids = [field.field_id for field in final.schema().fields]
    assert len(ids) == len(set(ids))
    assert sorted(final.scan().to_arrow()["id"].to_pylist()) == [1, 2, 3]
    print("Reloaded and revalidated schema:", final.schema().column_names)
