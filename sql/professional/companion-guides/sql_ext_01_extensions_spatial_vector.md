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
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-ext-01/lesson/workspace/sql/professional/lessons/sql_ext_01_extensions_spatial_vector.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. The key vocabulary for this lesson is Extension, Available/installed, Capability boundary, SRID, Geometry/geography, Embedding. Its worked SQL reads or creates `pg_catalog.pg_available_extensions`, `pro_extensions_lab.resources`, `pro_extensions_lab.remote_snapshot`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: pgavailableextensions answers whether the server installation exposes a control file and its default version. installedversion answers whether this database has created it. Neither proves the connected role may install/upgrade it, that replicas carry compatible binaries, or that an application was tested against that exact version.
The first runnable example has a concrete contract: Example 1 returns one row per `name`, `default_version`, and `installed_version` with columns `name`, `purpose`, `default_version`, `installed_version`, `available_on_server`, and `installed_in_database` from `requested`, and `pg_catalog.pg_available_extensions`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `name`, `purpose`, `default_version`, `installed_version`, `available_on_server`, and `installed_in_database`. Reselect the returned key columns from `requested`, and `pg_catalog.pg_available_extensions`, reject duplicate keys when the grain is one row per entity, and check the stated row cap and sort direction only when this example includes them. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

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

**How to read it:** Example 1: Start with `requested`, and `pg_catalog.pg_available_extensions` in `FROM`/`JOIN`. The final `SELECT` displays `name`, `purpose`, `default_version`, `installed_version`, `available_on_server`, and `installed_in_database`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `name`, `default_version`, and `installed_version` with columns `name`, `purpose`, `default_version`, `installed_version`, `available_on_server`, and `installed_in_database` from `requested`, and `pg_catalog.pg_available_extensions`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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

**Expected result/shape:** Example 2 must print the expected DDL command tag for `pro_extensions_lab.resources`. Verify the object in `pg_catalog.pg_class`, `pg_catalog.pg_available_extensions`, and `pg_catalog.pg_extension`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

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
   **Inputs/evidence:** For sql-ext-01 Exercise 1, complete the capability matrix written analysis and support its claims with read-only evidence from `pg_available_extensions`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-ext-01 Exercise 1, expected output: a completed the capability matrix written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `installed_version`.
   **Verify:** For sql-ext-01 Exercise 1, check the capability matrix written analysis against `installed_version`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
2. **Case folding:** compare generated lowercase storage with `citext` across
   collation, operators, joins, and writers.
   **Inputs/evidence:** For sql-ext-01 Exercise 2, read from `pro_extensions_lab.items`, `items_normalized_name_uk`, and `pro_extensions_lab.checked_l2`. Build the answer toward `result`; keep `result` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ext-01 Exercise 2, expected output: one row per `result`. The final columns are `result`.
   **Verify:** For sql-ext-01 Exercise 2, project `result` plus the raw source columns from `pro_extensions_lab.items`, `items_normalized_name_uk`, and `pro_extensions_lab.checked_l2` at each join stage; record row count and distinct `result`, then assert the final `result` values match those staged rows without unintended fanout or loss. Add one source row with a new `result`; verify the result gains exactly one row carrying that `result` value.
3. **Spatial meaning:** contrast abstract `point` distance with PostGIS
   geometry/geography, SRID, and earth units.
   **Inputs/evidence:** For sql-ext-01 Exercise 3, read from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Build the answer toward `point`; keep `point` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ext-01 Exercise 3, expected output: one row per `point`. The final columns are `point`.
   **Verify:** For sql-ext-01 Exercise 3, reselect the returned keys directly from the source; require unique `point` where the expected grain is one row per key and confirm the projected `point` against `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Add one source row with a new `point`; verify the result gains exactly one row carrying that `point` value.
4. **Vector safety:** validate dimensions and compare exact scan with ANN
   accuracy and lifecycle costs.
   **Inputs/evidence:** For sql-ext-01 Exercise 4, read from `pro_extensions_lab.items`. Build the answer toward `item_name`, `planar_distance`, `vector_distance`, and `payload_sha256`; keep `planar_distance` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ext-01 Exercise 4, expected output: one row per `planar_distance`. The final columns are `item_name`, `planar_distance`, `vector_distance`, and `payload_sha256`. The final order is `vector_distance, i.item_id`.
   **Verify:** For sql-ext-01 Exercise 4, reselect the returned keys directly from the source; require unique `planar_distance` where the expected grain is one row per key and confirm the projected `item_name`, `planar_distance`, `vector_distance`, and `payload_sha256` against `pro_extensions_lab.items`. Add one source row with a new `planar_distance`; verify the result gains exactly one row carrying that `planar_distance` value.
5. **Cryptographic purpose:** separate digest, password hashing, encryption,
   signing, and external key management.
   **Inputs/evidence:** For sql-ext-01 Exercise 5, use `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-ext-01 Exercise 5, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `crypt`.
   **Verify:** For sql-ext-01 Exercise 5, restore into an isolated target and reconcile `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
6. **FDW boundary:** design ownership, mapping, secret, contract, pushdown,
   consistency, failure, and snapshot behavior.
   **Inputs/evidence:** For sql-ext-01 Exercise 6, read from `pro_extensions_lab.remote_snapshot`, and `pg_catalog.pg_extension`. Build the answer toward `source_key`, `fetched_at`, and `payload`; keep `source_key` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ext-01 Exercise 6, expected output: one row per `source_key`. The final columns are `source_key`, `fetched_at`, and `payload`. The final order is `rs.source_key, rs.fetched_at DESC, rs.snapshot_id DESC`.
   **Verify:** For sql-ext-01 Exercise 6, reselect the returned keys directly from the source; require unique `source_key` where the expected grain is one row per key and confirm the projected `source_key`, `fetched_at`, and `payload` against `pro_extensions_lab.remote_snapshot`, and `pg_catalog.pg_extension`. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
7. **Search operators:** map trigram, prefix, and full-text questions to exact
   operators and indexes.
   **Inputs/evidence:** For sql-ext-01 Exercise 7, read from `requested`, `pg_catalog.pg_available_extensions`, and `pg_catalog.pg_extension`. Build the answer toward `extension_name`, `default_version`, `installed_version`, and `installed_owner`; keep `extension_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ext-01 Exercise 7, expected output: one row per `extension_name`. The final columns are `extension_name`, `default_version`, `installed_version`, and `installed_owner`. The final order is `r.extension_name`.
   **Verify:** For sql-ext-01 Exercise 7, project `extension_name` plus the raw source columns from `requested`, `pg_catalog.pg_available_extensions`, and `pg_catalog.pg_extension` at each join stage; record row count and distinct `extension_name`, then assert the final `extension_name`, `default_version`, `installed_version`, and `installed_owner` values match those staged rows without unintended fanout or loss. Add one source row with a new `extension_name`; verify the result gains exactly one row carrying that `extension_name` value.
8. **Lifecycle inventory:** record owner, versions, dependencies, trust, source,
   update path, approval, restore, and rollback.
   **Inputs/evidence:** For sql-ext-01 Exercise 8, use `pg_extension` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-ext-01 Exercise 8, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
   **Verify:** For sql-ext-01 Exercise 8, restore into an isolated target and reconcile `pg_extension` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
9. **Collation drift:** detect provider/version changes and plan impact review,
   reindex, and validation.
   **Inputs/evidence:** For sql-ext-01 Exercise 9, read from `pg_catalog.pg_collation`. Build the answer toward `collname`, `collprovider`, `recorded_version`, and `actual_version`; keep `collname` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ext-01 Exercise 9, expected output: one row per `collname`. The final columns are `collname`, `collprovider`, `recorded_version`, and `actual_version`. The final order is `c.collname`.
   **Verify:** For sql-ext-01 Exercise 9, run an anti-check that counts rows where NOT ((c.collversion IS NOT NULL AND c.collversion IS DISTINCT FROM pg_catalog.pg_collation_actual_version(c.oid))); require unique `collname` where the expected grain is one row per key and confirm the projected `collname`, `collprovider`, `recorded_version`, and `actual_version` against `pg_catalog.pg_collation`. Add one row for which `(c.collversion IS NOT NULL AND c.collversion IS DISTINCT FROM pg_catalog.pg_collation_actual_version(c.oid))` is true and one for which it is false; verify only the matching `collname` value is returned.
10. **PostGIS nearest:** design SRID/units-safe prefilter plus exact distance and
    tie behavior.
   **Inputs/evidence:** For sql-ext-01 Exercise 10, complete the postgis nearest written analysis and support its claims with read-only evidence from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-ext-01 Exercise 10, expected output: a completed the postgis nearest written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `st_dwithin`, and `st_distance`.
   **Verify:** For sql-ext-01 Exercise 10, check the postgis nearest written analysis against `st_dwithin`, and `st_distance`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
11. **pgvector choice:** compare metric/operator, normalization, HNSW/IVFFlat,
    recall, filter, dimension, write, and exact fallback.
   **Inputs/evidence:** For sql-ext-01 Exercise 11, read from `pro_extensions_lab.items`. Build the answer toward `item_id`, `item_name`, and `exact_l2`; keep `item_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ext-01 Exercise 11, expected output: one row per `item_id`. The final columns are `item_id`, `item_name`, and `exact_l2`. The final order is `exact_l2, i.item_id`.
   **Verify:** For sql-ext-01 Exercise 11, reselect the returned keys directly from the source; require unique `item_id` where the expected grain is one row per key and confirm the projected `item_id`, `item_name`, and `exact_l2` against `pro_extensions_lab.items`. Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.
12. **FDW operations:** add credential rotation, connection/time limits, drift,
    failure visibility, and last-known-good behavior.
   **Inputs/evidence:** For sql-ext-01 Exercise 12, read from `pro_extensions_lab.remote_snapshot`. Build the answer toward `source_key`, `snapshot_watermark`, and `retained_versions`; keep `source_key` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ext-01 Exercise 12, expected output: one row per `source_key`. The final columns are `source_key`, `snapshot_watermark`, and `retained_versions`. The final order is `rs.source_key`.
   **Verify:** For sql-ext-01 Exercise 12, independently aggregate `pro_extensions_lab.remote_snapshot` by `source_key`; require one output row for every distinct `source_key` tuple and compare `snapshot_watermark`, and `retained_versions` tuple by tuple. Tie two rows on `rs.source_key` and give them different `rs.source_key` values; verify `rs.source_key` chooses a stable first/last row.
13. **Supply chain:** review provenance, native privilege, CVEs, builds,
    licensing, patch ownership, and removal.
   **Inputs/evidence:** For sql-ext-01 Exercise 13, read from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Build the answer toward `supply_chain_answer`; keep `supply_chain_answer` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ext-01 Exercise 13, expected output: one row per `supply_chain_answer`. The final columns are `supply_chain_answer`.
   **Verify:** For sql-ext-01 Exercise 13, reselect the returned keys directly from the source; require unique `supply_chain_answer` where the expected grain is one row per key and confirm the projected `supply_chain_answer` against `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.
14. **Upgrade rehearsal:** restore isolation, capture dependencies/plans,
    canary correctness/performance, compatibility, and rollback limits.
   **Inputs/evidence:** For sql-ext-01 Exercise 14, use `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-ext-01 Exercise 14, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
   **Verify:** For sql-ext-01 Exercise 14, restore into an isolated target and reconcile `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

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

I have completed the direct catalog prerequisites: `sql-types-01`, `sql-ops-01`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_ext_01_extensions_spatial_vector.md
- Answer-free learner SQL: sql/professional/lessons/sql_ext_01_extensions_spatial_vector.sql

Key terms to teach in context: Extension, Available/installed, Capability boundary, SRID, Geometry/geography, Embedding. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: pgavailableextensions answers whether the server installation exposes a control file and its default version. installedversion answers whether this database has created it. Neither proves the connected role may install/upgrade it, that replicas carry compatible binaries, or that an application was tested against that exact version.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-ext-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
