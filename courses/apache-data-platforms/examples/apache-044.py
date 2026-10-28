import tempfile
from pathlib import Path

import pyarrow as pa
from datafusion import SessionContext
from pyiceberg.catalog import load_catalog
from pyiceberg.exceptions import NoSuchTableError

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    settings = {
        "type": "sql",
        "uri": "sqlite:///" + str(root / "catalog.db"),
        "warehouse": (root / "warehouse").as_uri(),
    }
    catalog = load_catalog("lesson", **settings)
    catalog.create_namespace("demo")
    data = pa.table({"id": [1, 2, 3], "region": ["east", "west", "east"], "amount": [4, 9, 7]})
    table = catalog.create_table("demo.orders", schema=data.schema)
    table.append(data)
    first = table.current_snapshot().snapshot_id
    ctx = SessionContext()
    ctx.register_record_batches("original", [table.scan(snapshot_id=first).to_arrow().to_batches()])

    def totals(name):
        assert name in {"original", "refreshed"}
        return (
            ctx.sql(
                f"SELECT region,SUM(amount) AS total FROM {name} GROUP BY region ORDER BY region"
            )
            .to_arrow_table()
            .to_pylist()
        )

    expected = [{"region": "east", "total": 11}, {"region": "west", "total": 9}]
    assert totals("original") == expected
    table.append(pa.table({"id": [4], "region": ["west"], "amount": [2]}))
    second = table.current_snapshot().snapshot_id
    ctx.register_record_batches(
        "refreshed", [table.scan(snapshot_id=second).to_arrow().to_batches()]
    )
    assert totals("original") == expected
    assert totals("refreshed") == [{"region": "east", "total": 11}, {"region": "west", "total": 11}]
    try:
        load_catalog("different-logical-catalog", **settings).load_table("demo.orders")
    except NoSuchTableError:
        print("Different catalog identity rejected without creating a replacement")
    else:
        raise AssertionError("Unexpected catalog alias")
    print("Snapshot-bound Arrow bridge:", first, second, totals("original"), totals("refreshed"))
