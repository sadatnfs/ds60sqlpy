# SQL-EXT-01 — Extensions, Spatial Data, and Vectors

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-types-01` and `sql-ops-01`
- **Prerequisites:** [SQL-TYPES-01](sql_types_01_native_types_search.md),
  [SQL-OPS-01](sql_ops_01_indexes_statistics_maintenance.md), privileges, and
  a disposable PostgreSQL 16+ database.
- **Artifacts:** [learner SQL](../lessons/sql_ext_01_extensions_spatial_vector.sql) ·
  [solution reasoning](../solutions/sql_ext_01_extensions_spatial_vector_solutions.md) ·
  [executable solution](../solutions/sql_ext_01_extensions_spatial_vector_solutions.sql)

Run the offline default:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_ext_01_extensions_spatial_vector.sql
```

It reads extension catalogs, uses built-in fallbacks, and rolls back. It never
executes `CREATE EXTENSION`, creates an FDW server/user mapping, or downloads an
image.

## Learning objectives

- Inspect extension capability/version boundaries and compare pg_trgm, citext,
  pgcrypto, PostGIS, pgvector, and postgres_fdw with bounded built-in fallbacks.
- Model planar versus geographic distance and implement exact small-vector
  distance.
- Design extension ownership, upgrade, portability, and security tests before
  adoption.

## Vocabulary and concepts

- **Extension:** versioned bundle of database objects installed per database.
- **Available/installed:** control files on the server versus objects created in
  the current database.
- **Capability boundary:** versions, privileges, image/platform, operators, and
  operational assumptions required by a feature.
- **SRID:** spatial reference-system identifier defining coordinate meaning.
- **Geometry/geography:** PostGIS planar/projected versus geodesic models.
- **Embedding:** numeric vector whose distance is meaningful only for a defined
  model/version/normalization.
- **HNSW/IVFFlat:** approximate pgvector index strategies with recall/build/query
  trade-offs.
- **FDW:** foreign data wrapper exposing remote data as foreign tables.
- **Pushdown:** executing eligible filtering/join work at the remote server.

## Worked example / walkthrough

`pg_available_extensions` answers whether the server installation exposes a
control file and its default version. `installed_version` answers whether this
database has created it. Neither proves the connected role may install/upgrade
it, that replicas carry compatible binaries, or that an application was tested
against that exact version.

The default fallbacks are intentionally narrow:

- generated `lower(display_name)` plus a unique index implements one normalized
  identifier rule; it is not a full citext replacement across collations and
  operators;
- expression-prefix and full-text indexes cover their exact query families, not
  pg_trgm similarity;
- built-in `point`/GiST handles an abstract planar grid, not Earth coordinates,
  SRIDs, transformations, topology, or geodesic distance;
- a three-element array and exact L2 scan teach vector grain/dimensions but offer
  no pgvector type, distance operator, or ANN index;
- built-in SHA-256 detects fixture drift but is not encryption, password
  hashing, authenticity, or key management; and
- a timestamped local snapshot demonstrates a resilient FDW alternative without
  network, server objects, mappings, or credentials.

PostGIS requires correct SRID and geometry/geography choice before indexing.
pgvector embeddings require model name/version, dimension, normalization,
distance metric, and safe re-embedding strategy. Approximate indexes trade recall
for speed and need evaluation data; “nearest” is not automatically relevant.

FDWs couple local queries to remote availability, latency, permissions, schema,
and transaction semantics. Pushdown varies by expression/server version. A
materialized local snapshot can provide isolation and reproducibility when
freshness requirements permit.

### Optional isolated container path

This is operator-approved specialization work, not a default command. Use a
separate Compose project/volume/port and an organization-approved image pinned
to exact PostgreSQL and extension versions. Inspect
`pg_available_extension_versions`, enable only the one feature under study in
that disposable database, run compatibility/upgrade/restore tests, then remove
that exact project and volume. PostGIS and pgvector images do not necessarily
contain each other; never assume one “extensions” image has every version.

DBA-only SQL inside that isolated target might include:

```sql
CREATE EXTENSION pg_trgm;
CREATE EXTENSION citext;
CREATE EXTENSION pgcrypto;
CREATE EXTENSION postgis;
CREATE EXTENSION vector;
CREATE EXTENSION postgres_fdw;
```

Do not run this block in the course database. Each statement needs availability,
owner, version, upgrade, backup/restore, replica, and removal review. FDW server
and user-mapping creation additionally handles remote endpoints and secrets and
is intentionally omitted.

## Exercises

Complete all seven prompts: capability classification, case-folding boundary,
spatial semantics, vector validation/index trade-offs, cryptographic purpose,
FDW design, and search-operator comparison. For each optional extension, record
the built-in fallback, what the fallback cannot do, and cleanup/rollback plan.

## Self-check

- Does the default run succeed when every optional extension is absent?
- Is no extension installed or upgraded?
- Are case, collation, spatial coordinates, vector dimensions/model, and
  cryptographic purpose explicit?
- Is every optional index paired with its exact operators and measured workload?
- Are FDW secrets absent from SQL and repository files?
- Is the optional environment isolated by database, port, project, and volume?
- Does rollback remove every fallback object?

## Common pitfalls

- `available` is not `installed`, authorized, compatible, or supported.
- Extension upgrades can change stored/index/operator behavior and require
  rehearsal on backups.
- Lowercasing is not universal language-aware identity.
- Longitude/latitude in built-in `point` produces meaningless Euclidean units.
- Vector similarity can encode model bias and drift; embeddings are versioned
  data, not timeless facts.
- Approximate nearest-neighbour results need recall evaluation.
- Fast hashes are unsafe password storage.
- FDW queries can turn remote slowness/failure into local transaction failure.
- `DROP EXTENSION ... CASCADE` is destructive and is never a casual cleanup
  shortcut.

## Next step

Continue to [SQL-REPL-01 — replication, CDC, and high availability](sql_repl_01_cdc_high_availability.md).
Carry extension binaries/versions, owners, grants, indexes, backup scope, replica
compatibility, and disaster-recovery evidence into every adoption decision.
