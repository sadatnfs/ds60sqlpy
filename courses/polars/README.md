# Polars: columnar data engineering

A complete route through typed tables, expression semantics, temporal correctness, lazy execution, Arrow interoperability, measured performance and validated data publication.

Start from the [main Docker instructions](../../README.md). Select this subject in the shared classroom. This path uses the prepared `data-engineering` worker and requires no host compiler or account. All examples use local synthetic inputs after image preparation.

## Route

| Lesson | Stage | Outcome |
| --- | --- | --- |
| [polars-001: Rows, columns, schemas and expressions](guides/polars-001.md) | beginner | Construct and verify a typed table with a stated row grain. |
| [polars-002: Expression contexts and explicit dependencies](guides/polars-002.md) | beginner | Build a transformation whose dependency stages are explicit. |
| [polars-003: Types, parsing failures and exact numeric values](guides/polars-003.md) | beginner | Implement a parsing policy that preserves rejected evidence. |
| [polars-004: Null, NaN and three-valued logic](guides/polars-004.md) | beginner | Explain how missingness changes a specific calculation. |
| [polars-005: Aggregation grain and weighted quantities](guides/polars-005.md) | beginner | Build an aggregate whose numerator, denominator and weighting unit are explicit. |
| [polars-006: Joins, cardinality and reconciliation](guides/polars-006.md) | beginner | Enrich a fact table while proving its grain and totals remain valid. |
| [polars-007: Time zones, elapsed time and interval boundaries](guides/polars-007.md) | intermediate | Define time semantics before aggregating a dataset. |
| [polars-008: Reshaping while preserving identity](guides/polars-008.md) | intermediate | Reshape a repeated-measurement dataset with a checked compound key. |
| [polars-009: Ordered windows and row-preserving statistics](guides/polars-009.md) | intermediate | Create row-preserving historical features with explicit ordering. |
| [polars-010: Lazy plans and optimizer reasoning](guides/polars-010.md) | intermediate | Explain a lazy query in terms of its requested result and observable execution plan. |
| [polars-011: Files, schema boundaries and columnar artifacts](guides/polars-011.md) | intermediate | Publish a small typed artifact with independently checked readback. |
| [polars-012: Arrow interoperability and categorical meaning](guides/polars-012.md) | intermediate | Move a typed table across an Arrow boundary while preserving its logical contract. |
| [polars-013: Nested data, lists and structs](guides/polars-013.md) | advanced | Normalize nested events with an explicit population and identity contract. |
| [polars-014: As-of joins and knowledge available at prediction time](guides/polars-014.md) | advanced | Reconstruct features using only information eligible at each prediction time. |
| [polars-015: Streaming execution and bounded output](guides/polars-015.md) | advanced | Evaluate a query under an explicit engine and resource contract. |
| [polars-016: Native expressions and the boundary of Python UDFs](guides/polars-016.md) | advanced | Use a Python UDF only with an explicit value, type and batching contract. |
| [polars-017: Performance measurements with correctness controls](guides/polars-017.md) | advanced | Produce a reviewable performance comparison with a correctness oracle. |
| [polars-018: A validated event-to-feature publication](guides/polars-018.md) | advanced | Publish a feature artifact with explicit derivation and consumption contracts. |

## Authoring

Maintained prose is in `authoring/units.json`; complete programs are in `references/`. Run `python authoring/build.py` from this directory, or use `--check` to detect drift. The three related data courses share `courses/ml-engineering/authoring/publish.py`. Keep the full repository when using the authoring tools. The shared readers are generated separately.
