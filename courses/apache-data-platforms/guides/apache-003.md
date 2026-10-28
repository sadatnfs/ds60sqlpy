# apache-003: Files, objects and tables

Tutorial mode. Stage: beginner. Direct prerequisites: `apache-002`.

## A file is not automatically a committed table

A Parquet file stores rows in a documented physical format. A directory can hold
many such files. A table adds a logical identity and rules describing which files
belong to a consistent version. Without those rules, listing a directory while a
writer is changing it can produce an incomplete or mixed collection. The term
'lakehouse' does not itself specify a transaction protocol; the actual format and
catalog implementation do.

Iceberg models table versions with metadata, snapshots and manifests that refer
to data files. A catalog maintains the current metadata location for a table.
A successful commit changes the table's visible version according to that
catalog's concurrency contract. Readers use a selected snapshot rather than
assuming every file currently visible in a directory is part of the table.

This chapter uses the real PyIceberg library with its local SQL catalog backed by
SQLite. It creates all data beneath one temporary directory and performs actual
commits. SQLite is chosen to keep the example offline and inspectable. It is not
presented as a scalable shared catalog or a substitute for the later Metastore
workshop. The API and snapshot behavior are real; the operational scope is local.

## Worked case A: two appends create two different views

The first case creates a namespace and a typed table, then appends two orders.
It retains the resulting snapshot ID before appending a third order. The current
scan now returns three rows, while a scan using the retained snapshot returns
the original two. Both answers are correct because they refer to different
versions of the same table.

The test checks exact record identities, not merely row counts. Two snapshots
could each contain two rows but different records. It also checks that snapshot
IDs differ without assuming they are consecutive integers or timestamps. An ID
is a version reference whose interpretation belongs to the format; a learner
should not derive ordering by arithmetic on an opaque identifier.

A published analysis can record the snapshot ID together with the query and code
revision. That makes its data selection more explicit than saying 'the latest
orders table'. Reproducibility still depends on retaining the referenced files
and metadata. Expiring old snapshots or deleting their files can remove the
ability to reproduce an old result, so retention is part of the publication
contract rather than an unrelated storage-cleanup choice.

## Worked case B: a file in the warehouse is not necessarily table data

The second case writes a separate Parquet file under the warehouse path without
committing it through the table. A directory scan of that standalone file can
read its row, but the Iceberg table scan remains unchanged. The catalog and
snapshot metadata never admitted that file into the table's current version.
The test therefore distinguishes physical existence from logical membership.

This is useful during failure analysis. A failed writer may leave an unreferenced
file after creating bytes but before completing the metadata commit. That file
is not evidence that the table transaction succeeded. Conversely, deleting an
apparently old file just because its modification time is old can corrupt a
still-retained snapshot. Cleanup must understand references and retention rather
than guessing from a directory listing.

For a selected snapshot \(s\), the visible relation can be described as
\(T_s=\bigcup_{f\in F_s}\operatorname{rows}(f)\), with any format-defined
delete semantics applied. The important object is the snapshot's selected file
set \(F_s\), not every file in the warehouse. Later Iceberg chapters refine
this model with field IDs, partition evolution, deletes and optimistic commits.

## Mistakes and diagnosis

Do not describe two separate appends as one transaction if the API committed them
separately. Do not call a table scan 'time travel' unless it actually selects a
retained version. Do not count a file upload as a successful table publication.
When a consumer sees an unexpected result, record the catalog name, namespace,
table identifier and snapshot before inspecting lower-level files.

**Interview discussion: what does a table format add beyond Parquet?** Parquet
provides file structure and columnar storage capabilities. A table format defines
metadata and operations for selecting and evolving a collection of files as a
logical table. The catalog connects a table identity to its current metadata.
The exact guarantees depend on the chosen format, catalog and engine versions.
This worked example verifies real local snapshot selection and membership, while
leaving shared-service availability and cross-engine compatibility to their own
explicit workshops.

## Complete worked source

This is a complete editable worked program for the declared prepared runtime. It uses bounded local fixtures and does not install packages or start distributed services.

```python
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
```

## Primary references

- [PyIceberg local catalog and writes](https://py.iceberg.apache.org/)
- [Iceberg specification](https://iceberg.apache.org/spec/)
