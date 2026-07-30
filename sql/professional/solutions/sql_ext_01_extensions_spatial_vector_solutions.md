# SQL-EXT-01 Solutions — Extensions, Spatial, and Vector Boundaries

Run:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_ext_01_extensions_spatial_vector_solutions.sql
```

The solution uses only built-ins and rolls back.

## Exercise 1 — Capability matrix

Join a requested-extension list to `pg_available_extensions`. A missing row is
unavailable; a row with NULL `installed_version` is available but not installed;
a non-NULL installed version exists in this database. Also capture every
available version, PostgreSQL/image version, control-file trust, CREATE
privilege, owner, replica compatibility, and supported upgrade path.

## Exercise 2 — Case-insensitive identity

A generated lower-case key centralizes one invariant and supports a unique
index. It differs from citext across operators, implicit casts, joins,
collations, Unicode case folding, and schema type contracts. Choose a documented
normalization/collation and test real-language edge cases rather than assuming
lowercase equals identity.

## Exercise 3 — Spatial semantics

Built-in `point <-> point` returns planar units on an abstract coordinate grid.
PostGIS geometry adds SRID-aware planar operations and transformations;
geography models Earth distance. Longitude/latitude degrees are not meters and
cross dateline/poles; select SRID/type before distance/index design.

## Exercise 4 — Vectors

`checked_l2` rejects unequal dimensions and computes exact L2 by matching array
ordinality. This is adequate only for tiny fixtures. pgvector adds typed
dimensions/operators and exact/approximate indexes. HNSW and IVFFlat differ in
build time, memory, training/list/probe/search parameters, update behavior, and
recall. Evaluate against labeled queries and pin embedding model/version.

## Exercise 5 — Cryptography

Built-in SHA-256 is a deterministic integrity checksum. pgcrypto adds digest,
password `crypt`, random bytes, and PGP-style encryption, but database-side key
exposure and threat model matter. Passwords need a deliberately slow password
KDF; encryption keys should usually be managed outside the protected data and
remain recoverable under strict access.

## Exercise 6 — FDW boundary

Own foreign servers/mappings separately, keep credentials out of DDL/Git, import
only reviewed columns, test pushdown with EXPLAIN, bound timeouts/concurrency,
define transaction consistency, and materialize a local timestamped snapshot
when remote failure/freshness trade-offs permit. Reconcile source keys and
record extraction watermark.

## Exercise 7 — Search

Prefix `LIKE 'post%'` can use a compatible pattern index; full-text search uses
lexemes/language; pg_trgm supports similarity and many wildcard patterns through
its `%`, distance, LIKE/ILIKE operator support. Pick the operator first, then
the matching GIN/GiST trigram operator class and measured threshold.

## Edge cases

- Pre-existing extensions are legitimate environment state; the solution
  inspects and never drops them.
- Extension dump/restore ordering and binary availability require rehearsal.
- FDW remote schema drift can break local prepared queries.
- Embedding backfills need dual-version compatibility like schema migrations.

