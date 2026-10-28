# apache-042: Concurrency and optimistic commits

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-040`, `apache-006`.

## A catalog commit must detect competing table state

Two writers can load the same table metadata and prepare different updates.
Without a conflict check, the later writer could replace the pointer and discard
the earlier writer's committed change. Iceberg uses optimistic concurrency: a
writer prepares an update, then commits subject to requirements about the state
it observed. A conflict means the client must reload and decide whether its
operation remains valid, not overwrite the newer metadata blindly.

A simplified compare-and-swap rule is
\(\mathrm{commit}(v_{old},v_{new})\) succeeds only if the catalog's current
version still matches the required old state. Actual Iceberg requirements are
more specific to operations and include schema, snapshot and other identities.
The model explains the reason for the boundary; the executable source uses real
PyIceberg catalog validation rather than implementing a substitute lock manager.

Conflict recovery is different from delivery retry. A client that never received
a commit response must determine whether its previous operation succeeded before
repeating a business append. Reloading the table can reveal new state, but it does
not by itself give every append an application-level idempotency key. Record source
operation identity and reconcile ambiguous outcomes when exact effects matter.

## Worked case A: reject a stale schema update

The program creates two handles to the same table. The first handle commits an
optional note field. The stale handle then tries to add a different field based
on its older schema. The prepared catalog rejects the stale update with an actual
CommitFailedException. The independent readback confirms that note exists and
the stale field does not.

This sequence is deterministic and needs no timing-dependent threads. It models
two clients by retaining separate real table handles, then deliberately orders
the commits. It demonstrates conflict detection, not simultaneous network failure,
distributed consensus or a benchmark of concurrent write throughput. Those claims
would require additional topology and measurements.

The original data remains readable after the rejection. A conflict must not be
handled by deleting the table or recreating its warehouse. Its files are not
corrupt merely because another writer advanced metadata. Diagnose the specific
requirement that failed and compare the intended operation with the new table
state.

## Worked case B: reload and revalidate the intended update

A fresh handle loads the committed note field, then adds reviewed as another
optional field. Both fields are present after this second successful commit.
The program verifies all field identities are unique and the original three
orders remain unchanged. This is a valid retry because the intended addition is
compatible with the newly observed schema.

A rename conflict can require a business decision instead. If another writer
renamed or removed the source field, blindly reapplying a textual operation might
change a different field or fail again. A retry policy must distinguish retryable
transport failures, optimistic conflicts, invalid requests and permanent access
errors. Exponential backoff reduces pressure but cannot decide semantic validity.

For append workflows, a safe recovery design may reuse already-written immutable
files after revalidation rather than rewrite all data. That depends on the actual
operation and writer support. Unreferenced files can remain after failed attempts;
their later cleanup must respect all retained snapshots and in-flight writers.
A conflict error is not permission for broad directory deletion.

## Diagnosis and interview discussion

Log the catalog identity, loaded table version, intended operation and exact
failure category. Keep application operation identifiers separate from snapshot
IDs. Bound retry count and preserve the final unknown outcome for reconciliation.
Never turn every exception into success or catch a conflict and silently drop
one writer's requested change.

**Interview discussion: why choose optimistic concurrency for analytical tables?**
Immutable data preparation can proceed without holding a long exclusive catalog
lock, while a short validated metadata commit resolves competing changes. The
tradeoff is explicit conflict handling and sometimes wasted preparation work.
These cases show both the rejected stale update and a reloaded, revalidated
success without inventing a global lock or claiming every operation is automatically
safe to replay.

## Complete worked source

This is a complete editable worked program for the declared prepared runtime. It uses bounded local fixtures and does not install packages or start distributed services.

```python
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
```

## Primary references

- [Iceberg concurrent commits](https://iceberg.apache.org/docs/latest/reliability/)
- [PyIceberg updates](https://py.iceberg.apache.org/api/)
