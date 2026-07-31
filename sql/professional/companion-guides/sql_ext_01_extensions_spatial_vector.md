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
   **Inputs/evidence:** For sql-ext-01 Exercise 1, LEFT JOIN the requested extension-name fixture (citext, pg_trgm, pgcrypto, postgis, postgres_fdw, and vector) to `pg_available_extensions` and `pg_extension`. This is read-only discovery.
   **Expected result/shape:** For sql-ext-01 Exercise 1, One row per requested `extension_name`, with `extension_name`, `default_version`, `installed_version`, `installed_owner`, and `capability_state`, ordered by `extension_name`. State is `unavailable`, `available_not_installed`, or `installed`.
   **Verify:** For sql-ext-01 Exercise 1, Every requested name appears exactly once even when unavailable; compare installed versions directly with `pg_extension`. Record CREATE privilege/approval as unknown unless separately proven—availability does not grant permission. Hint ladder, rung 1: Start from the requested list and LEFT JOIN catalogs, otherwise unavailable names disappear.
2. **Case folding:** compare generated lowercase storage with `citext` across
   collation, operators, joins, and writers.
   **Inputs/evidence:** For sql-ext-01 Exercise 2, Inspect generated column `pro_extensions_lab.items.normalized_name` and its unique-index catalog row; compare that narrow `lower(item_name)` rule with optional `citext`.
   **Expected result/shape:** For sql-ext-01 Exercise 2, A catalog evidence row names the generated expression and unique index definition. A behavior table has `case_id`, `candidate_name`, `normalized_name`, `expected_outcome`, and `observed_sqlstate` for a distinct insert and a case-fold collision.
   **Verify:** For sql-ext-01 Exercise 2, In a savepoint, `Charlie` succeeds and `alpha` conflicts with existing `Alpha` using SQLSTATE `23505`; rollback removes both attempts. Document Unicode/collation, operators/joins, and cross-writer limitations rather than claiming `lower()` is universally equivalent to `citext`. Hint ladder, rung 1: The generated column is a stored key; every lookup and join must use the same explicit normalization contract.
3. **Spatial meaning:** contrast abstract `point` distance with PostGIS
   geometry/geography, SRID, and earth units.
   **Inputs/evidence:** For sql-ext-01 Exercise 3, Calculate `<->` from each `pro_extensions_lab.items.location` to the built-in point `(1,1)`, and write a comparison matrix for built-in `point`, PostGIS `geometry`, and PostGIS `geography`.
   **Expected result/shape:** For sql-ext-01 Exercise 3, One row per `item_id`, with `item_id`, `item_name`, and `planar_distance`, ordered by `planar_distance, item_id`. The matrix names coordinate model, SRID support, distance units, index/operator, and appropriate use for each type.
   **Verify:** For sql-ext-01 Exercise 3, Distances may tie, so `item_id`—not distance—is the identity and final tie-break. Prove the built-in result is Cartesian grid distance and explicitly reject interpreting latitude/longitude degrees as meters. Hint ladder, rung 1: A numeric distance has no geographic meaning until the coordinate reference system and units are defined.
4. **Vector safety:** validate dimensions and compare exact scan with ANN
   accuracy and lifecycle costs.
   **Inputs/evidence:** For sql-ext-01 Exercise 4, Strengthen `pro_extensions_lab.checked_l2(left,right)` to reject NULL arrays, zero dimensions, unequal dimensions, NULL elements, and non-finite elements before calculating exact L2 distance.
   **Expected result/shape:** For sql-ext-01 Exercise 4, One row per `item_id`, with `item_id`, `item_name`, and `vector_distance`, ordered by `vector_distance, item_id`. The supplied `[0,0,0]` to `[3,4,0]` control equals `5`.
   **Verify:** For sql-ext-01 Exercise 4, Named negative controls reject dimension mismatch, empty arrays, NULL elements, `Infinity`, and `NaN` with SQLSTATE `23514`; equal distance ties remain separate item IDs. Compare exact scan results with any approved ANN index before reporting recall, memory, build, or write cost. Hint ladder, rung 1: `sum()` silently ignores NULL inputs, so validation must happen before unnesting and aggregation.
5. **Cryptographic purpose:** separate digest, password hashing, encryption,
   signing, and external key management.
   **Inputs/evidence:** For sql-ext-01 Exercise 5, Read `item_id`, `item_name`, and generated `payload_sha256` from `pro_extensions_lab.items`; separately classify SHA-256, optional `pgcrypto.digest`, `crypt`, PGP encryption, and external key management.
   **Expected result/shape:** For sql-ext-01 Exercise 5, One row per `item_id` with the three evidence columns, ordered by `item_id`. A purpose matrix names integrity digest, password hashing, encryption, key custody, and capability/fallback.
   **Verify:** For sql-ext-01 Exercise 5, Recompute SHA-256 from `payload` and compare all 64 hex characters; changing payload changes the digest. The matrix must explicitly forbid a fast unsalted digest for password storage and must not claim optional pgcrypto functions ran when unavailable. Hint ladder, rung 1: Hashing, password verification, encryption, and key management solve different threats.
6. **FDW boundary:** design ownership, mapping, secret, contract, pushdown,
   consistency, failure, and snapshot behavior.
   **Inputs/evidence:** For sql-ext-01 Exercise 6, Use local `pro_extensions_lab.remote_snapshot`; no foreign server, user mapping, network connection, or credential is created. Choose the latest row per `source_key` by `fetched_at DESC, snapshot_id DESC`.
   **Expected result/shape:** For sql-ext-01 Exercise 6, One row per `source_key`, with `source_key`, `snapshot_id`, `fetched_at`, and `payload`, ordered by `source_key`.
   **Verify:** For sql-ext-01 Exercise 6, Add two same-time snapshots and prove greater `snapshot_id` wins. Separately review server ownership, secret location/rotation, imported columns, pushdown, transaction consistency, timeout, failure isolation, and snapshot fallback before any approved FDW deployment. Hint ladder, rung 1: Capability inventory and a local snapshot are safe evidence; neither proves a remote FDW connection is authorized or healthy.
7. **Search operators:** map trigram, prefix, and full-text questions to exact
   operators and indexes.
   **Inputs/evidence:** For sql-ext-01 Exercise 7, Build a reviewed matrix for prefix `LIKE 'term%'`, optional pg_trgm similarity/operators, and built-in full-text search. Name the query operator and matching index/operator class together.
   **Expected result/shape:** For sql-ext-01 Exercise 7, One row per `search_method`, with `search_method`, `query_operator`, `index_strategy`, `ranking_semantics`, `strength`, and `limitation`.
   **Verify:** For sql-ext-01 Exercise 7, Use one exact prefix, one misspelling, and one multi-token document to show the methods answer different questions. If `pg_trgm` is absent, record that capability as unavailable and run only built-in comparisons. Hint ladder, rung 1: An index helps only operators supported by its operator class; “fuzzy,” “prefix,” and “linguistic” are not synonyms.
8. **Lifecycle inventory:** record owner, versions, dependencies, trust, source,
   update path, approval, restore, and rollback.
   **Inputs/evidence:** For sql-ext-01 Exercise 8, Extend Exercise 1's read-only requested-extension inventory with available versions/trusted flag, installed schema/owner, dependencies, update path, publisher/package provenance, approval, backup/restore needs, rollback test, and named owner.
   **Expected result/shape:** For sql-ext-01 Exercise 8, One row per requested `extension_name`, with catalog facts kept separate from reviewed policy fields. No `CREATE EXTENSION`, `ALTER EXTENSION`, or `DROP EXTENSION` runs.
   **Verify:** For sql-ext-01 Exercise 8, Every installed extension has an exact version, owner, schema, dependency inventory, package source, upgrade and restore rehearsal, and rollback limit. Unavailable extensions remain visible with an explicit fallback instead of disappearing. Hint ladder, rung 1: Catalog state is observed evidence; approval, provenance, rollback, and operational ownership are separate decisions.
9. **Collation drift:** detect provider/version changes and plan impact review,
   reindex, and validation.
   **Inputs/evidence:** For sql-ext-01 Exercise 9, Read `pg_collation` and compare non-NULL recorded `collversion` with `pg_collation_actual_version(oid)`. This query detects; it does not reindex or refresh metadata.
   **Expected result/shape:** For sql-ext-01 Exercise 9, One row per mismatched `(collation_schema, collation_name, encoding)`, with those identity fields, `collprovider`, `recorded_version`, and `actual_version`, ordered by all three identity fields.
   **Verify:** For sql-ext-01 Exercise 9, An empty result means no mismatch was detected, not that every dependent index was inspected. For each returned collation, inventory dependent indexes, rehearse `REINDEX`, validate ordering/uniqueness, and only then refresh version metadata under an approved runbook. Hint ladder, rung 1: `collname` alone is not globally unique; preserve its namespace and encoding.
10. **PostGIS nearest:** design SRID/units-safe prefilter plus exact distance and
    tie behavior.
   **Inputs/evidence:** For sql-ext-01 Exercise 10, Write but do not execute a PostGIS query unless capability and approval are confirmed. Use `geography` with a declared SRID, a GiST indexable `ST_DWithin` radius prefilter, exact `ST_Distance`, and stable `resource_id` tie-break.
   **Expected result/shape:** For sql-ext-01 Exercise 10, A reviewed query contract names parameters, coordinate validation, meters as units, output grain/columns/order, antimeridian/pole cases, maximum radius, timeout, fallback, and owner.
   **Verify:** For sql-ext-01 Exercise 10, In an approved isolated PostGIS environment, compare the indexed query with a small exact control set, inspect `EXPLAIN (ANALYZE, BUFFERS)`, and test equal distances plus antimeridian/pole fixtures. Otherwise report `not executed: capability unavailable`. Hint ladder, rung 1: Prefilter for indexable radius, then calculate exact distance and order by distance plus stable identity.
11. **pgvector choice:** compare metric/operator, normalization, HNSW/IVFFlat,
    recall, filter, dimension, write, and exact fallback.
   **Inputs/evidence:** For sql-ext-01 Exercise 11, Use validated arrays and `checked_l2` as the built-in exact fallback; separately define optional pgvector cosine, inner-product, and L2 semantics plus HNSW/IVFFlat evaluation.
   **Expected result/shape:** For sql-ext-01 Exercise 11, One row per `item_id`, with `item_id`, `item_name`, and `exact_l2`, ordered by `exact_l2, item_id`.
   **Verify:** For sql-ext-01 Exercise 11, Compare every ANN candidate set with this exact ordering and report recall at the chosen `k`, filtered recall, latency, build memory/time, update cost, and index size. State normalization assumptions and use `item_id` to keep equal distances deterministic. Hint ladder, rung 1: A fast plan is not sufficient; ANN adoption needs a correctness benchmark against the exact metric.
12. **FDW operations:** add credential rotation, connection/time limits, drift,
    failure visibility, and last-known-good behavior.
   **Inputs/evidence:** For sql-ext-01 Exercise 12, Aggregate local `pro_extensions_lab.remote_snapshot` by `source_key`; accompany it with an FDW operations contract for secrets, connections, schema drift, timeouts, pushdown, partial failure, and fallback.
   **Expected result/shape:** For sql-ext-01 Exercise 12, One row per `source_key`, with `source_key`, `snapshot_watermark`, and `retained_versions`, ordered by `source_key`.
   **Verify:** For sql-ext-01 Exercise 12, Independently compare `max(fetched_at)` and counts per key; add a same-time version and confirm the latest-row query uses `snapshot_id` for its tie, while this aggregate correctly increments `retained_versions`. Simulate remote unavailability by using only the timestamped local fallback. Hint ladder, rung 1: A watermark says when the snapshot was fetched, not that the remote source is current or complete.
13. **Supply chain:** review provenance, native privilege, CVEs, builds,
    licensing, patch ownership, and removal.
   **Inputs/evidence:** For sql-ext-01 Exercise 13, For one unavailable requested extension, assemble observed package availability plus reviewed source/build provenance, SBOM/native dependencies, CVEs, license, reproducibility, signer/hash, patch owner/SLA, restore compatibility, removal test, and approving authority.
   **Expected result/shape:** For sql-ext-01 Exercise 13, One row per `review_item`, with `review_item`, `observed_evidence`, `status`, `owner`, and `blocking_reason`. Unknown or missing evidence remains visible and blocks approval.
   **Verify:** For sql-ext-01 Exercise 13, A successful local compile is not sufficient. Remove the source signature/SBOM or make the removal rehearsal fail; the final decision must remain `rejected`/`blocked` without installing anything. Hint ladder, rung 1: Native extension code executes inside the database server process, so provenance and patch ownership are security controls.
14. **Upgrade rehearsal:** restore isolation, capture dependencies/plans,
    canary correctness/performance, compatibility, and rollback limits.
   **Inputs/evidence:** For sql-ext-01 Exercise 14, Plan an extension upgrade only in a separately restored disposable database. Capture installed/target versions, package build, dependency graph, objects, query plans/results, backup compatibility, application canaries, elapsed/lock/WAL evidence, rollback limit, owner, and cleanup.
   **Expected result/shape:** For sql-ext-01 Exercise 14, One row per `phase_number`, with `phase_name`, `before_evidence`, `after_evidence`, `status`, `owner`, and `failure_response`; this transaction emits a plan and changes no extension.
   **Verify:** For sql-ext-01 Exercise 14, Every before/after correctness and performance check must pass within explicit tolerances. Inject a changed result or incompatible backup restore and prove approval remains blocked; record when downgrade is not a safe rollback and restore/forward-fix is required. Hint ladder, rung 1: Extension DDL success does not prove application semantics, plans, backup compatibility, or reversibility.

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
