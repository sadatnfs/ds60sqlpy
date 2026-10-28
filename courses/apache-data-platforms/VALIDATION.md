# Apache course validation boundaries

The course remains unadmitted until all 88 developed units and their runtime
contracts exist. A design row, image manifest or successful import is not a
completed service qualification.

## Prepared libraries

Actual native Linux ARM64 Docker execution has checked the developed Python
references for Arrow, DataFusion and PyIceberg. The image uses Arrow 23.0.1,
DataFusion Python 55.0.0 and PyIceberg 0.12.0. Checks include independent fixture
identities and sums, SQL null/cardinality behavior, typed UDFs, bounded session
settings, retained snapshots, field-ID renames, partition evolution, rejected
stale schema commits and metadata expiration without physical cleanup claims.

The SQL catalog's logical name is part of its identity. Reopening a SQLite file
under another name is not an alias for the existing catalog. The cross-engine
example explicitly materializes PyIceberg output as Arrow before DataFusion
queries it; it does not claim a direct Hive or REST catalog integration.

## Arrow Flight and IPC

The actual local Docker topology passed exact reads, unknown descriptors and
three invalid ticket forms, exact retained-container resume and replacement over
retained fixture storage. The client namespace probe resolved the real service
name and required failure when the separate client addressed its own loopback.
The Python Arrow 23 -> Rust Arrow 60 -> Python IPC bridge compiled offline against
the prepared Rust image and preserved exact primitive schema, values and nulls.

These checks do not prove authentication, arbitrary schema interoperability,
zero copies at every boundary, replication or availability during a single-server
outage. No host service port is published by the Flight fixture.

## Kafka

The explicit official-binary route passed native Linux ARM64 positive, negative,
repeat-initialization, exact-resume and retained-volume replacement checks.
Transaction readback distinguished three committed records from four uncommitted
records, including one aborted payload. Separate identical application send calls
remained distinct. Consumer checks observed replay before commit, retained next
offsets, no replay after commit and full reads for an independent group.

The compaction fixture verifies the real topic policy and observed log updates;
it explicitly does not claim completed physical compaction. The JSON validator
is an application reader, not a schema registry. Consumer assignment is manual,
so the current probe does not claim an actual coordinator rebalance experiment.
The topology has one broker/controller and no high availability.

## Remaining acceptance

Native AMD64 runtime execution is separate from published multiarch descriptors.
Ballista, Airflow, Flink, Cassandra, Pinot, Hive/Metastore, Atlas and Delta Sharing
require their own actual project qualification. Incompatible optional clients
remain isolated from the ordinary library runtime. Unsupported architectures
must fail before build/pull and explain the separately supported native or
portable-client route, without automatic AMD64 emulation on ARM.
