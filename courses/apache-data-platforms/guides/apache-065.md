# apache-065: Metastore durability and clients

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-064`, `apache-063`.

## Metastore availability and metadata durability are separate

A remote Metastore service exposes metadata operations while PostgreSQL persists
its relational state. Restarting the Thrift process can preserve tables because
the database remains. Removing a disposable container can also preserve tables
when its database volume is retained. Neither outcome implies that deleting the
volume or losing the physical disk is recoverable without a backup.

A client library must be compatible with the selected service. Shared protocol
names do not guarantee every method, field or optional feature interoperates
across arbitrary releases. The prepared Java client comes from the same Hive
image as the server to keep that first boundary explicit. A separately prepared
PyIceberg HiveCatalog or Spark client needs its own matching dependencies and
actual exchange before being described as supported.

PostgreSQL schema initialization is an explicit project action. Ordinary startup
verifies the stored schema version instead of automatically upgrading it.
Database connectivity, schema compatibility and application readiness are three
different observations. An open PostgreSQL port can coexist with a missing or
incompatible Metastore schema.

## Worked case A: persist metadata in PostgreSQL

Start only the owned PostgreSQL service, initialize the fresh Metastore schema
once, verify its version, and then start the Metastore and HiveServer2. Initialize
the bounded external table separately. Capture the database/table/partition
metadata and the independent row query before touching lifecycle operations.
The fixture credentials apply only to this isolated local synthetic project.

The database data directory lives in a named owned volume. The warehouse has a
separate volume because metadata and data bytes have different lifecycles.
Retaining the former while discarding the latter can leave a valid catalog entry
whose files are absent. Retaining only the warehouse can leave useful Parquet
bytes with no record of the logical table definition.

A consistent recovery plan identifies both state sets, their relation and the
publication boundary. If a table format stores an authoritative metadata pointer,
that pointer also belongs in the backup story. Copying a directory of data files
while commits continue can produce a set that never represented one valid table
state, even when every copied file is individually readable.

## Worked case B: query from a fresh metadata client after restart

Stop and resume the exact owned services, then run a fresh Java Thrift client.
It should see the same external table and partition without recreating them.
Run the Beeline query separately and compare the original rows. A fresh client
avoids mistaking a previously cached in-process object for a successful remote
metadata exchange.

Next remove containers/network with down, retain both volumes, start replacement
containers and repeat only read-only checks. Do not call initialize-schema or
initialize during this readback. If the schema or table is absent, report the
failure. Automatic reconstruction would turn a persistence test into a different
experiment and conceal lost state.

Multiple Metastore service instances can share a suitable durable database under
a reviewed deployment design, but that requires connection capacity, locking,
version compatibility and actual failover checks. One retained local database
and one Thrift process do not qualify high availability or protect against the
single Docker engine's failure domain.

## Diagnosis and interview discussion

Record the client URI, server/client versions, schema version, database identity,
volume ownership and table metadata. Distinguish a failed connection from missing
schema, wrong catalog/database and unsupported protocol behavior. Retrying an
invalid endpoint or schema cannot repair the underlying contract and may hide
useful first-failure diagnostics.

**Interview discussion: does a stateless Metastore process mean metadata needs no
backup?** No. Process state can be replaceable while its backing database remains
authoritative. These cases preserve PostgreSQL metadata and warehouse bytes
separately, then require independent fresh-client readback after exact resume
and replacement.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Hive apache-065 command notebook

Run from the copied owned Hive project, following its README. Native service
acceptance is separately recorded in QUALIFICATION.md.

```bash
bash run.sh metadata
bash run.sh stop
bash run.sh resume
bash run.sh metadata
bash run.sh check
```

For replacement, use down/start then only check/metadata. Never initialize while testing retention. Compare database and warehouse ownership separately.

The classroom does not execute these Docker commands. Retain source, schema,
file identities, actual responses and failure scope in an independent receipt.

## Primary references

- [Hive4.2.1 preparation and components](https://hive.apache.org/development/quickstart/)
- [Hive DDL](https://hive.apache.org/docs/latest/language/languagemanual-ddl/)
- [Hive Metastore administration](https://hive.apache.org/docs/latest/admin/adminmanual-metastore-administration/)
- [Hive/Iceberg integration](https://iceberg.apache.org/docs/latest/hive/)
- [Pinned schema tool source](https://github.com/apache/hive/tree/rel/release-4.2.1/standalone-metastore/metastore-server/src/main/java/org/apache/hadoop/hive/metastore/tools/schematool)
