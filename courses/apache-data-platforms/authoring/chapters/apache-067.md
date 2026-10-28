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
