# apache-013: Parquet datasets and predicate pruning

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-012`.

## Key terms

- **Dataset fragment:** One file or file piece of a multi-file Parquet dataset that the scanner can read or skip.
- **Hive-style partitioning:** A directory layout such as region=east that supplies a column value through the path instead of storing it in every row. It is a convention, not evidence of a Hive Metastore registration.
- **Partition pruning:** Skipping whole fragments whose partition values or statistics prove they cannot satisfy the filter.
- **Row-group statistics:** Per-column minimum, maximum and null counts stored in Parquet metadata that let a scanner skip row groups without decoding them.
- **Residual filter:** The part of a predicate that metadata cannot decide, which must still be evaluated against the rows that are read.

## The mechanism

A Parquet dataset can span several files and directories. A dataset scanner
combines a logical schema with file fragments and a requested computation.
Projection names the columns needed in the result. A filter restricts rows.
Partition expressions, file statistics and row-group statistics may permit the
scanner to exclude work, but an exclusion decision must remain compatible with
the query's semantics. A row that could satisfy the filter cannot be discarded
merely because its file's name looks inconvenient.

A Hive-style directory such as `region=east` supplies a partition value through
its path. The physical Parquet file need not repeat that value in every row.
The dataset reader reconstructs the logical column using a declared partition
schema. This is a layout convention, not proof that Apache Hive wrote the files
or that a Hive Metastore contains a table registration for them.

The program creates a bounded synthetic dataset in a temporary directory. It
never downloads a public dataset and removes its own files after the checks.
That keeps the causal question clear: how do projection, partition pruning and
residual filtering affect one known set of records? File-level observations are
reported separately from row-level answers.

## Worked case A: eliminate an impossible partition

The first case writes four records into east and west partition directories.
It opens a dataset with an explicit string partition field and requests only
`id` and `amount` for east. The expected answer is the two east records. The
program also asks the dataset which fragments can match the partition predicate.
There are two fragments in the full dataset and one candidate for east.

That reduction follows from a logical implication: a fragment known to satisfy
`region=west` cannot contain a row satisfying `region=east`. The partition
expression is enough to exclude it. If a dataset has missing or inconsistent
partition metadata, the scanner must be conservative instead of manufacturing
certainty from an incomplete directory listing.

Projection and filtering play different roles. The returned table omits `region`
because the result requests only two columns, yet the scanner still needs the
partition value to evaluate the filter. Seeing no region column in the result
does not mean the filter was ignored. The assertions verify both result schema
and row identity so this distinction is observable.

## Worked case B: retain a fragment but reject some of its rows

The second case adds `amount > 10` to the east predicate. The east fragment
remains a candidate because one of its rows may match. Only the row with amount 17
survives the complete row predicate; the east row with amount 4 does not. The
candidate-fragment count is still one, while the output-row count changes from
two to one. Pruning and residual evaluation therefore answer different questions.

The fixture deliberately contains two distinct amounts inside one partition.
If every partition contained a single uniform value, a mistaken implementation
that returned whole candidate files could look correct. The independent oracle
filters the original Python records and compares exact IDs and amounts with the
Arrow result. It does not simply repeat a scanner call and compare it with itself.

For a simple scan, a rough data-work model is
\[W\approx\sum_{f\in F_{candidate}}\sum_{c\in C_{needed}}B_{fc}+W_{decode}+W_{predicate}.\]
This is a reasoning model, not a timing equation: compression, page reads,
metadata caches, thread scheduling and filesystem behavior affect real cost.
The lesson records candidates and answers, then leaves performance measurement
to a separately controlled workload rather than inferring speed from four rows.

## Mistakes and diagnosis

Do not confuse a partition folder with an atomic table transaction. A reader
listing files while a writer modifies them can observe an inconsistent collection
unless a higher-level table protocol coordinates visibility. Do not conclude
that a filter was fully pushed down merely because a logical plan contains it.
Inspect the appropriate metadata and retain a correctness check for residual
rows. Do not infer a stable row order without an explicit sort; dataset scans
may return fragments in an implementation-dependent order.

## Interview discussion

**Does partition pruning replace filtering?** It excludes fragments whose known
partition conditions contradict the query. Remaining fragments still require
correct evaluation of any unresolved predicate, possibly helped by statistics
or page indexes. Iceberg later adds committed table snapshots and field-aware
metadata to this picture. Parquet files plus a directory convention alone do not
supply those transaction and evolution guarantees.

## Worked examples

### Count fragments pruned by a partition filter

```python
import tempfile

import pyarrow as pa
import pyarrow.dataset as ds

table = pa.table({"id": [1, 2, 3, 4], "region": ["east", "west", "east", "west"]})
part = ds.partitioning(pa.schema([("region", pa.string())]), flavor="hive")
with tempfile.TemporaryDirectory() as root:
    ds.write_dataset(table, root, format="parquet", partitioning=part)
    data = ds.dataset(root, format="parquet", partitioning=part)
    east = ds.field("region") == "east"
    print(len(list(data.get_fragments())), len(list(data.get_fragments(filter=east))))
```

```text
2 1
```

Two fragments exist and only one survives the east filter, so the west directory is never opened. That pruning comes from the directory names alone, before any file footer is read. If the filtered count equals the total, check that the partitioning object passed at read time matches the one used to write; a dataset opened without it sees region only as a path, not as a column.

### Separate fragment pruning from row filtering

```python
import tempfile

import pyarrow as pa
import pyarrow.dataset as ds

table = pa.table({"region": ["east", "east", "west"], "amount": [4, 17, 30]})
part = ds.partitioning(pa.schema([("region", pa.string())]), flavor="hive")
with tempfile.TemporaryDirectory() as root:
    ds.write_dataset(table, root, format="parquet", partitioning=part)
    data = ds.dataset(root, format="parquet", partitioning=part)
    rule = (ds.field("region") == "east") & (ds.field("amount") > 10)
    print(len(list(data.get_fragments(filter=rule))), data.to_table(filter=rule).num_rows)
```

```text
1 1
```

One fragment is kept but only one of its two rows passes, because the amount condition cannot be decided from the directory name. The scanner still has to read the east file and evaluate the predicate row by row. When a query is slower than expected, compare fragments kept with rows returned; many kept fragments and few returned rows suggest the layout does not match the common filter.

## Complete worked source

This is a complete editable worked program for the declared prepared runtime. It uses bounded local fixtures and does not install packages or start distributed services.

```python
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
```

## Primary references

- [Arrow dataset guide](https://arrow.apache.org/docs/python/dataset.html)
- [Arrow Parquet guide](https://arrow.apache.org/docs/python/parquet/index.html)
