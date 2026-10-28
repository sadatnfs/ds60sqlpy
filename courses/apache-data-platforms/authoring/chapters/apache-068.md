## A metadata upgrade changes durable state

The Metastore's relational schema is versioned independently from a container
name. Upgrading application binaries can require a schema migration, and rolling
back those binaries does not automatically reverse that migration. Plan an
upgrade around compatible clients, the exact database schema, stored metadata,
warehouse state and a tested restoration path.

The prepared workshop overrides the official image's automatic init-or-upgrade
entrypoint. Explicit initialize-schema is for a fresh disposable database;
verify-schema reads version information; ordinary startup verifies compatibility
before serving. This separation prevents a routine resume from silently becoming
a database migration. A missing schema should fail clearly instead of being
filled in during readback.

A backup must include enough information to reconstruct one intended state.
For metadata, that can include a consistent PostgreSQL dump, role/schema
requirements and version information. Warehouse and table-format metadata need
corresponding retention and transfer. A database dump alone cannot restore data
files that were lost from a separate volume or expired by an unrelated process.

## Worked case A: verify before startup

Start the owned database and run the pinned schematool information check. Record
the stored schema version and selected Hive release before starting the service.
A fresh uninitialized database must fail the information check. Only an explicit
initialization action may create its schema, after which verification is repeated.
This is an expected preparation transition, not an operational failure to hide.

For an existing project, compare the saved schema with the release's documented
compatibility and migration path. Do not infer support from a numerically close
version. Capture a known table, partition locations and exact row identities so
post-upgrade acceptance covers meaningful metadata and data access rather than
only a process returning healthy.

Client compatibility also belongs in the upgrade plan. A server upgrade can leave
an older external client outside the tested method/feature boundary. Keep a
representative second metadata client and SQL query in the acceptance dossier.
Do not declare success merely because the upgraded server's own command-line
tool can read its database.

## Worked case B: reject incompatibility and restore an owned copy

Take a consistent dump of the disposable metadata database and record its digest,
source version and table identity. Restore it into a separately owned database
copy before changing anything. Use the copy to test a deliberately incompatible
schema/version condition and require verification to fail before service startup.
Never edit a valuable Metastore VERSION row as a shortcut for this experiment.

Restore the known dump into another empty owned target with matching software,
then compare table names, schemas, partitions, metadata locations and actual query
rows. A successful restore command is weaker than these semantic checks. If the
warehouse is separately retained, confirm that its bytes and permissions still
match the catalog locations after the target starts.

Define a recovery point and acceptable downtime before scheduling a migration.
Writes occurring after a dump can make rollback lose newer metadata or refer to
files not represented in the backup. A maintenance window, dual-write policy or
other explicit cutover procedure must address that gap. The small local exercise
does not establish a universal online migration technique.

## Diagnosis and interview discussion

Retain the first schema failure, migration logs, dump identity, client/server
versions and post-restore semantic comparison. Distinguish configuration error,
unsupported schema, unavailable database and missing warehouse files. Automatic
initialization or broad volume deletion can erase the condition that makes the
failure explainable.

**Interview discussion: why is replacing an old container image insufficient for
rolling back a Metastore upgrade?** Durable database changes can outlive the
container and may be incompatible with the old binary. These cases require
preflight schema verification and an independently tested owned restoration path
before treating a migration as recoverable.
