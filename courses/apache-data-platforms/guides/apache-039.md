# apache-039: Snapshots and the table abstraction

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-003`, `apache-013`.

## Key terms

- **Iceberg table:** A table defined by metadata files that record its schema, partition spec and snapshots, rather than by whichever Parquet files happen to sit in a directory.
- **Snapshot:** A committed table state that references the data files it contains. Immutable data files are reused across snapshots, so a snapshot is not a full copy.
- **Manifest list:** The file a snapshot points to that lists its manifests. Each manifest in turn lists data or delete files with partition values and statistics.
- **Catalog pointer:** The catalog's record of a table's current metadata file. Moving it is the commit that makes a new snapshot current.
- **Warehouse:** The storage location holding a table's data and metadata files, distinct from the catalog that points to the current metadata.

## A table is a committed view of files

A directory of Parquet objects does not by itself say which files form a table,
which schema applies, or which concurrent update won. Iceberg adds metadata that
identifies table state and the data files belonging to each snapshot. A catalog
locates the current table metadata and supplies the commit boundary used by its
writers. The warehouse contains data and metadata files; the catalog's pointer
and the warehouse's bytes are related but different responsibilities.

A snapshot is a committed table state, not a full byte-for-byte copy of every
file. Immutable data files can be reused across snapshots. Snapshot metadata
references manifest lists and manifests, which describe data and delete files
and statistics. This indirection supports evolution and planning, but also means
that deleting an apparently old file by hand can break a still-retained snapshot.
Always use the table's supported maintenance mechanisms and retention policy.

The complete program uses real PyIceberg with a local SQLite catalog and a
temporary warehouse. It performs actual file writes and catalog commits. This
single-process fixture does not stand in for a remote Hive Metastore, REST
catalog, distributed lock service or cloud object store. Those components have
additional configuration and failure boundaries studied in the project workshops.

## Worked case A: create, append and inspect

The first append commits three orders with amounts 4, 9 and 7. The program records
the current snapshot identifier and checks exact order identities plus total 20.
A snapshot identifier is an opaque table identity, not an increasing row count
or a timestamp that should be invented by a caller. Capture the actual identifier
returned by the table after commit.

The fixture inspects planned files and verifies that each referenced data file
exists. That connects logical table state to physical storage without assuming
that every object beneath the warehouse is live table data. It also checks the
schema and records the catalog type. A visible file alone is insufficient to
claim it was committed; a catalog entry alone is insufficient if the referenced
bytes were lost or became inaccessible.

Appending does not impose row ordering. The program sorts by order ID before
comparison, because a scan may enumerate manifests and files in a different order
from application insertion. An analytical consumer that requires ordering must
request it explicitly after scan. The same principle holds when another engine
reads this table through a compatible integration.

## Worked case B: retain the first snapshot after another append

A second append adds order 4 with amount 2. The current state now has four orders
and total 22. Reading with the recorded first snapshot still returns three orders
and total 20. The program asserts both results independently. This is real local
time travel over retained metadata and files, not a copied Python list presented
as an Iceberg history mechanism.

Reopening the same named catalog and table establishes that the committed pointer survives
the original table handle. It does not prove the state survives deletion of the
SQLite database or warehouse. The SQL catalog name is also part of its identity: using a different name in the
same SQLite database selects a different logical catalog, rather than an alias.
Both database and warehouse must be retained together in a persistent
project. Copying only the source code to another machine does not migrate its
catalog or data volume.

Snapshot selection must be captured in a report or training-data receipt if exact
reproduction matters. A query against the current table can change after another
append, even though its SQL is identical. Conversely, a retained snapshot is not
a promise of indefinite retention: an authorized expiration policy can later
remove its reference and permit physical cleanup.

## Diagnosis and interview discussion

Check table identity, catalog configuration, metadata location, current snapshot
and storage accessibility separately. A file-not-found error can mean missing
warehouse bytes rather than a corrupt SQL query. A table-not-found error can mean
the client is connected to the wrong catalog, even if similarly named files exist.
Do not repair either by automatically creating a new empty table over the path.

**Interview discussion: why use Iceberg if Parquet already stores typed columns?**
Parquet describes a file. Iceberg describes a versioned table made of files,
including commits, schema identity, partition specifications and retained history.
These cases show the actual extra contract: one current committed view and an
independently selectable earlier snapshot, both pointing to real local files.

## Worked examples

### List the files a scan will read

```python fragment
for task in table.scan().plan_files():
    print(task.file.file_path, task.file.record_count, task.file.file_format)
```

Run after the first append in the lesson program, this prints one line per data file: a file URI under the warehouse data directory, a record count of 3, and the format PARQUET. The planner gets this list from the manifests of the current snapshot, not by listing the directory. Sum the record counts and compare with the scan row count; a mismatch usually means delete files are being applied, which the record count of a data file alone does not show.

### Reopen the catalog and read by snapshot

```python fragment
reopened = load_catalog(
    "lesson",
    type="sql",
    uri="sqlite:///" + str(root / "catalog.db"),
    warehouse=(root / "warehouse").as_uri(),
)
orders = reopened.load_table("demo.orders")
print(len(orders.snapshots()), orders.scan(snapshot_id=first).to_arrow().num_rows)
```

After two appends, a fresh catalog object should report two snapshots and three rows for the first one, proving the history lives in the SQLite catalog and the metadata files rather than in Python memory. If the reopened catalog cannot find the table, compare the uri and warehouse values with the writer; a different SQLite path creates a new empty catalog without any error.

## Complete worked source

Run it as the [worked program rules](../STUDY-GUIDE.md#worked-programs) describe.

```python
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
```

## Primary references

- [PyIceberg table API](https://py.iceberg.apache.org/api/)
- [Iceberg table specification](https://iceberg.apache.org/spec/)
