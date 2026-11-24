# apache-042: Concurrency and optimistic commits

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-040`, `apache-006`.

## Key terms

- **Optimistic concurrency:** A commit strategy in which writers prepare updates without locks and the catalog accepts a commit only if the table state they observed is still current.
- **Commit requirement:** A condition sent with an Iceberg commit, such as the expected current snapshot or schema identity, that the catalog checks before swapping metadata.
- **Compare-and-swap:** An atomic update that replaces the current value only if it still equals an expected old value, the model behind a catalog's metadata pointer swap.
- **Commit conflict:** A rejected commit because another writer changed the table first. The client must reload and decide whether its operation is still valid.
- **Ambiguous commit:** A commit whose response was lost, so the client must check whether it succeeded before repeating a business append.

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

## Worked examples

### Reject a commit based on stale metadata

```python
from pyiceberg.exceptions import CommitFailedException
from pyiceberg.types import LongType

stale = catalog.load_table("demo.orders")
with table.update_schema() as update:
    update.add_column("note", LongType())
try:
    with stale.update_schema() as update:
        update.add_column("stale_field", LongType())
except CommitFailedException as error:
    print("rejected:", type(error).__name__)
```

The second writer loaded the table before the note column existed, so its commit asserts a schema that is no longer current, and the SQL catalog refuses the pointer swap. The output names CommitFailedException. Silent success here would mean the catalog accepted a last-writer-wins update and lost note. The same check protects concurrent appends from replacing each other's snapshots.

### Reload, revalidate and retry the intended change

```python
current = catalog.load_table("demo.orders")
names = current.schema().column_names
if "stale_field" not in names:
    with current.update_schema() as update:
        update.add_column("stale_field", LongType())
print(catalog.load_table("demo.orders").schema().column_names)
```

The retry starts from freshly loaded metadata and checks whether its change is still needed before committing, so the final column list contains id, region, amount, note and stale_field. Blindly retrying the old update object would fail again, and retrying a data append without revalidation can double write rows. Decide per operation whether a conflict should retry, merge or stop for a human.

### Inspect the metadata pointer after each commit

```python
print(catalog.load_table("demo.orders").metadata_location)
with current.update_schema() as update:
    update.add_column("reviewed", LongType())
print(catalog.load_table("demo.orders").metadata_location)
```

Each line prints a different metadata JSON path under the table metadata directory, with an incremented version prefix. The SQL catalog row stores only this pointer, so a commit is a compare-and-swap on that row. When diagnosing a conflict, compare the location a writer loaded with the current one; if they differ, the writer was stale.

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
