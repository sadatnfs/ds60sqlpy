# apache-063: Warehouse, catalog and execution

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-003`, `apache-008`, `apache-039`.

## Key terms

- **HiveServer2:** The Hive service that accepts SQL sessions from clients such as Beeline and runs queries on an execution engine.
- **Hive Metastore:** The service that stores metadata for databases, tables, columns, partitions and storage locations, without reading the data files themselves.
- **Warehouse:** The filesystem or object-store location holding a table's actual data files, separate from the Metastore records that describe them.
- **External table:** A Hive table whose data files live at a declared location that Hive does not own, so dropping the table leaves the files in place.
- **Beeline:** The JDBC command-line client used to open a HiveServer2 session and run SQL.

## Query service, metadata service and storage have different jobs

HiveServer2 accepts SQL sessions through its supported client protocol. The
Metastore describes databases, tables, columns, partitions, storage descriptors
and related metadata. A warehouse filesystem or object store holds the actual
files. A separate relational database can persist Metastore records. The word
Hive can refer to this ecosystem, so always name the component involved in a
failure or capability claim.

A Metastore response can identify a Parquet location without reading those
Parquet bytes. A query engine then needs its own storage access, format reader
and execution environment. Conversely, being able to list files does not prove
that a logical table exists in the intended catalog. These are separate paths
with independent authentication, network and compatibility requirements.

The [owned Hive project](../projects/hive/README.md) prepares Hive 4.2.1,
PostgreSQL-backed metadata, Beeline, an actual Java Thrift client and a bounded
Parquet warehouse. That release requires JDK 21. The source is an explicit
prepared route until its live acceptance ledger passes; image descriptors and
Java parsing alone are not Hive execution evidence.

## Worked case A: register an external table

The warehouse fixture has three orders in one day partition. CREATE EXTERNAL
TABLE declares id, region and amount, a separate day partition column, Parquet
storage and a file URI. ADD PARTITION associates the day value with its actual
location. The resulting table is a logical description over existing bytes, not
a conversion of arbitrary files into a transactional format.

The project's initialization script contains the complete registration:

From [`projects/hive/initialize.hql`](../projects/hive/initialize.hql):

```hql
CREATE DATABASE IF NOT EXISTS ds60 LOCATION 'file:///warehouse/ds60.db';
CREATE EXTERNAL TABLE IF NOT EXISTS ds60.orders (id INT, region STRING, amount INT)
PARTITIONED BY (day STRING) STORED AS PARQUET LOCATION 'file:///warehouse/orders';
ALTER TABLE ds60.orders ADD IF NOT EXISTS PARTITION (day='2026-01-01') LOCATION 'file:///warehouse/orders/day=2026-01-01';
```

The query oracle expects IDs 1/2/3 with amounts 4/9/7 and regional totals 11 and 9.
Record the table's exact database, name, type and location beside that result.
An identically named table in a different Metastore can point somewhere else.
A client connecting to an embedded local catalog by mistake can therefore see
an empty namespace while the intended remote catalog remains intact.

External and managed table lifecycle rules can differ, including configured
purge behavior and release-specific properties. Do not assume dropping an external
table is always harmless to its files. Read the selected table properties and
storage policy before any destructive DDL. The tutorial's check operations read
existing state and do not drop tables or reset the warehouse.

## Worked case B: inspect metadata without querying data

The separate MetadataProbe.java constructs HiveMetaStoreClient with the explicit
Thrift service URI and asks for ds60.orders. It checks external-table type,
three physical columns, one partition key and one registered partition. A missing
owned table must raise the actual missing-object condition. This independent
client does not use Beeline or scan Parquet.

Now compare that response with the actual HiveServer2 row query. Metadata success
and SQL success establish different boundaries. If metadata is correct but the
query cannot read a location, investigate the engine's filesystem permissions,
URI interpretation and format dependencies. Recreating the catalog would be an
unjustified response to a data-plane access failure.

The local fixture mounts the same owned warehouse at the same absolute container
path for the relevant clients. A path meaningful only inside one container is
not a portable distributed storage URI. An object-store integration needs its
own endpoint, credentials, supported filesystem implementation and execution
qualification, rather than a host-path substitution in a catalog record.

## Diagnosis and interview discussion

Draw the client-to-HiveServer2, engine-to-Metastore, Metastore-to-PostgreSQL and
engine-to-storage connections separately. Record which one failed and preserve
its diagnostic. A healthy database socket does not prove a compatible Metastore
schema, and a healthy Thrift socket does not prove query execution or file access.

**Interview discussion: why does a catalog entry not prove a table is readable?**
It supplies metadata while actual data access belongs to the query engine and
storage path. These cases first register a bounded external contract, then inspect
that metadata independently so a failure can be attributed to the correct layer.

## Worked examples

### Register an external table and one partition

```sql
CREATE DATABASE IF NOT EXISTS ds60 LOCATION 'file:///warehouse/ds60.db';

CREATE EXTERNAL TABLE IF NOT EXISTS ds60.orders (id INT, region STRING, amount INT)
PARTITIONED BY (day STRING)
STORED AS PARQUET
LOCATION 'file:///warehouse/orders';

ALTER TABLE ds60.orders ADD IF NOT EXISTS PARTITION (day = '2026-01-01')
LOCATION 'file:///warehouse/orders/day=2026-01-01';
```

These statements from initialize.hql only write metadata to the PostgreSQL-backed metastore; no Parquet file is read or created. EXTERNAL means dropping the table later removes the definition but leaves the files. Partitions are not discovered automatically, so a new day directory stays invisible to queries until ALTER TABLE ADD PARTITION or MSCK REPAIR TABLE registers it.

### Read metadata through Thrift without Beeline

```java
Table table = client.getTable("ds60", "orders");
Partition partition = client.getPartition("ds60", "orders", List.of("2026-01-01"));
System.out.println(table.getSd().getLocation());
System.out.println(partition.getSd().getLocation());
```

This simplified fragment from MetadataProbe.java talks directly to the metastore, so it works even when HiveServer2 is down. It should print file:/warehouse/orders and file:/warehouse/orders/day=2026-01-01. The probe also asks for a table that does not exist and expects an error, which shows the metastore answers truthfully rather than with a default. Seeing the right locations here while a Beeline query fails narrows the problem to HiveServer2 or the files, not the catalog.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Hive apache-063 command notebook

Run from the copied owned Hive project, following its README. Native service
acceptance is separately recorded in QUALIFICATION.md.

```bash
bash run.sh prepare
bash run.sh start-db
bash run.sh initialize-schema
bash run.sh start
bash run.sh initialize
bash run.sh check
bash run.sh metadata
```

The metadata probe reads actual Thrift table/partition metadata independently from Beeline and data files.

The classroom does not execute these Docker commands. Retain source, schema,
file identities, actual responses and failure scope in an independent receipt.

## Primary references

- [Hive4.2.1 preparation and components](https://hive.apache.org/development/quickstart/)
- [Hive DDL](https://hive.apache.org/docs/latest/language/languagemanual-ddl/)
- [Hive Metastore administration](https://hive.apache.org/docs/latest/admin/adminmanual-metastore-administration/)
- [Hive/Iceberg integration](https://iceberg.apache.org/docs/latest/hive/)
- [Pinned schema tool source](https://github.com/apache/hive/tree/rel/release-4.2.1/standalone-metastore/metastore-server/src/main/java/org/apache/hadoop/hive/metastore/tools/schematool)
