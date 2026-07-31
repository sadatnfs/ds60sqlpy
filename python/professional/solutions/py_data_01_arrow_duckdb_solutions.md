# Arrow and DuckDB solution reasoning

Attempt `python-data-01` before opening the executable
[`py_data_01_arrow_duckdb_solution.py`](py_data_01_arrow_duckdb_solution.py).

## Boundary-first parsing

The tracked CSV is intentionally plain text. `parse_sale` is the single place
that establishes integer, date, decimal, and nullable-text semantics. It checks
required fields and rejects negative units or prices. Downstream code can
therefore accept `Sale` rather than repeatedly guessing what strings mean.

The portable summary uses `Decimal` and an explicit zero. The pandas fallback
also reads prices as strings before constructing decimals; converting through a
binary float would import approximation into the calculation.

## Why the fallback is layered

The module first guarantees a standard-library CSV route. If pandas exists, it
demonstrates a convenient typed CSV reader. PyArrow and DuckDB are separate,
optional capabilities. Package detection never installs or downloads
anything, so an offline learner gets a complete, truthful reduced path.

## Schema and null proof

The Arrow schema marks every domain field non-null except `note` and gives price
a two-decimal fixed-width decimal type. `Table.from_pylist(..., schema=schema)`
applies that contract before writing. Reading the Parquet file and comparing
the complete schema proves more than checking values alone.

The test also checks `null_count == 3`. Empty strings from CSV became Python
`None`, which Arrow writes as NULL rather than a zero-length string.

## Partition safety

`partition_directory` accepts a deliberately small alphabet. That prevents a
domain value from becoming `../...` or creating nested directories. The writer
sorts region keys and keeps stable filenames, so tests and examples remain
deterministic.

This policy is suitable for the fixture, not universal. Real systems often map
arbitrary domain values to encoded partition values and maintain a catalog.

## Query-plan evidence

DuckDB receives the path and threshold as parameters. The aggregate query does
not reference `note`, and its filter uses `units`. `EXPLAIN` is captured and
searched for filter/projection semantics. That supports the claim that the
engine planned selective work.

It does not prove an exact byte count. To establish physical skipping for a
large dataset, inspect profiling metrics and design row groups or partitions
whose statistics make skipping possible.

## Alternatives and edge cases

- CSV remains an excellent interchange format for small, inspectable, or
  streaming data. Add a sidecar schema when contracts matter.
- Arrow IPC/Feather targets fast Arrow exchange; Parquet targets durable,
  compressed analytical storage.
- DuckDB can read CSV directly, but doing so does not demonstrate Parquet schema
  preservation.
- A dataset may evolve fields. Decide whether readers unify compatible schemas,
  reject drift, or migrate old files.
- Hive-style partition names are a convention. They do not automatically make
  a dimension a good partition key.

## Expected results

The portable path reports six rows, revenue `114.60`, three null notes, and
three region partitions. With optional packages, the Parquet schema round trip
is equal and DuckDB reports qualifying revenue for north, south, and west while
its plan exposes filter and projection information.

---

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Reasoning before implementation

Boundary parsing proves semantic types first; round-trip, plan, and cross-engine reconciliation then prove storage/query behavior.

1. **explicit parse/schema:** turns untrusted text into typed dates, decimals, integers, and nullable fields at one controlled boundary.
2. **Parquet row groups/partitions:** organize data for selective scans without creating unsafe values or millions of tiny files.
3. **DuckDB projection/filter:** pushes required columns and supported predicates near the scan; inspect plan and profile.
4. **Prove the failure boundary:** Exercise one normal case, one boundary case, and one injected failure without relying on hidden state.

**Alternative:** CSV remains excellent for small interchange; SQLite/pandas may be simpler when schema scale and selective scans do not justify Arrow tooling.

**Trade-off:** Parquet adds schema/compression/pushdown while requiring engines, evolution policy, file-layout management, and less direct inspection.

**Failure boundary:** Decimal overflow, timezone normalization, schema evolution, partition traversal, duplicate lookup keys, tiny files, and missing optional packages need policy.

**Verification:** Reconcile typed values/nulls/totals across engines, assert schema round-trip, reject unsafe partitions, inspect plan plus scan metrics, and exercise the CSV fallback.

### Verification micro-example

Run this small, deterministic case before adapting the reference to a
larger system. It gives the reasoning above an executable anchor:

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

The reference implementation is one defensible contract, not a license
to copy internal steps into every system. Preserve the observable
guarantees and repeat the failure tests when adapting it.

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reference

Use this map after an honest attempt. The executable implementation remains
[`py_data_01_arrow_duckdb_solution.py`](py_data_01_arrow_duckdb_solution.py); this section explains the
contract, evidence, alternatives, and edge cases behind every numbered task.

### Exercise 1 — define the CSV contract

**Prompt recap:** Implement `parse_nullable_text` and `total_revenue`. Parse dates, integers, and prices in one place rather than scattering conversion across analysis code. Test blank notes and a malformed number. For real money, prefer `Decimal` or integer minor units. A binary `float` is used in the learner exercise only to keep its first step small.

**Reference reasoning:** A columnar pipeline needs an explicit schema, null/decimal semantics, safe partitions, parameterized local queries, and cross-engine evidence. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** define the CSV contract — assert parse_nullable_text('') is None and nonblank text is preserved; on the six-row fixture, total_revenue must be 114.60, blank notes count to three, and a malformed numeric field raises ValueError naming the field.

### Exercise 2 — compare storage contracts

**Prompt recap:** Make a table in your notes: | Question | CSV | Parquet | | --- | --- | --- | | Can a text editor inspect it? | | | | Are types/nullability stored? | | | | Can a scan select columns efficiently? | | | | Does Python need an extra engine? | | | | Is append/stream exchange simple? | | | Choose a format for a five-row configuration export and for a repeated 50-million-row analytical scan. Explain each answer.

**Reference reasoning:** A columnar pipeline needs an explicit schema, null/decimal semantics, safe partitions, parameterized local queries, and cross-engine evidence. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** compare storage contracts — complete every CSV/Parquet comparison-table cell, choose CSV for the five-row human-inspected configuration and Parquet for the repeated 50-million-row scan, and cite type/nullability, projection, engine, streaming, and inspection evidence for both choices.

### Exercise 3 — build an Arrow schema

**Prompt recap:** With PyArrow installed, define non-null integer, date, region, category, units, and decimal fields plus a nullable note. Create the table with this schema, write Parquet, read it, and assert: - schema equality, - six rows, and - three null notes. Do not infer the schema first and then claim it was guaranteed.

**Reference reasoning:** A columnar pipeline needs an explicit schema, null/decimal semantics, safe partitions, parameterized local queries, and cross-engine evidence. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** build an Arrow schema — with PyArrow installed, define non-null integer, date, region, category, units, and decimal fields plus a nullable note; create the table with this schema, write Parquet, read it, and assert: - schema equality, - six rows, and - three null notes; do not infer the schema first and then claim it was guaranteed.

### Exercise 4 — make partitions deliberate

**Prompt recap:** Implement `partition_directory`. Reject `../north`, slashes, empty strings, and unexpected case. Write one stable file per region at `region=<validated-value>/part-000.csv`. Partitioning every high-cardinality value can create millions of tiny files, so choose commonly filtered dimensions and plan file sizes.

**Reference reasoning:** A columnar pipeline needs an explicit schema, null/decimal semantics, safe partitions, parameterized local queries, and cross-engine evidence. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** make partitions deliberate — assert north, south, and west map exactly to region=<value>/part-000.csv under the root; ../north, either slash, blank, and wrong-case values must raise ValueError before any file is written.

### Exercise 5 — query Parquet with DuckDB

**Prompt recap:** Use an in-memory connection and `read_parquet(?)`. Group revenue by region for rows with at least two units. Bind path and threshold values as parameters. Then run `EXPLAIN` on the same SQL. Find: - a Parquet scan, - a units filter, and - projected columns that exclude `note`. Record the plan from your installed DuckDB version. Plan formatting changes, so look for semantics rather than copying one exact rendering.

**Reference reasoning:** A columnar pipeline needs an explicit schema, null/decimal semantics, safe partitions, parameterized local queries, and cross-engine evidence. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** query Parquet with DuckDB — assert the parameterized DuckDB result equals the fallback's sorted region/revenue rows; the EXPLAIN output must name a Parquet scan, units filter, and projected revenue/region/units columns while excluding note.

### Exercise 6 — explain pushdown honestly

**Prompt recap:** Pushdown does not mean every query reads zero irrelevant bytes. Row-group statistics, file organization, filter selectivity, expression support, and engine version matter. Write: 1. what the plan proves, 2. what it suggests may be skipped, and 3. what would require profiling or scan metrics to prove.

**Reference reasoning:** A columnar pipeline needs an explicit schema, null/decimal semantics, safe partitions, parameterized local queries, and cross-engine evidence. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** explain pushdown honestly — write a three-row evidence table separating what EXPLAIN proves, what row-group statistics suggest, and what measured scanned rows/bytes must establish; include one selective and one nonselective filter result.

### Exercise 7 — exercise the fallback

**Prompt recap:** Run `summarize_with_csv_fallback` in an environment without PyArrow/DuckDB. If pandas exists, it uses typed `read_csv`; otherwise it uses the standard library. Confirm the same row count, null count, region set, and revenue across engines.

**Reference reasoning:** A columnar pipeline needs an explicit schema, null/decimal semantics, safe partitions, parameterized local queries, and cross-engine evidence. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** exercise the fallback — force the no-PyArrow/no-DuckDB path and assert row count 6, null-note count 3, the same region set, and revenue 114.60; compare every value with the optional-engine result when that capability is installed.

### Exercise 8 — plan schema evolution

**Prompt recap:** Create version 2 of the sales schema with one nullable additive column and one proposed type change. Define which readers remain compatible and write a migration/rejection policy.

**Reasoning path:** Adding a nullable field is often backward-compatible; changing decimal scale, nullability, meaning, or type may require a new dataset version.

Persist a schema version and field metadata beside each dataset. A v1 reader
can ignore an additive nullable field when its projection is explicit. A v2
reader supplies a documented default/null when reading v1. A type or semantic
change is rejected or transformed through a named migration with validation.

Test both directions using explicit Arrow schemas; do not rely on whatever
coercion the installed engine happens to perform.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** plan schema evolution — create version 2 of the sales schema with one nullable additive column and one proposed type change; define which readers remain compatible and write a migration/rejection policy.

### Exercise 9 — control file and row-group size

**Prompt recap:** Generate a larger local deterministic dataset and compare many tiny Parquet files with fewer bounded files/row groups. Record metadata count, scan planning, file sizes, and filtered query behavior.

**Reasoning path:** Partition values and file size solve different problems. Keep the total dataset small enough for a laptop and repeat measurements.

Write the same typed rows with two layouts, verify identical aggregates, then
compare file count, median file bytes, row-group statistics, and repeated query
times. Treat timing as machine-specific evidence. Tiny files add filesystem and
planning overhead; overly large row groups reduce pruning granularity.

Choose a target range based on actual storage/engine workload rather than a
universal number. Clean the generated data under an ignored temporary path.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** control file and row-group size — generate a larger local deterministic dataset and compare many tiny Parquet files with fewer bounded files/row groups; record metadata count, scan planning, file sizes, and filtered query behavior.

### Exercise 10 — validate a dataset before querying

**Prompt recap:** Build a local validation report for schema equality, required/null counts, unique row IDs, accepted regions, positive units, decimal range, date range, partition-to-column agreement, and total row count.

**Reasoning path:** Read metadata and bounded columns first where possible; include failing row counts and opaque IDs without dumping sensitive data.

Separate hard contract failures from informational statistics. Validate every
file against the declared schema and ensure the path partition value equals the
stored region. Duplicate IDs, unsafe regions, negative units, or schema drift
fail before analytical SQL runs.

The report includes dataset/version hash, file count, rows, and per-check
status. A successful Parquet read is not a data-quality proof.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** validate a dataset before querying — build a local validation report for schema equality, required/null counts, unique row IDs, accepted regions, positive units, decimal range, date range, partition-to-column agreement, and total row count.

### Exercise 11 — reconcile a local analytical join

**Prompt recap:** Create a small region lookup fixture, join it to sales in DuckDB, and reproduce the result with standard-library or pandas logic. Include an unknown region and duplicate lookup key.

**Reasoning path:** Validate lookup-key uniqueness before the join and choose inner versus left semantics explicitly.

Reject the duplicate dimension key rather than allowing an accidental
many-to-many revenue multiplication. For a left join, preserve every sale and
mark unknown region metadata as missing; for an inner join, report excluded row
and revenue counts.

Sort and compare canonical output rows across engines, including decimal
normalization and nulls. Matching totals alone can hide duplicated and dropped
rows.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** reconcile a local analytical join — create a small region lookup fixture, join it to sales in DuckDB, and reproduce the result with standard-library or pandas logic; include an unknown region and duplicate lookup key.

### Exercise 12 — find a non-pushdown filter

**Prompt recap:** Compare `units >= ?` with a transformed predicate such as a function of units. Inspect plans and scan evidence, then rewrite only when semantics remain identical.

**Reasoning path:** Simple comparisons often map to row-group statistics; arbitrary functions may need evaluation after scanning.

Parameterize both queries, verify equal selected rows for the chosen rewrite,
and inspect `EXPLAIN` for filter placement. Record engine/version because plan
syntax and supported pushdown evolve. If scan metrics are unavailable, claim
only what the plan shows—not bytes avoided.

Never alter boundary behavior (nulls, overflow, rounding, timezone) merely to
obtain a prettier plan.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** find a non-pushdown filter — print both plans and measured scan evidence for units >= 2 and the transformed predicate; if rewritten, assert the sorted result rows are identical and record whether filter/projection pushdown changed.

### Exercise 13 — publish a dataset atomically

**Prompt recap:** Write partitioned output to a temporary version directory, validate it, create a manifest of relative paths, sizes, hashes, rows, and schema, then atomically update a local current-version pointer.

**Reasoning path:** Readers must never see a half-written dataset. The manifest is written after data files and verified before promotion.

Use a unique staging directory under ignored storage. Close all writers,
validate every file, and write the manifest last. Promotion uses an atomic
rename or small pointer-file replacement supported by the local filesystem.
On failure, leave the previous version untouched and remove/review staging.

Do not overwrite an existing immutable version. Hashes detect accidental
change but do not prove source trust or data correctness.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** publish a dataset atomically — write partitioned output to a temporary version directory, validate it, create a manifest of relative paths, sizes, hashes, rows, and schema, then atomically update a local current-version pointer.

### Exercise 14 — reconcile decimals and timestamps across engines

**Prompt recap:** Add boundary decimal values and timezone-aware timestamps to a local round trip. Compare CSV parsing, Arrow/Parquet, pandas, and DuckDB types and results with explicit normalization.

**Reasoning path:** Declare decimal precision/scale and one timestamp storage timezone. Compare canonical values, not default display strings.

Represent money as Arrow decimal and SQL DECIMAL, checking overflow and scale
before write. Store instants in UTC with timezone metadata and derive local
calendar fields separately. CSV needs explicit parsers for both contracts.

Normalize query results into decimal strings/minor units and UTC ISO timestamps
before cross-engine comparison. Reject naive/ambiguous timestamps rather than
letting local machine timezone decide.

**Common trap:** Schema inference, float money, unsafe partition text, tiny files, or engine-specific coercion can produce plausible aggregates whose underlying contract has changed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** reconcile decimals and timestamps across engines — add boundary decimal values and timezone-aware timestamps to a local round trip; compare CSV parsing, Arrow/Parquet, pandas, and DuckDB types and results with explicit normalization.
