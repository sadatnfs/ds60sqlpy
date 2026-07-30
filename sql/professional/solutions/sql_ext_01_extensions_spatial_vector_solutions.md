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

## Exercise 8 — Extension lifecycle inventory

Join `pg_extension` to available versions and dependency catalogs; add owner,
installed/default/available version, update paths, trust, package/image source,
supported platforms, backup behavior, replica compatibility, approver, patch
owner, and tested removal/rollback.

An extension is executable code and schema objects, not a feature flag. Binary
availability on every restore/replica node matters. The executable answer only
inventories capabilities and never changes them.

## Exercise 9 — Collation version drift

Compare recorded provider versions with current actual versions. A mismatch
means sort keys may have changed after libc/ICU updates; it does not identify
every affected index automatically.

Inventory indexes, constraints, partitions, and materialized results using that
collation; plan controlled REINDEX/refresh, conflict handling, capacity/locks,
and post-checks. Refresh version metadata only after remediation is validated.

## Exercise 10 — PostGIS nearest-resource design

Use geography point SRID 4326 (or a reviewed transformed geometry). Apply
`ST_DWithin` in meters so GiST can prefilter, then order candidates by exact
`ST_Distance` and a stable resource ID.

Validate coordinate order/range, SRID, units, empty geometry, poles,
antimeridian, and spheroid accuracy. This is design-only unless PostGIS is
already approved in an isolated environment.

## Exercise 11 — pgvector metric and ANN evidence

Choose L2, negative inner product, or cosine from the embedding model contract.
Normalize when required and enforce comparable model/version/dimension.

Measure exact top-k ground truth against HNSW/IVFFlat recall with real filters,
concurrency, mutations, build time, memory, disk, and latency. Tune search
parameters and retain an exact fallback; index use is not relevance evidence.

## Exercise 12 — Operable FDW boundary

Use external secret storage and a narrow mapping owner with rotation rehearsal;
bound connections/timeouts and remote resources. Validate imported schema,
inspect pushdown, and monitor latency, rows, errors, and freshness.

Define transaction and retry semantics. Maintain a timestamped reconciled
last-known-good snapshot when stale local data is safer than live dependency
failure. Never commit credentials in SQL.

## Exercise 13 — Extension supply-chain review

Require approved publisher/source, pinned checksums, reproducible or trusted
packages, dependency/SBOM and CVE/license review, native-code privilege analysis,
platform support, patch owner/SLA, backup/restore, and removal rehearsal.

Compiling successfully is not approval. Native code runs inside the database
process; prefer a maintained external service or built-in fallback when
lifecycle ownership is absent.

## Exercise 14 — Upgrade rehearsal

Restore a representative disposable database with old binaries, inventory
dependent objects/functions/plans and data checks, then follow a supported
update path. Run catalog, correctness, application, and performance canaries.

Confirm dump/restore and replica compatibility. Many upgrades are not reversibly
transactional, so rollback may require traffic fencing and restore rather than
an attempted downgrade.

## Edge cases

- Pre-existing extensions are legitimate environment state; the solution
  inspects and never drops them.
- Extension dump/restore ordering and binary availability require rehearsal.
- FDW remote schema drift can break local prepared queries.
- Embedding backfills need dual-version compatibility like schema migrations.
