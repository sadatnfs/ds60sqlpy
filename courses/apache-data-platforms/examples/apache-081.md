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
