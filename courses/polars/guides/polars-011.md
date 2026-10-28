# polars-011: Files, schema boundaries and columnar artifacts

## Level and prerequisites

Intermediate. Direct prerequisites: `polars-003`, `polars-010`

**Outcome:** Publish a small typed artifact with independently checked readback.

## Question and mechanism

A file boundary is both an I/O boundary and a data contract. CSV stores textual fields and relies on parsing rules. Parquet stores typed columns and metadata that can support selective reading. Neither format guarantees correct identifiers, units or valid rows. The program should state the expected schema and verify the records that cross the boundary.

Partitioned data adds another layer of identity. A glob can select several files, but file order is not a meaningful record order. A stable key and an explicit sort are needed for sequence comparisons. A new output file should also be kept outside the input pattern; otherwise a later run may accidentally ingest its previous output and duplicate records.

When parsing a textual source, preserve raw values until rejection is accounted for. Reading a mixed amount column as text and then casting it under an explicit policy makes the bad token visible. The accepted total and rejected identifiers form complementary evidence. Publishing only a successful total would hide the fact that one source row did not contribute.

## Syntax and data contract

write_parquet emits typed columnar data, scan_parquet builds a lazy source, and sink_parquet materializes a query into an output file. A glob such as part-*.parquet should name only inputs. schema_overrides can keep a problematic CSV field as text so its parsing policy is explicit. Use readback checks on the output artifact instead of assuming a completed write preserves the intended result.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Combine typed parts and verify readback

Two Parquet parts contain three identified records. The lazy query selects the contract fields and writes a combined result. The readback assertion checks both key order and the total after sorting, without relying on the filesystem's listing order.

**Expected evidence:** The combined artifact contains ids [1, 2, 3] with total value 10.5.

```python
import tempfile
from pathlib import Path

import polars as pl


def example_one():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        pl.DataFrame({"id": [1, 2], "value": [2.5, 3.5]}).write_parquet(root / "part-a.parquet")
        pl.DataFrame({"id": [3], "value": [4.5]}).write_parquet(root / "part-b.parquet")
        query = pl.scan_parquet(str(root / "part-*.parquet")).select("id", "value")
        query.sink_parquet(root / "combined.parquet")
        result = pl.read_parquet(root / "combined.parquet").sort("id")
        assert result["id"].to_list() == [1, 2, 3]
        assert result["value"].sum() == 10.5
        return {"rows": result.to_dicts(), "schema": str(result.schema)}


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Quarantine malformed CSV text

The CSV fixture includes a nonnumeric token. The program reads the field as text, derives a numeric value and identifies the rejected record. It keeps the raw token in the quarantine output so the cause can be explained.

**Expected evidence:** Id 2 is rejected and accepted numeric values total 6.

```python
import tempfile
from pathlib import Path

import polars as pl


def example_two():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "raw.csv"
        path.write_text("id,amount\n1,2\n2,broken\n3,4\n")
        raw = pl.read_csv(path, schema_overrides={"amount": pl.String})
        parsed = raw.with_columns(pl.col("amount").cast(pl.Int64, strict=False).alias("parsed"))
        invalid = parsed.filter(pl.col("parsed").is_null())
        assert invalid["id"].to_list() == [2]
        assert parsed.filter(pl.col("parsed").is_not_null())["parsed"].sum() == 6
        return {"quarantine": invalid.to_dicts(), "accepted_total": 6}


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Change input order

Rename the input parts so their lexical order changes.

**Check:** Sorted logical output remains equal.

**Hint:** File order is not row identity.


### 2. Prevent self-ingestion

Explain why combined.parquet is outside part-*.parquet.

**Check:** A rerun does not read its prior combined output.

**Hint:** Inspect the input pattern.


### 3. Validate the output key

Check output id uniqueness after combining parts.

**Check:** n_unique equals height for the valid fixture.

**Hint:** Parts can overlap.


### 4. Track rejected coverage

Report accepted and rejected CSV counts.

**Check:** Two accepted plus one rejected equals three source rows.

**Hint:** Every source row needs an outcome.


### 5. Test a schema change

Change one part from numeric values to incompatible text.

**Check:** The program either rejects it or follows a documented cast policy.

**Hint:** Do not rely on accidental coercion.


### 6. Verify an artifact

Read the written Parquet file and compare its schema and values.

**Check:** Readback matches the intended frame.

**Hint:** The write return value is not the result itself.


## Diagnose errors and misleading results

A glob that includes an output directory can inflate every subsequent run. A CSV inference error can originate from a late malformed token rather than a completely wrong delimiter. Inspect selected paths, schemas and row accounting before adding broad ignore_errors behavior. Keep the example's temporary paths distinct from a learner's valuable files.

## Transfer to independent work

Publish a small typed artifact with independently checked readback. Extend it to multiple input parts, a deliberate overlap and one malformed value. Describe which failures stop publication and which produce an explicit quarantine artifact; that decision becomes a testable contract in analytics engineering.

## Primary references

- [Polars documentation: Files, schema boundaries and columnar artifacts](https://docs.pola.rs/user-guide/io/parquet/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-011`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
