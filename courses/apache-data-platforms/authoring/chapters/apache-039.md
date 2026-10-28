## A table is a committed view of files

A directory of Parquet objects does not by itself say which files form a table,
which schema applies, or which concurrent update won. Iceberg adds metadata that
identifies table state and the data files belonging to each snapshot. A catalog
locates the current table metadata and supplies the commit boundary used by its
writers. The warehouse contains data and metadata files; the catalog's pointer
and the warehouse's bytes are related but different responsibilities.

A snapshot is a committed table state, not a full byte-for-byte copy of every
file. Immutable data files can be reused across snapshots. Snapshot metadata
references manifest lists and manifests, which describe data and delete files
and statistics. This indirection supports evolution and planning, but also means
that deleting an apparently old file by hand can break a still-retained snapshot.
Always use the table's supported maintenance mechanisms and retention policy.

The complete program uses real PyIceberg with a local SQLite catalog and a
temporary warehouse. It performs actual file writes and catalog commits. This
single-process fixture does not stand in for a remote Hive Metastore, REST
catalog, distributed lock service or cloud object store. Those components have
additional configuration and failure boundaries studied in the project workshops.

## Worked case A: create, append and inspect

The first append commits three orders with amounts 4, 9 and 7. The program records
the current snapshot identifier and checks exact order identities plus total 20.
A snapshot identifier is an opaque table identity, not an increasing row count
or a timestamp that should be invented by a caller. Capture the actual identifier
returned by the table after commit.

The fixture inspects planned files and verifies that each referenced data file
exists. That connects logical table state to physical storage without assuming
that every object beneath the warehouse is live table data. It also checks the
schema and records the catalog type. A visible file alone is insufficient to
claim it was committed; a catalog entry alone is insufficient if the referenced
bytes were lost or became inaccessible.

Appending does not impose row ordering. The program sorts by order ID before
comparison, because a scan may enumerate manifests and files in a different order
from application insertion. An analytical consumer that requires ordering must
request it explicitly after scan. The same principle holds when another engine
reads this table through a compatible integration.

## Worked case B: retain the first snapshot after another append

A second append adds order 4 with amount 2. The current state now has four orders
and total 22. Reading with the recorded first snapshot still returns three orders
and total 20. The program asserts both results independently. This is real local
time travel over retained metadata and files, not a copied Python list presented
as an Iceberg history mechanism.

Reopening the same named catalog and table establishes that the committed pointer survives
the original table handle. It does not prove the state survives deletion of the
SQLite database or warehouse. The SQL catalog name is also part of its identity: using a different name in the
same SQLite database selects a different logical catalog, rather than an alias.
Both database and warehouse must be retained together in a persistent
project. Copying only the source code to another machine does not migrate its
catalog or data volume.

Snapshot selection must be captured in a report or training-data receipt if exact
reproduction matters. A query against the current table can change after another
append, even though its SQL is identical. Conversely, a retained snapshot is not
a promise of indefinite retention: an authorized expiration policy can later
remove its reference and permit physical cleanup.

## Diagnosis and interview discussion

Check table identity, catalog configuration, metadata location, current snapshot
and storage accessibility separately. A file-not-found error can mean missing
warehouse bytes rather than a corrupt SQL query. A table-not-found error can mean
the client is connected to the wrong catalog, even if similarly named files exist.
Do not repair either by automatically creating a new empty table over the path.

**Interview discussion: why use Iceberg if Parquet already stores typed columns?**
Parquet describes a file. Iceberg describes a versioned table made of files,
including commits, schema identity, partition specifications and retained history.
These cases show the actual extra contract: one current committed view and an
independently selectable earlier snapshot, both pointing to real local files.
