# apache-081: Batch lakehouse with reproducible snapshots

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-020`, `apache-044`.

## Key terms

- **Batch lakehouse:** A path combining Parquet files, an Iceberg table commit and a query engine to publish a reproducible batch result.
- **Snapshot identifier:** The Iceberg snapshot ID that fixes exactly which data files a batch result read.
- **Source identity:** The recorded fixture, schema, catalog and table identities that bind a result to its exact inputs.
- **Arrow bridge:** Materializing a selected snapshot as an Arrow table for DataFusion. It does not prove that a direct Spark or Iceberg connector ran.
- **Identity dossier:** The receipt pairing source, snapshot, reader versions and exact result so another contributor can reproduce and check the batch.

## A reproducible batch product names its inputs and commit

A batch lakehouse path can combine Arrow interchange, an Iceberg table and a
query engine. Each component has a different responsibility: Arrow represents
in-memory data, Parquet stores columnar files, Iceberg identifies committed table
state, and DataFusion executes a supported query. A catalog locates and commits
metadata; it does not automatically make every engine a compatible table reader.

The bounded integration source uses actual PyIceberg with a local SQL catalog,
materializes one selected snapshot as Arrow and executes actual DataFusion SQL.
This is the same explicit library boundary taught earlier, now packaged with a
source/result identity dossier. A separately prepared Spark read is an extension
requiring compatible catalog and storage access; the Arrow bridge does not prove
that a direct Spark/Iceberg connector ran.

A useful receipt identifies source fixture, schema, catalog, table, snapshot,
reader versions and exact result. Hashes help bind bytes, but they do not prove
the program was correct or the input complete. Independent expected identities
and changed-condition behavior remain necessary even when every file is
content-addressed.

## Worked case A: publish one finite event batch

The batch source contains three orders with IDs 1/2/3 and amounts 4/9/7. Create one
owned temporary catalog/table, append the actual Arrow batch and record the
selected Iceberg snapshot. Scan that snapshot to Arrow and register it in a fresh
DataFusion session. Require exact rows and regional totals east 11 and west 9.

The independent oracle comes from the input contract, not a second copy of the
same SQL. Save a deterministic logical digest of the primitive rows beside the
actual snapshot ID. Physical Parquet hashes can change with encoding or library
versions while the logical table remains equivalent, so record which identity
each digest represents.

The catalog database and warehouse are distinct state. A path to Parquet files
is not enough to reconstruct which files formed the committed table. Preserve
metadata and snapshot references while the result is needed. A real recurring
publication also needs an atomic consumer pointer and explicit handling of
concurrent writers rather than a directory overwrite.

## Worked case B: a correction creates a new observation boundary

Append a fourth west order with amount 2 and capture the new snapshot. The old
version-pinned scan remains three rows and west 9; the new scan contains four rows
and west 11. The previously registered DataFusion Arrow relation remains bound
to its materialized state until explicitly refreshed. Require all three
observations rather than expecting the engine to follow the catalog automatically.

For a prepared Spark comparison, point a compatible actual connector at the same
intended catalog/table/snapshot and compare exact identities and types. If Spark
instead reads an exported Parquet snapshot, describe that export boundary
explicitly. Equal results through an export do not prove direct shared-catalog
interoperability.

A schema change adds another condition to reproducibility. Compare stable field
identity and supported logical types, not only display names. A reader returning
plausible coerced values can violate money or timestamp semantics. Negative
schema and unsupported-feature checks should therefore accompany a useful
cross-engine acceptance suite.

## Diagnosis and interview discussion

Separate acquisition completeness, table commit, materialization, query execution
and artifact publication. Preserve the selected snapshot when investigating a
changed result; rerunning against current state can erase the comparison. An
old successful receipt remains evidence for its exact source/runtime state,
not automatic qualification for a changed connector.

**Interview discussion: what makes a batch result reproducible beyond saving SQL?**
A defined input/schema/catalog/snapshot contract, compatible reader versions and
independent result identity. The two cases bind one committed batch and then
show exactly which refresh changes the answer, while keeping the prepared
Spark connector claim separate.

## Worked examples

### Run the batch into a new output directory

```bash
cd work/integration
bash run.sh batch batch-1
cat .workshop/batch-1/receipt.json
```

run.sh refuses an output name that already exists, so each run leaves a separate receipt. The receipt lists two snapshot IDs, the original totals east 11 and west 9, and current totals east 11 and west 11 after the correction row. A second run must use batch-2; reusing a name would overwrite evidence that a reviewer may still need.

### A content digest for the declared input

```python
import hashlib
import json

rows = [
    {"id": 1, "region": "east", "amount": 4},
    {"id": 2, "region": "west", "amount": 9},
    {"id": 3, "region": "east", "amount": 7},
]
encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
print(hashlib.sha256(encoded).hexdigest()[:16])
```

```text
fe0fffef33dcfb0d
```

This mirrors logical_digest in batch_snapshot.py. Sorting keys and fixing separators makes the digest depend on values, not on formatting, so two runs over the same logical input agree even if the file layout differs. If a later batch reports a different source digest while claiming the same input, someone changed the data and the comparison between runs is invalid.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Integration apache-081 complete worked notebook

Run the actual bounded PyIceberg/Arrow/DataFusion program in the prepared Python profile. Retain old/new snapshot and materialization identities. A Spark read is a separately prepared connector/export path.

## What this batch receipt must hold

- The two Iceberg snapshot IDs, in commit order, from the local SQL catalog.
- The Arrow schema string that DataFusion registered, including the integer amount type.
- Original rows 1/2/3 and current rows 1/2/3/4, saved as primitive values.
- Original totals east 11 and west 9, and current totals east 11 and west 11.
- A fresh catalog readback and the rejected wrong logical catalog name.
- An explicit false for direct Spark or Iceberg/DataFusion connector acceptance.

The receipt is a dossier only when those fields agree with each other. If the
second snapshot ID equals the first, the correction never committed and the
west 11 total came from somewhere else. If the pinned scan returns four rows,
the program read current state instead of the selected snapshot. The
[shared receipt rules](../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
mkdir -p .workshop
# From the copied integration project; use the complete Docker command in README.
cat batch_snapshot.py
cat README.md
```

In `batch_snapshot.py`, find `BASE_ROWS` and `EXTRA` first; they are the whole
input contract. Then find where `expected_old` is written by hand rather than
computed by the same query. That separation is what makes the regional totals an
independent check. `run.sh batch batch-1` refuses an existing output directory,
so a second experiment needs a new name such as `batch-2`.

## Primary references

- [Iceberg snapshot commits and isolation](https://iceberg.apache.org/docs/latest/reliability/)
- [PyIceberg scans to Arrow](https://py.iceberg.apache.org/api/#query-the-data)
- [DataFusion registration of Arrow tables](https://datafusion.apache.org/python/user-guide/io/arrow.html)
- [Arrow columnar types for the materialized batch](https://arrow.apache.org/docs/format/Columnar.html)
