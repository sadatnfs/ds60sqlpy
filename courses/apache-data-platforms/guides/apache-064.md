# apache-064: Schemas, partitions and serialization

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-063`.

## Key terms

- **Storage descriptor:** The Metastore record that ties a table's columns to a file format, input and output classes, SerDe and location.
- **SerDe:** Serializer and deserializer, the component that translates between stored bytes and Hive column values.
- **Partition registration:** Adding a partition value and its location to the Metastore, for example with ALTER TABLE ADD PARTITION. Creating a directory alone does not register it.
- **Physical schema:** The column names and types actually written in the Parquet files, which must stay compatible with the catalog's declared types.

## A table schema interprets physical bytes

Hive's storage descriptor connects logical columns with a file format, input and
output implementation, serialization/deserialization rules and a location.
SerDe means serializer/deserializer: the component translating between stored
representations and engine values. Parquet also carries a physical schema, so
logical declarations must remain compatible with the actual files and reader.
A catalog type name does not rewrite existing bytes.

Partition columns are often represented in directory names and catalog values
rather than repeated in each file. Registering a partition tells the engine
which location corresponds to a logical value. Merely creating a directory does
not always register it, and registering a location does not establish that the
files contain the expected rows. Partition discovery is an operational choice
with its own scope and safety requirements.

The prepared owned fixture creates int32 id and amount fields and a string
region in Parquet. It uses an explicit UTC day partition. Matching those details
between fixture writer, catalog declaration and query is essential. A local
three-column read does not establish compatibility for every decimal, timestamp,
collection or schema-evolution feature.

## Worked case A: register one day and project columns

Create the external table over the warehouse/orders root, then add the single
known day partition pointing to warehouse/orders/day=2026-01-01. Query that
partition and select id, region and amount. The independent oracle returns the
three known rows in ID order. Querying the day column should yield the registered
partition value even though it is not stored as a primitive column in each file.

Partition pruning can reduce eligible locations when a compatible predicate
constrains day. Column projection can reduce what a columnar reader must access.
These mechanisms operate at different levels. An explain plan showing one
partition does not prove that only selected physical columns were read, and a
small returned table does not establish either optimization by itself.

Use explicit locations in this fixture rather than an unrestricted discovery
command against a valuable warehouse. A directory scan can encounter incomplete,
foreign or stale partitions. Decide which naming, completeness and ownership
rules make a directory eligible before turning discovery into recurring
publication behavior.

## Worked case B: a wrong declaration changes the result contract

Prepare a separately named experimental table over a copied owned location with
an intentionally incompatible field type. Run a bounded query and retain the
actual reader or conversion failure. Some format/type combinations may instead
produce nulls or supported conversions, so the negative oracle must match the
pinned implementation rather than assuming every mismatch throws the same error.

A second controlled mismatch points a registered partition at a known empty
owned directory. An empty query can be a valid consequence of that location;
it is not evidence that the original file disappeared. Compare catalog location,
file listing and expected identity set before modifying any data. Wrong location
and wrong type are different failures even when both yield missing values.

For a schema change, decide whether the operation alters only metadata, rewrites
files or uses a table format with stable field identity. Renaming a column in
plain external-table metadata is not automatically equivalent to Iceberg field-ID
rename semantics. Mixing those mental models can silently associate old bytes
with the wrong business meaning.

## Diagnosis and interview discussion

Inspect DESCRIBE output, partition values and locations, physical Parquet schema,
reader implementation and actual exceptions. Keep string dates, UTC timestamps
and epoch units explicit. Preserve the original valid table while testing wrong
schemas under a distinct owned name, then remove only the experimental resources
when their evidence has been retained.

**Interview discussion: why can a directory exist but a partition query return no
rows?** The catalog may not register it, may point elsewhere, or may interpret
its contents differently. The two cases connect logical registration to physical
schema and location, without treating file discovery as a transactional commit.

## Worked examples

### Generate the Parquet file for one day

```python
import pyarrow as pa
import pyarrow.parquet as pq

table = pa.table(
    {
        "id": pa.array([1, 2, 3], pa.int32()),
        "region": ["east", "west", "east"],
        "amount": pa.array([4, 9, 7], pa.int32()),
    }
)
sink = pa.BufferOutputStream()
pq.write_table(table, sink)
print(pq.read_schema(pa.BufferReader(sink.getvalue())))
```

```text
id: int32
region: string
amount: int32
```

The printed schema shows id and amount as int32 and region as string, which match INT and STRING in the Hive declaration. The day column is absent on purpose: Hive derives it from the directory name day=2026-01-01, not from the file. If the file were written with int64 columns, a reader expecting INT can fail or convert depending on the engine version, which is why the schema should be inspected before blaming the query.

### Project from the registered day

```sql
SELECT
  region,
  SUM(amount)
FROM
  ds60.orders
WHERE
  day = '2026-01-01'
GROUP BY
  region
ORDER BY
  region;
```

From explain.sql, this should return east 11 and west 9. The EXPLAIN version of the same query shows the partition filter applied before the scan, so only one directory is read. Two different failures look alike here: a missing partition returns zero rows with no error, while a wrong column type in a separately named table produces a reader error or nulls. Record which one you saw before changing anything, because the fixes are different.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Hive apache-064 command notebook

Run from the copied owned Hive project, following its README. Native service
acceptance is separately recorded in QUALIFICATION.md.

```bash
cat initialize.hql
cat fixture.py
bash run.sh check
bash run.sh metadata
```

Use separately named copied-owned tables for wrong-type and wrong-location experiments. Record the actual reader response; an empty location and an incompatible schema are different conditions.

The classroom does not execute these Docker commands. Retain source, schema,
file identities, actual responses and failure scope in an independent receipt.

## Primary references

- [Hive4.2.1 preparation and components](https://hive.apache.org/development/quickstart/)
- [Hive DDL](https://hive.apache.org/docs/latest/language/languagemanual-ddl/)
- [Hive Metastore administration](https://hive.apache.org/docs/latest/admin/adminmanual-metastore-administration/)
- [Hive/Iceberg integration](https://iceberg.apache.org/docs/latest/hive/)
- [Pinned schema tool source](https://github.com/apache/hive/tree/rel/release-4.2.1/standalone-metastore/metastore-server/src/main/java/org/apache/hadoop/hive/metastore/tools/schematool)
