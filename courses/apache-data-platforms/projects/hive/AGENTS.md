# Hive/Metastore workshop

Use actual Hive 4.2.1/JDK 21 and PostgreSQL, with schema initialization explicit.
Never inherit the upstream automatic initOrUpgradeSchema path on ordinary resume.
Preserve metadata and warehouse volumes, and compare independent Thrift metadata
with actual HiveServer2 query output. Iceberg compatibility and ACID operations
need separate evidence. Native descriptor availability is not acceptance. Do not
use emulation, shared databases, ambient credentials, global prune or publication.


Preparation shares the normal lifecycle lock and has an atomic preparation lock.
Keep one canonical bounded identity.tsv for source/class/Hive/JDK image identities.
Runtime checks that same identity, not separate hash sidecars. Both temporary
classpath and compiler/verifier containers have exact owner/kind/role labels and
inspected immutable image IDs. Reap a known running compiler before clearing its
stage; retain unknown ownership/state for reconciliation. No accepted class may
hide a leftover preparation owner. Never auto-replay an uncertain preparation.

The typed Thrift oracle must reject wrong column names/types, partition key/type,
value or location even when cardinalities match. Opening a lesson downloads no
packages. Ordinary resume and readback never initialize schema or fixtures.
