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
