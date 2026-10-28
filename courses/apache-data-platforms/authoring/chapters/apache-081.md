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
