# dbt and analytics engineering

A complete SQL-first route from real Core/DuckDB project files through tests, macros, snapshots, incremental correctness, contracts, documentation, targets, state/defer CI, governance and accepted data-product recovery.

Start from the [main Docker instructions](../../README.md). Select this subject in the shared classroom. This path uses the prepared `data-engineering` worker and requires no host compiler or account. All examples use local synthetic inputs after image preparation.

## Route

| Lesson | Stage | Outcome |
| --- | --- | --- |
| [dbt-001: A real dbt project and its execution stages](guides/dbt-001.md) | beginner | Build and inspect a local dbt project through its real adapter. |
| [dbt-002: Seeds, staging and rejected records](guides/dbt-002.md) | beginner | Create a staging boundary with complete record accounting. |
| [dbt-003: Dependency graphs and materialization choices](guides/dbt-003.md) | beginner | Choose a materialization using observed database behavior and a stated workload. |
| [dbt-004: Data tests and the meaning of a failed build](guides/dbt-004.md) | beginner | Use data tests as explicit evidence for a declared contract. |
| [dbt-005: Source freshness and clock assumptions](guides/dbt-005.md) | beginner | Define and test a source freshness policy with an explicit clock and response. |
| [dbt-006: Unit fixtures and integration tests](guides/dbt-006.md) | beginner | Use controlled fixtures to test transformation logic and real-data checks to test integration. |
| [dbt-007: Jinja macros and compiled SQL evidence](guides/dbt-007.md) | intermediate | Review a macro through its source, emitted SQL and actual result. |
| [dbt-008: Incremental watermarks and late-arriving records](guides/dbt-008.md) | intermediate | State the assumptions under which an incremental result equals a full recomputation. |
| [dbt-009: Keyed updates, lookback windows and idempotency](guides/dbt-009.md) | intermediate | Implement a keyed incremental contract with tested boundary and repeat-run behavior. |
| [dbt-010: Snapshots and observed historical state](guides/dbt-010.md) | intermediate | Explain what a snapshot actually observed and what it cannot reconstruct. |
| [dbt-011: Enforced model schemas and constraint boundaries](guides/dbt-011.md) | intermediate | Define a model schema contract and verify both accepted and rejected changes. |
| [dbt-012: Model versions and semantic compatibility](guides/dbt-012.md) | intermediate | Manage a semantic model change with explicit consumer versioning. |
| [dbt-013: Selectors, graph expansion and state comparison](guides/dbt-013.md) | advanced | Construct and inspect a reproducible selection against an explicit baseline. |
| [dbt-014: Documentation, catalogs, exposures and ownership](guides/dbt-014.md) | advanced | Build documentation that joins observed structure with authored meaning and ownership. |
| [dbt-015: Publication gates after materialization](guides/dbt-015.md) | advanced | Separate candidate computation from accepted publication. |
| [dbt-016: Metric contracts and valid denominators](guides/dbt-016.md) | advanced | Publish a metric with a complete numerator/denominator contract and an independent check. |
| [dbt-017: Temporal data products and late-known facts](guides/dbt-017.md) | advanced | Produce a historical feature relation with explicit entity, time and version semantics. |
| [dbt-018: Local packages and reusable project dependencies](guides/dbt-018.md) | advanced | Prepare and inspect a real reusable dbt dependency with an explicit source boundary. |
| [dbt-019: Targets, environments and owned database routing](guides/dbt-019.md) | advanced | Run a project against an explicitly identified owned target and verify its actual destination. |
| [dbt-020: Deferral and the choice of upstream state](guides/dbt-020.md) | advanced | Use deferral with an explicit upstream-state contract. |
| [dbt-021: Slim CI with actual builds and data tests](guides/dbt-021.md) | advanced | Implement a reproducible reduced CI workflow with explicit selection, baseline and ownership. |
| [dbt-022: Diagnose template, database and semantic failures](guides/dbt-022.md) | advanced | Diagnose failures using the layer that actually rejected the work. |
| [dbt-023: Query plans, measured cost and semantic equivalence](guides/dbt-023.md) | advanced | Measure database work with a correctness oracle and a clearly defined interval. |
| [dbt-024: Groups, model access and governance boundaries](guides/dbt-024.md) | advanced | Use groups and model access to define supported project interfaces, while keeping database authorization claims separate. |
| [dbt-025: Recovery, accepted versions and atomic pointers](guides/dbt-025.md) | advanced | Recover a data product through explicit accepted versions and a tested pointer mechanism. |
| [dbt-026: Publish a complete validated analytics product](guides/dbt-026.md) | advanced | Deliver a complete local analytics product with a reviewable acceptance decision. |

## Authoring

Maintained prose is in `authoring/units.json`; complete programs are in `references/`. Run `python authoring/build.py` from this directory, or use `--check` to detect drift. The three related data courses share `courses/ml-engineering/authoring/publish.py`. Keep the full repository when using the authoring tools. The shared readers are generated separately.

## Complete local project

The maintained retail project contains actual SQL models, seeds, macros, local packages, tests, snapshots and target configuration. Copy it to an owned working directory and use its Docker launcher to inspect durable artifacts and evolve a complete project.

Follow the [complete project instructions](projects/retail/README.md).
