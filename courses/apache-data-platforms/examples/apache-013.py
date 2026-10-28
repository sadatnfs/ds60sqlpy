import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.dataset as ds

records = [
    {"id": 1, "region": "east", "amount": 4},
    {"id": 2, "region": "west", "amount": 30},
    {"id": 3, "region": "east", "amount": 17},
    {"id": 4, "region": "west", "amount": 2},
]
table = pa.Table.from_pylist(records)
partitioning = ds.partitioning(pa.schema([("region", pa.string())]), flavor="hive")
with tempfile.TemporaryDirectory(prefix="arrow-dataset-") as temporary:
    path = Path(temporary) / "events"
    ds.write_dataset(table, path, format="parquet", partitioning=partitioning)
    dataset = ds.dataset(path, format="parquet", partitioning=partitioning)
    east = ds.field("region") == "east"
    assert len(list(dataset.get_fragments())) == 2
    assert len(list(dataset.get_fragments(filter=east))) == 1
    selected = dataset.to_table(columns=["id", "amount"], filter=east).sort_by("id")
    assert selected.column_names == ["id", "amount"]
    assert selected.to_pylist() == [{"id": 1, "amount": 4}, {"id": 3, "amount": 17}]
    predicate = east & (ds.field("amount") > 10)
    actual = dataset.to_table(columns=["id", "amount"], filter=predicate).sort_by("id").to_pylist()
    expected = [
        {"id": r["id"], "amount": r["amount"]}
        for r in records
        if r["region"] == "east" and r["amount"] > 10
    ]
    assert actual == expected == [{"id": 3, "amount": 17}]
    assert len(list(dataset.get_fragments(filter=predicate))) == 1
    print("All fragments:", 2, "east candidates:", 1)
    print("East projection:", selected.to_pylist())
    print("Residual filter result:", actual)
