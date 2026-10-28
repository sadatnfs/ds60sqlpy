# apache-081: Batch lakehouse with reproducible snapshots

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-020`, `apache-044`.

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

Append a fourth west order with amount2 and capture the new snapshot. The old
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

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Integration apache-081 complete worked notebook

Run the actual bounded PyIceberg/Arrow/DataFusion program in the prepared Python profile. Retain old/new snapshot and materialization identities. A Spark read is a separately prepared connector/export path.

## Receipt fields and independent oracle

- Source revision/hashes and exact declared input IDs, values, schema and time units.
- Actual native platform, package/image identities and owned resource namespace.
- Selected table snapshot/version, source positions or process/lineage identity as appropriate.
- Positive result against an independent oracle and a typed negative observation.
- Read-only retained-state comparison after the selected lifecycle transition.
- Cleanup/evidence-storage result and any separate prepared or unavailable feature.

For the common three-order fixture, require IDs 1/2/3 with amounts 4/9/7, total 20,
east 11 and west 9. A later fourth west order of2changes current total to22 and west
to11while an earlier pinned snapshot remains unchanged. Do not use this simple
oracle to claim correctness for a different pipeline without defining its
deduplication, correction and visibility semantics.

Read the selected project README and qualification ledger before commands. The
classroom does not execute Docker commands in this Markdown pad. Prepared
configuration, unit policy fixtures, successful compilation and actual service
acceptance remain different observations. Never include credentials or signed URLs.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
mkdir -p .workshop
# From the copied integration project; use the complete Docker command in README.
cat batch_snapshot.py
cat README.md
```

These inspections do not start or qualify a service. Execute only the chosen
project's complete documented owned route and retain its actual receipt.

## Primary references

- [Iceberg reliability and table state](https://iceberg.apache.org/docs/latest/reliability/)
- [Arrow data format](https://arrow.apache.org/docs/format/Columnar.html)
- [Flink stateful stream processing](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/concepts/stateful-stream-processing/)
- [Kafka delivery/transaction design](https://kafka.apache.org/44/design/design/)
- [Atlas API and metadata boundaries](https://atlas.apache.org/api/v2/index.html)
- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
