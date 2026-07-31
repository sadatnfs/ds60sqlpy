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

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-EXT-01 — PostgreSQL Extensions, Spatial Data, and Vectors** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-ext-01/sql_ext_01_extensions_spatial_vector.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Some demonstrations require privileges or server features a normal course role may not have. Run the capability check first. The supported default path still teaches inspection and design without creating cluster-wide roles, extensions, or replication objects.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_ext_01_extensions_spatial_vector.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_ext_01_extensions_spatial_vector.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. This lesson introduces or reinforces
Extension, Available/installed, Capability boundary, SRID, Geometry/geography, Embedding. Its worked SQL reads or creates `pg_catalog.pg_available_extensions`, `pro_extensions_lab.resources`, `pro_extensions_lab.remote_snapshot`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: pgavailableextensions answers whether the server installation exposes a control file and its default version. installedversion answers whether this database has created it. Neither proves the connected role may install/upgrade it, that replicas carry compatible binaries, or that an application was tested against that exact version.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/professional/lessons/sql_ext_01_extensions_spatial_vector.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH requested(name, purpose) AS (
    VALUES
        ('pg_trgm'::text, 'trigram similarity and wildcard indexes'::text),
        ('citext', 'case-insensitive text type'),
        ('pgcrypto', 'cryptographic digest/encryption helpers'),
        ('postgis', 'coordinate reference systems and spatial operations'),
        ('vector', 'vector type and nearest-neighbour indexes'),
        ('postgres_fdw', 'foreign PostgreSQL tables')
)
SELECT
    requested.name,
    requested.purpose,
    available.default_version,
    available.installed_version,
    available.name IS NOT NULL AS available_on_server,
    available.installed_version IS NOT NULL AS installed_in_database
FROM requested
LEFT JOIN pg_catalog.pg_available_extensions AS available
  ON available.name = requested.name
ORDER BY requested.name;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
CREATE TABLE pro_extensions_lab.resources (
    resource_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    display_name text NOT NULL CHECK (btrim(display_name) <> ''),
    normalized_name text GENERATED ALWAYS AS (lower(display_name)) STORED,
    summary text NOT NULL,
    location point NOT NULL,
    embedding double precision[] NOT NULL
        CHECK (cardinality(embedding) = 3),
    payload text NOT NULL,
    payload_sha256 text GENERATED ALWAYS AS (
        encode(sha256(payload::bytea), 'hex')
    ) STORED
);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

Complete all fourteen prompts. Begin with capability classification, case-folding boundary,
spatial semantics, vector validation/index trade-offs, cryptographic purpose,
FDW design, and search-operator comparison; then cover lifecycle, collation,
operable spatial/vector/FDW designs, supply chain, and upgrade rehearsal. For
each optional extension, record the built-in fallback, what it cannot do, and
the cleanup/rollback plan.

Do not install, update, or connect externally in these exercises; produce
capability evidence and reviewed designs:

1. **Capability matrix:** distinguish unavailable, available, and installed
   versions without treating availability as permission.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. **Case folding:** compare generated lowercase storage with `citext` across
   collation, operators, joins, and writers.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
3. **Spatial meaning:** contrast abstract `point` distance with PostGIS
   geometry/geography, SRID, and earth units.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. **Vector safety:** validate dimensions and compare exact scan with ANN
   accuracy and lifecycle costs.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. **Cryptographic purpose:** separate digest, password hashing, encryption,
   signing, and external key management.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. **FDW boundary:** design ownership, mapping, secret, contract, pushdown,
   consistency, failure, and snapshot behavior.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
7. **Search operators:** map trigram, prefix, and full-text questions to exact
   operators and indexes.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
8. **Lifecycle inventory:** record owner, versions, dependencies, trust, source,
   update path, approval, restore, and rollback.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
9. **Collation drift:** detect provider/version changes and plan impact review,
   reindex, and validation.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
10. **PostGIS nearest:** design SRID/units-safe prefilter plus exact distance and
    tie behavior.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
11. **pgvector choice:** compare metric/operator, normalization, HNSW/IVFFlat,
    recall, filter, dimension, write, and exact fallback.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
12. **FDW operations:** add credential rotation, connection/time limits, drift,
    failure visibility, and last-known-good behavior.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
13. **Supply chain:** review provenance, native privilege, CVEs, builds,
    licensing, patch ownership, and removal.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
14. **Upgrade rehearsal:** restore isolation, capture dependencies/plans,
    canary correctness/performance, compatibility, and rollback limits.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

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

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-ext-01 — PostgreSQL Extensions, Spatial Data, and Vectors.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/professional/companion-guides/sql_ext_01_extensions_spatial_vector.md
- Answer-free learner SQL: sql/professional/lessons/sql_ext_01_extensions_spatial_vector.sql

The lesson concepts include Extension, Available/installed, Capability boundary, SRID, Geometry/geography, Embedding. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: pgavailableextensions answers whether the server installation exposes a control file and its default version. installedversion answers whether this database has created it. Neither proves the connected role may install/upgrade it, that replicas carry compatible binaries, or that an application was tested against that exact version.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-ext-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
