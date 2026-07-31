# Columnar data, Arrow, Parquet, and embedded analytical SQL

**Stable ID:** `python-data-01`

**Level:** intermediate/advanced

**Estimated time:** 180–240 minutes

## Level and prerequisites

- **Catalog prerequisite:** `python-23`
- Python Days 1–23, especially CSV, pandas I/O, generators, and data pipelines
- SQL `SELECT`, `WHERE`, aggregation, and `GROUP BY`
- Core setup for the CSV path
- Optional local `pandas`, `pyarrow`, and `duckdb` packages for the columnar path

The tracked dataset is
[`fixtures/data/sales.csv`](../fixtures/data/sales.csv). No example downloads
data. Missing optional packages activate an explained CSV fallback.

## Learning objectives

By the end, you can:

1. Compare CSV and Parquet by portability, schema, nulls, and scan behavior.
2. Apply an explicit schema at a text-file boundary.
3. Explain Arrow's in-memory columnar role and Parquet's file role.
4. Preserve typed dates, decimals, and nullable text in a Parquet round trip.
5. Create a partition-aware local layout without unsafe path values.
6. Query a Parquet file with embedded DuckDB and inspect its plan.
7. Describe projection and predicate pushdown using observed evidence.
8. Choose the portable CSV fallback when columnar dependencies are unavailable.

### Motivation

CSV is inspectable almost everywhere, but it does not carry a type system:
`"2"`, `"2026-01-02"`, and an empty field all arrive as text. Columnar formats
can preserve schema and avoid reading irrelevant columns or row groups. Those
advantages are useful only when the surrounding tools, schema ownership, and
interoperability justify the additional dependency.

## Vocabulary and concepts

- **Row-oriented:** values for one record are stored together.
- **Columnar:** values for one field are stored together, enabling compressed
  and selective analytical scans.
- **Schema:** field names, types, nullability, and sometimes metadata.
- **NULL:** an explicitly missing value, distinct from empty text and zero.
- **Arrow:** a language-independent columnar memory format and ecosystem.
- **Parquet:** a columnar file format with schema and row-group metadata.
- **Row group:** a horizontal chunk whose statistics may allow skipping.
- **Projection pushdown:** reading only columns required by a query.
- **Predicate pushdown:** applying filters at or near the scan so irrelevant
  data can be skipped.
- **Partition:** a directory or file grouping derived from a bounded dimension,
  such as `region=north`.
- **Embedded database:** a query engine running in the application process
  rather than a separate server.
- **Query plan:** the engine's description of how it will execute a query.

## Worked example / walkthrough

### Observe CSV's boundary

Before running the learner file, predict the Python type of `units`,
`unit_price`, and an empty `note`.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_data_01_arrow_duckdb.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_data_01_arrow_duckdb.py
```

`csv.DictReader` returns strings. The empty note is `""`, not `None`. This is
why the solution defines `Sale` and converts every field at one controlled
boundary.

### Follow the local columnar path

The executable reference performs this flow in a temporary directory:

```text
tracked CSV -> typed Sale values -> Arrow table -> Parquet file
                                      |
                                      +-> schema/null round-trip check
                                      |
                                      +-> DuckDB SELECT + EXPLAIN
```

Run it with the optional packages installed:

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\solutions\py_data_01_arrow_duckdb_solution.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/solutions/py_data_01_arrow_duckdb_solution.py
```

If PyArrow or DuckDB is absent, the program says so and still completes the
CSV and partition exercises. It never tries to install a package.

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

Work from the repository root. First run the answer-free learner
module named in this guide's original walkthrough. Read each TODO as a
contract: record the input, returned value, raised exception, and side
effect before implementing it. Then run the focused test command in
**Self-check**. Keep exploratory changes in a copy or a new test; the
checked-in solution remains a comparison artifact.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_data_01_arrow_duckdb.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_data_01_arrow_duckdb.py
```

The focused test command is shown in **Self-check** below. The learner
module is intentionally answer-free, so `TODO` output is the expected
starting state rather than a setup failure.

## Mechanism lab — two small examples before the full system

### Boundary and mental model

CSV records text and delimiters but carries no authoritative type or
nullability contract. Arrow is a language-independent columnar memory
representation; Parquet is a columnar file format with schema, row
groups, encodings, and statistics. DuckDB is an embedded engine that
can query these files without loading every column into pandas first.

Columnar performance depends on selecting columns, filtering using
supported predicates, row-group statistics, file sizes, and partition
layout. An `EXPLAIN` plan shows intended operations; bytes read and
elapsed profiles establish what was actually skipped.

- **explicit parse/schema:** turns untrusted text into typed dates, decimals, integers, and nullable fields at one controlled boundary.
- **Parquet row groups/partitions:** organize data for selective scans without creating unsafe values or millions of tiny files.
- **DuckDB projection/filter:** pushes required columns and supported predicates near the scan; inspect plan and profile.

### Micro-example A — observe CSV's string-only boundary

```python
import csv
from pathlib import Path

path = Path("python/professional/fixtures/data/sales.csv")
with path.open("r", encoding="utf-8", newline="") as handle:
    row = next(csv.DictReader(handle))
types = {name: type(value).__name__ for name, value in row.items()}
print(row, types)
assert set(types.values()) == {"str"}
```

**Expected observation:** Dates, units, prices, and blanks all arrive as strings and must be interpreted by an explicit contract.

**Why it matters:** The tracked fixture encoding, delimiter, header, decimal/date meanings, and blank-value policy are known.

### Micro-example B — show why projection changes analytical work

```python
rows = [
    {"region": "north", "units": 2, "note": "large free text"},
    {"region": "south", "units": 1, "note": "another free text"},
]
projected = [
    {"region": row["region"], "units": row["units"]}
    for row in rows if row["units"] >= 2
]
print(projected)
assert projected == [{"region": "north", "units": 2}]
```

**Expected observation:** The query's logical result needs only two fields; a columnar engine may avoid reading the unrelated note column.

**Why it matters:** Physical pushdown still requires supported file metadata, expression, layout, and engine evidence.

### Debugging and transfer

**Common mistake:** Inferring a schema from one batch and claiming it guarantees later files, or treating `EXPLAIN` as bytes-read proof.

**Diagnostic:** Validate schema/nulls/keys/ranges, inspect file/row-group metadata and plan, then profile a bounded query against a CSV/pandas fallback.

**Transfer question:** How would decimal precision, timestamp timezone, and an additive nullable field be versioned across readers?

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercises

### Exercise 1 — define the CSV contract

Implement `parse_nullable_text` and `total_revenue`. Parse dates, integers, and
prices in one place rather than scattering conversion across analysis code.
Test blank notes and a malformed number.

For real money, prefer `Decimal` or integer minor units. A binary `float` is
used in the learner exercise only to keep its first step small.

**Verify:** For task `define the CSV contract`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 2 — compare storage contracts

Make a table in your notes:

| Question | CSV | Parquet |
| --- | --- | --- |
| Can a text editor inspect it? |  |  |
| Are types/nullability stored? |  |  |
| Can a scan select columns efficiently? |  |  |
| Does Python need an extra engine? |  |  |
| Is append/stream exchange simple? |  |  |

Choose a format for a five-row configuration export and for a repeated
50-million-row analytical scan. Explain each answer.

**Verify:** For task `compare storage contracts`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 3 — build an Arrow schema

With PyArrow installed, define non-null integer, date, region, category, units,
and decimal fields plus a nullable note. Create the table with this schema,
write Parquet, read it, and assert:

- schema equality,
- six rows, and
- three null notes.

Do not infer the schema first and then claim it was guaranteed.

**Verify:** For task `build an Arrow schema`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.







### Exercise 4 — make partitions deliberate

Implement `partition_directory`. Reject `../north`, slashes, empty strings, and
unexpected case. Write one file per region under:

```text
region=north/part-000.csv
region=south/part-000.csv
region=west/part-000.csv
```

Partitioning every high-cardinality value can create millions of tiny files.
Choose stable, commonly filtered dimensions and plan file sizes.

**Verify:** For task `make partitions deliberate`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Exercise 5 — query Parquet with DuckDB

Use an in-memory connection and `read_parquet(?)`. Group revenue by region for
rows with at least two units. Bind path and threshold values as parameters.

Then run `EXPLAIN` on the same SQL. Find:

- a Parquet scan,
- a units filter, and
- projected columns that exclude `note`.

Record the plan from your installed DuckDB version. Plan formatting changes, so
look for semantics rather than copying one exact rendering.

**Verify:** For task `query Parquet with DuckDB`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 6 — explain pushdown honestly

Pushdown does not mean every query reads zero irrelevant bytes. Row-group
statistics, file organization, filter selectivity, expression support, and
engine version matter. Write:

1. what the plan proves,

**Verify:** For task `what the plan proves,`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.





2. what it suggests may be skipped, and

**Verify:** For task `what it suggests may be skipped, and`, demonstrate the concrete requirement “2. what it suggests may be skipped, and” with explicit inputs, observable output, and one counterexample.





3. what would require profiling or scan metrics to prove.

**Verify:** For task `what would require profiling or scan metrics to prove`, demonstrate the concrete requirement “3. what would require profiling or scan metrics to prove” with explicit inputs, observable output, and one counterexample.







### Exercise 7 — exercise the fallback

Run `summarize_with_csv_fallback` in an environment without PyArrow/DuckDB. If
pandas exists, it uses typed `read_csv`; otherwise it uses the standard
library. Confirm the same row count, null count, region set, and revenue across
engines.

**Verify:** For task `exercise the fallback`, record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.







### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 8 — plan schema evolution

Create version 2 of the sales schema with one nullable additive column and one proposed type change. Define which readers remain compatible and write a migration/rejection policy.

**Progressive hint:** Adding a nullable field is often backward-compatible; changing decimal scale, nullability, meaning, or type may require a new dataset version.

**Verify:** For task `plan schema evolution`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then assert exact names, order, types/nullability or versions and prove one mismatch is rejected rather than silently coerced.







### Exercise 9 — control file and row-group size

Generate a larger local deterministic dataset and compare many tiny Parquet files with fewer bounded files/row groups. Record metadata count, scan planning, file sizes, and filtered query behavior.

**Progressive hint:** Partition values and file size solve different problems. Keep the total dataset small enough for a laptop and repeat measurements.

**Verify:** For task `control file and row-group size`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Exercise 10 — validate a dataset before querying

Build a local validation report for schema equality, required/null counts, unique row IDs, accepted regions, positive units, decimal range, date range, partition-to-column agreement, and total row count.

**Progressive hint:** Read metadata and bounded columns first where possible; include failing row counts and opaque IDs without dumping sensitive data.

**Verify:** For task `validate a dataset before querying`, record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state; then assert exact names, order, types/nullability or versions and prove one mismatch is rejected rather than silently coerced.







### Exercise 11 — reconcile a local analytical join

Create a small region lookup fixture, join it to sales in DuckDB, and reproduce the result with standard-library or pandas logic. Include an unknown region and duplicate lookup key.

**Progressive hint:** Validate lookup-key uniqueness before the join and choose inner versus left semantics explicitly.

**Verify:** For task `reconcile a local analytical join`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.







### Exercise 12 — find a non-pushdown filter

Compare `units >= ?` with a transformed predicate such as a function of units. Inspect plans and scan evidence, then rewrite only when semantics remain identical.

**Progressive hint:** Simple comparisons often map to row-group statistics; arbitrary functions may need evaluation after scanning.

**Verify:** For task `find a non-pushdown filter`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Exercise 13 — publish a dataset atomically

Write partitioned output to a temporary version directory, validate it, create a manifest of relative paths, sizes, hashes, rows, and schema, then atomically update a local current-version pointer.

**Progressive hint:** Readers must never see a half-written dataset. The manifest is written after data files and verified before promotion.

**Verify:** For task `publish a dataset atomically`, assert exact names, order, types/nullability or versions and prove one mismatch is rejected rather than silently coerced; then verify identity/hash and metadata, then reload or inspect the artifact outside the creating state and test one tampered mismatch.







### Exercise 14 — reconcile decimals and timestamps across engines

Add boundary decimal values and timezone-aware timestamps to a local round trip. Compare CSV parsing, Arrow/Parquet, pandas, and DuckDB types and results with explicit normalization.

**Progressive hint:** Declare decimal precision/scale and one timestamp storage timezone. Compare canonical values, not default display strings.

**Verify:** For task `reconcile decimals and timestamps across engines`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then show the relevant row/group/time identities and assert the training and evaluation information boundaries are disjoint.







## Self-check

- Raw CSV values are recognized as text until parsed.
- Empty note fields become `None`, not an accidental empty category.
- Revenue is exactly `114.60` with decimal arithmetic.
- Partition values cannot escape their output directory.
- The Arrow schema before and after Parquet is identical.
- Parquet retains six rows and three null notes.
- DuckDB returns only qualifying regional aggregates.
- The plan visibly contains filter and projection evidence.
- The module completes offline when optional packages are absent.

Run the focused tests:

Windows PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m unittest python.professional.tests.test_py_data_01_arrow_duckdb -v
```

macOS/Linux:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest python.professional.tests.test_py_data_01_arrow_duckdb -v
```

## Common pitfalls

- **Dates or integers become generic objects:** schema inference saw mixed or
  missing values. Declare and validate the schema at ingestion.
- **Empty text and NULL are conflated:** decide the domain meaning before
  converting; empty text may be a valid value in some datasets.
- **Parquet import fails:** pandas needs a Parquet engine. Use explicit
  PyArrow, or remain on the documented CSV path.
- **A query plan lacks pushdown text:** engine versions format plans
  differently, or the expression cannot be pushed into the scan. Inspect the
  complete plan and simplify the predicate.
- **A partition creates an unsafe path:** raw domain text was used as a
  directory. Validate against a bounded alphabet or map values explicitly.
- **Thousands of tiny files make scans slower:** partition granularity or write
  batching is too fine.
- **Results differ by a fraction:** binary floating-point was used for decimal
  currency. Use a decimal schema or integer minor units.

## Next step

- Apply the format decision to Python Day 23's pipeline with an explicit schema.
- Compare DuckDB's local analytical role with PostgreSQL's multi-user,
  transactional role.
- Continue to `python-pro-01` if the data pipeline should become an installable
  package, or Bridge Day 6 for database bulk-loading contracts.

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-data-01` — Columnar data, Arrow, Parquet, and embedded analytical SQL.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize typed data boundaries, Arrow/Parquet schema, partitions, and pushdown evidence. Use exactly these maintained learner materials:
- guide: `python/professional/companion-guides/py_data_01_arrow_duckdb.md`
- learner artifact: `python/professional/lessons/py_data_01_arrow_duckdb.py`

Assume only the prerequisites declared in the guide. Do not open or
quote anything under `solutions/` unless I explicitly ask after an
honest attempt. First explain one concept in plain language and show a
tiny example. Then ask me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
