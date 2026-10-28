# apache-044: Catalogs and cross-engine reads

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-039`, `apache-015`, `apache-042`.

## A catalog protocol and a query engine are separate choices

A catalog tells a client how to find and commit table metadata. A query engine
plans and executes operations over data. Supporting the same file format does
not imply two engines support the same catalog protocol, table version, delete
mode or schema evolution. A compatible integration must establish each boundary
explicitly. The phrase cross-engine read is a claim about a tested path, not an
automatic consequence of using open formats.

This chapter uses a real local PyIceberg SQL catalog to select a committed
snapshot, materializes its bounded scan as Arrow, and registers that Arrow table
in actual DataFusion. DataFusion executes the aggregation. It does not directly
consult the SQLite catalog, write an Iceberg commit or provide a Hive Metastore
client in this example. The Arrow bridge is an explicit materialization boundary
with its own memory and snapshot timing.

A direct Iceberg table provider can potentially push planning and filtering closer
to storage, but it needs its own prepared connector and compatibility checks.
The existence of such an integration upstream is not evidence that this classroom
profile contains it. The separate Hive workshop studies the real Metastore path;
this local example establishes the narrower engine boundary that is actually
prepared and reproducible offline.

## Worked case A: query one committed snapshot through Arrow

The program appends three orders, captures the real snapshot identifier and reads
that exact snapshot into Arrow. It registers the result as orders in a fresh
DataFusion session. The grouped query returns east total 11 and west total 9,
with deterministic ordering. A separate Python sum over the fixture supplies the
expected result rather than asking the same query to verify itself.

The response records the selected snapshot identifier beside the query result.
That identifies the table state that was materialized. The DataFusion relation is
an in-memory view of that specific scan; it does not automatically follow the
catalog's next commit. Treating it as a live table could produce stale application
results even though the engine executes correctly.

The fixture is small enough to collect safely. On a large table, materializing
every row in one process can eliminate the benefit of a scalable storage layout.
A direct provider or bounded scan would need explicit capability, memory and
predicate checks. A successful three-row bridge is not a general recommendation
to collect every production dataset into Python first.

## Worked case B: a new append does not mutate the old relation

A second append adds a west order with amount 2. The original registered relation
still returns west total 9, while a newly scanned and registered relation returns
11. Both are correct for their selected states. The program checks the old and
new snapshots and aggregates separately, making the refresh boundary observable.

The same SQL text can therefore produce different answers after an explicit
refresh. A reproducible analytics or training pipeline must record whether it
uses a fixed snapshot or the current table. Merely saving the table name is not
enough when it is mutable. Conversely, refreshing an existing engine relation
without recording its new source identity can make a report difficult to audit.

The program also attempts to load the table using a different logical SQL catalog
name against the same SQLite file. The real catalog correctly reports no such
table. This demonstrates why connection strings and storage paths alone do not
fully specify catalog identity. Do not recover by creating an empty replacement
under the new name; first compare the intended catalog and namespace.

## Diagnosis and interview discussion

Record engine version, reader/writer library version, catalog type and identity,
warehouse location, selected snapshot, schema and materialization boundary.
Check unsupported operations before migration rather than relying on a successful
simple select. Delete files, partition evolution and concurrency can reveal
compatibility limits that a primitive three-column scan does not exercise.

**Interview discussion: does DataFusion reading an Arrow table prove direct
Iceberg catalog integration?** No. This path uses PyIceberg for catalog and scan,
then DataFusion for execution over materialized Arrow. The two cases show an
actual useful cross-library workflow while preserving the distinction between a
bridge, a direct connector and a remote catalog protocol.

## Complete worked source

This is a complete editable worked program for the declared prepared runtime. It uses bounded local fixtures and does not install packages or start distributed services.

```python
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
```

## Primary references

- [PyIceberg query integration](https://py.iceberg.apache.org/api/#query-the-data)
- [DataFusion Arrow I/O](https://datafusion.apache.org/python/user-guide/io/arrow.html)
- [Iceberg catalog concepts](https://iceberg.apache.org/docs/latest/)
