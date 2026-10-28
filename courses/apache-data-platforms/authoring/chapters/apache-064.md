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
