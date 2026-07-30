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

## Exercises

### Exercise 1 — define the CSV contract

Implement `parse_nullable_text` and `total_revenue`. Parse dates, integers, and
prices in one place rather than scattering conversion across analysis code.
Test blank notes and a malformed number.

For real money, prefer `Decimal` or integer minor units. A binary `float` is
used in the learner exercise only to keep its first step small.

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

### Exercise 3 — build an Arrow schema

With PyArrow installed, define non-null integer, date, region, category, units,
and decimal fields plus a nullable note. Create the table with this schema,
write Parquet, read it, and assert:

- schema equality,
- six rows, and
- three null notes.

Do not infer the schema first and then claim it was guaranteed.

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

### Exercise 5 — query Parquet with DuckDB

Use an in-memory connection and `read_parquet(?)`. Group revenue by region for
rows with at least two units. Bind path and threshold values as parameters.

Then run `EXPLAIN` on the same SQL. Find:

- a Parquet scan,
- a units filter, and
- projected columns that exclude `note`.

Record the plan from your installed DuckDB version. Plan formatting changes, so
look for semantics rather than copying one exact rendering.

### Exercise 6 — explain pushdown honestly

Pushdown does not mean every query reads zero irrelevant bytes. Row-group
statistics, file organization, filter selectivity, expression support, and
engine version matter. Write:

1. what the plan proves,
2. what it suggests may be skipped, and
3. what would require profiling or scan metrics to prove.

### Exercise 7 — exercise the fallback

Run `summarize_with_csv_fallback` in an environment without PyArrow/DuckDB. If
pandas exists, it uses typed `read_csv`; otherwise it uses the standard
library. Confirm the same row count, null count, region set, and revenue across
engines.

### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 8 — plan schema evolution

Create version 2 of the sales schema with one nullable additive column and one proposed type change. Define which readers remain compatible and write a migration/rejection policy.

**Progressive hint:** Adding a nullable field is often backward-compatible; changing decimal scale, nullability, meaning, or type may require a new dataset version.

### Exercise 9 — control file and row-group size

Generate a larger local deterministic dataset and compare many tiny Parquet files with fewer bounded files/row groups. Record metadata count, scan planning, file sizes, and filtered query behavior.

**Progressive hint:** Partition values and file size solve different problems. Keep the total dataset small enough for a laptop and repeat measurements.

### Exercise 10 — validate a dataset before querying

Build a local validation report for schema equality, required/null counts, unique row IDs, accepted regions, positive units, decimal range, date range, partition-to-column agreement, and total row count.

**Progressive hint:** Read metadata and bounded columns first where possible; include failing row counts and opaque IDs without dumping sensitive data.

### Exercise 11 — reconcile a local analytical join

Create a small region lookup fixture, join it to sales in DuckDB, and reproduce the result with standard-library or pandas logic. Include an unknown region and duplicate lookup key.

**Progressive hint:** Validate lookup-key uniqueness before the join and choose inner versus left semantics explicitly.

### Exercise 12 — find a non-pushdown filter

Compare `units >= ?` with a transformed predicate such as a function of units. Inspect plans and scan evidence, then rewrite only when semantics remain identical.

**Progressive hint:** Simple comparisons often map to row-group statistics; arbitrary functions may need evaluation after scanning.

### Exercise 13 — publish a dataset atomically

Write partitioned output to a temporary version directory, validate it, create a manifest of relative paths, sizes, hashes, rows, and schema, then atomically update a local current-version pointer.

**Progressive hint:** Readers must never see a half-written dataset. The manifest is written after data files and verified before promotion.

### Exercise 14 — reconcile decimals and timestamps across engines

Add boundary decimal values and timezone-aware timestamps to a local round trip. Compare CSV parsing, Arrow/Parquet, pandas, and DuckDB types and results with explicit normalization.

**Progressive hint:** Declare decimal precision/scale and one timestamp storage timezone. Compare canonical values, not default display strings.

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
