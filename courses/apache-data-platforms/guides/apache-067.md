# apache-067: Transactional tables and Iceberg integration

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-066`, `apache-063`.

## Key terms

- **Hive ACID table:** A transactional managed table that uses write IDs, delta directories and compaction to support insert, update and delete.
- **Write ID:** The identifier Hive assigns to each transactional write so readers can determine which deltas are visible.
- **Iceberg storage handler:** The Hive 4 integration that lets Hive create and query Iceberg tables through Iceberg's snapshot commit protocol.
- **Reader compatibility:** Whether a given engine can correctly read a table's transaction protocol, file layout and delete representation.

## A catalog does not choose a transaction protocol for every table

Hive can describe tables with different storage and transaction mechanisms.
Traditional Hive transactional tables coordinate write IDs, visibility and
compaction through their supported ACID machinery. Iceberg tables use a table
metadata/snapshot commit protocol and stable schema identity. Both can appear
under familiar SQL names while offering different files, operations and reader
requirements.

A plain Parquet external table has neither protocol merely because the files
are columnar. Updating a directory and changing catalog metadata are not a
substitute for an atomic table commit. Choose the required transaction and
concurrency behavior first, then prepare compatible writers, catalog and readers.
A successful SELECT over primitive columns exercises a narrow subset of that
compatibility surface.

Hive 4.2 includes its own documented Iceberg integration. The prepared iceberg.hql
uses that release's storage-handler syntax in a separately named owned table.
It remains an explicit extension with an independent acceptance requirement.
The ordinary PyIceberg SQLite-catalog examples and the default external Parquet
workshop do not establish direct shared HiveCatalog interoperability.

## Worked case A: compare two commit narratives

Consider a Hive ACID update of one order versus an Iceberg append creating a new
snapshot. Identify the metadata that tells a reader which records are visible,
which files are authoritative, and what compaction or maintenance means. Save
the selected table properties and actual transaction/snapshot metadata from the
chosen real experiment rather than drawing both mechanisms as one generic log.

For the Iceberg path, record a snapshot before and after a bounded append and
read the earlier state through a supported time-travel operation. The earlier
snapshot should retain its original rows while the current table adds the new
row. An arbitrary listing of all Parquet files can include old and current files
and therefore answer a different question.

For an ACID path, use only the selected release's supported transactional table
configuration and operations. Explain its compactor and reader obligations.
Do not issue an update against the plain external Parquet fixture and then call
an unrelated syntax or format failure a demonstration of transaction isolation.
The negative case must match the specific contract being investigated.

## Worked case B: read a compatible Iceberg table

Prepare the separate table with the pinned Hive integration, insert the three
known orders and require exact ID/value readback. Inspect its catalog entry,
metadata location, schema and snapshot. If another engine participates, record
its exact connector and selected snapshot rather than assuming common Parquet
support is sufficient.

The prepared extension's statements are in the project. Running them is a separate
prepared step with its own acceptance receipt, not part of the default check:

From [`projects/hive/iceberg.hql`](../projects/hive/iceberg.hql):

```sql
-- Prepared extension, separate table and acceptance receipt required.
CREATE EXTERNAL TABLE ds60.orders_iceberg (id INT, region STRING, amount INT)
STORED BY ICEBERG LOCATION 'file:///warehouse/orders_iceberg';
INSERT INTO ds60.orders_iceberg VALUES (1, 'east', 4), (2, 'west', 9), (3, 'east', 7);
SELECT * FROM ds60.orders_iceberg ORDER BY id;
```

`STORED BY ICEBERG` hands the table's metadata and snapshots to the Iceberg storage
handler, so the `INSERT` creates a new Iceberg snapshot rather than a new Hive
partition directory.

Schema evolution, partition evolution, equality/position deletes and newer table
features can expose compatibility limits absent from a primitive scan. Select
one changed condition, such as a field rename or an actual supported delete,
and verify it through both chosen readers. An engine that ignores a delete file
can return plausible but incorrect extra rows.

Metadata ownership also matters during drop and cleanup. A catalog operation
can remove a pointer while files remain, or a purge option can delete data needed
by retained snapshots and readers. Use documented maintenance procedures and
retention policies. Never delete apparently orphaned files from a shared warehouse
based solely on a directory listing.

## Diagnosis and interview discussion

Record table type, properties, format version, writer/reader versions, catalog
identity, transaction or snapshot identity and actual changed-condition results.
Separate a metadata protocol error from a storage-access or unsupported-feature
failure. Preserve the original table before experimenting with migrations.

**Interview discussion: does storing a table in Hive Metastore make every reader
transactionally compatible?** No. The catalog identifies metadata while readers
must implement the table's actual visibility and commit protocol. These cases
compare the mechanisms and require a tested integration rather than equating a
shared table name with shared semantics.

## Worked examples

### Declare an Iceberg table through Hive

```sql
CREATE EXTERNAL TABLE ds60.orders_iceberg (id INT, region STRING, amount INT)
STORED BY ICEBERG
LOCATION 'file:///warehouse/orders_iceberg';

INSERT INTO ds60.orders_iceberg
VALUES
  (1, 'east', 4),
  (2, 'west', 9),
  (3, 'east', 7);
```

From the prepared iceberg.hql, STORED BY ICEBERG means commits go through Iceberg metadata files and a pointer swap, not through Hive ACID delta directories. The Hive metastore stores only the table name and the current metadata_location property. After the insert, a metadata JSON and a snapshot should appear under the table location; if only data files appear, the Iceberg handler was not active and the result is not an Iceberg table.

### Confirm a second reader sees the same snapshot

```python
table = catalog.load_table("ds60.orders_iceberg")
snapshot = table.current_snapshot()
print(snapshot.snapshot_id, table.metadata_location)
print(sorted(table.scan().to_arrow()["id"].to_pylist()))
```

This PyIceberg fragment assumes a catalog object already configured against the same Hive metastore. A compatible second reader should print the same metadata_location that Hive stored and the IDs [1, 2, 3]. Matching rows with a different metadata location means the reader used another catalog or a stale pointer. Treat this as a prepared extension until both readers have actually run against the owned table.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Hive apache-067 command notebook

Run from the copied owned Hive project, following its README. Native service
acceptance is separately recorded in QUALIFICATION.md.

```bash
cat iceberg.hql
cat conf/hive-site.xml
```

This is a prepared Iceberg extension, not an executed default reference. Prepare and test the exact bundled Hive integration, metadata/snapshot identity and second reader before asserting cross-engine compatibility.

The classroom does not execute these Docker commands. Retain source, schema,
file identities, actual responses and failure scope in an independent receipt.

## Primary references

- [Hive4.2.1 preparation and components](https://hive.apache.org/development/quickstart/)
- [Hive DDL](https://hive.apache.org/docs/latest/language/languagemanual-ddl/)
- [Hive Metastore administration](https://hive.apache.org/docs/latest/admin/adminmanual-metastore-administration/)
- [Hive/Iceberg integration](https://iceberg.apache.org/docs/latest/hive/)
- [Pinned schema tool source](https://github.com/apache/hive/tree/rel/release-4.2.1/standalone-metastore/metastore-server/src/main/java/org/apache/hadoop/hive/metastore/tools/schematool)
