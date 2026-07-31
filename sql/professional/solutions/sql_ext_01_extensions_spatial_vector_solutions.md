# SQL-EXT-01 Solutions — Extensions, Spatial, and Vector Boundaries


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_ext_01_extensions_spatial_vector_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_ext_01_extensions_spatial_vector_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Extension, Available/installed, Capability boundary, SRID, Geometry/geography, Embedding. Its worked-model focus is:
pgavailableextensions answers whether the server installation exposes a control file and its default version. installedversion answers whether this database has created it. Neither proves the connected role may install/upgrade it, that replicas carry compatible binaries, or that an application was tested against that exact version.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 1, LEFT JOIN the requested extension-name fixture (citext, pg_trgm, pgcrypto, postgis, postgres_fdw, and vector) to `pg_available_extensions` and `pg_extension`. This is read-only discovery.
- **Expected result/shape:** For sql-ext-01 Exercise 1, One row per requested `extension_name`, with `extension_name`, `default_version`, `installed_version`, `installed_owner`, and `capability_state`, ordered by `extension_name`. State is `unavailable`, `available_not_installed`, or `installed`.
- **Independent verification:** For sql-ext-01 Exercise 1, Every requested name appears exactly once even when unavailable; compare installed versions directly with `pg_extension`. Record CREATE privilege/approval as unknown unless separately proven—availability does not grant permission. Hint ladder, rung 1: Start from the requested list and LEFT JOIN catalogs, otherwise unavailable names disappear.

## Exercise 2 — Case-insensitive identity

A generated lower-case key centralizes one invariant and supports a unique
index. It differs from citext across operators, implicit casts, joins,
collations, Unicode case folding, and schema type contracts. Choose a documented
normalization/collation and test real-language edge cases rather than assuming
lowercase equals identity.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 2, Inspect generated column `pro_extensions_lab.items.normalized_name` and its unique-index catalog row; compare that narrow `lower(item_name)` rule with optional `citext`.
- **Expected result/shape:** For sql-ext-01 Exercise 2, A catalog evidence row names the generated expression and unique index definition. A behavior table has `case_id`, `candidate_name`, `normalized_name`, `expected_outcome`, and `observed_sqlstate` for a distinct insert and a case-fold collision.
- **Independent verification:** For sql-ext-01 Exercise 2, In a savepoint, `Charlie` succeeds and `alpha` conflicts with existing `Alpha` using SQLSTATE `23505`; rollback removes both attempts. Document Unicode/collation, operators/joins, and cross-writer limitations rather than claiming `lower()` is universally equivalent to `citext`. Hint ladder, rung 1: The generated column is a stored key; every lookup and join must use the same explicit normalization contract.

## Exercise 3 — Spatial semantics

Built-in `point <-> point` returns planar units on an abstract coordinate grid.
PostGIS geometry adds SRID-aware planar operations and transformations;
geography models Earth distance. Longitude/latitude degrees are not meters and
cross dateline/poles; select SRID/type before distance/index design.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 3, Calculate `<->` from each `pro_extensions_lab.items.location` to the built-in point `(1,1)`, and write a comparison matrix for built-in `point`, PostGIS `geometry`, and PostGIS `geography`.
- **Expected result/shape:** For sql-ext-01 Exercise 3, One row per `item_id`, with `item_id`, `item_name`, and `planar_distance`, ordered by `planar_distance, item_id`. The matrix names coordinate model, SRID support, distance units, index/operator, and appropriate use for each type.
- **Independent verification:** For sql-ext-01 Exercise 3, Distances may tie, so `item_id`—not distance—is the identity and final tie-break. Prove the built-in result is Cartesian grid distance and explicitly reject interpreting latitude/longitude degrees as meters. Hint ladder, rung 1: A numeric distance has no geographic meaning until the coordinate reference system and units are defined.

## Exercise 4 — Vectors

`checked_l2` rejects unequal dimensions and computes exact L2 by matching array
ordinality. This is adequate only for tiny fixtures. pgvector adds typed
dimensions/operators and exact/approximate indexes. HNSW and IVFFlat differ in
build time, memory, training/list/probe/search parameters, update behavior, and
recall. Evaluate against labeled queries and pin embedding model/version.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 4, Strengthen `pro_extensions_lab.checked_l2(left,right)` to reject NULL arrays, zero dimensions, unequal dimensions, NULL elements, and non-finite elements before calculating exact L2 distance.
- **Expected result/shape:** For sql-ext-01 Exercise 4, One row per `item_id`, with `item_id`, `item_name`, and `vector_distance`, ordered by `vector_distance, item_id`. The supplied `[0,0,0]` to `[3,4,0]` control equals `5`.
- **Independent verification:** For sql-ext-01 Exercise 4, Named negative controls reject dimension mismatch, empty arrays, NULL elements, `Infinity`, and `NaN` with SQLSTATE `23514`; equal distance ties remain separate item IDs. Compare exact scan results with any approved ANN index before reporting recall, memory, build, or write cost. Hint ladder, rung 1: `sum()` silently ignores NULL inputs, so validation must happen before unnesting and aggregation.

## Exercise 5 — Cryptography

Built-in SHA-256 is a deterministic integrity checksum. pgcrypto adds digest,
password `crypt`, random bytes, and PGP-style encryption, but database-side key
exposure and threat model matter. Passwords need a deliberately slow password
KDF; encryption keys should usually be managed outside the protected data and
remain recoverable under strict access.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 5, Read `item_id`, `item_name`, and generated `payload_sha256` from `pro_extensions_lab.items`; separately classify SHA-256, optional `pgcrypto.digest`, `crypt`, PGP encryption, and external key management.
- **Expected result/shape:** For sql-ext-01 Exercise 5, One row per `item_id` with the three evidence columns, ordered by `item_id`. A purpose matrix names integrity digest, password hashing, encryption, key custody, and capability/fallback.
- **Independent verification:** For sql-ext-01 Exercise 5, Recompute SHA-256 from `payload` and compare all 64 hex characters; changing payload changes the digest. The matrix must explicitly forbid a fast unsalted digest for password storage and must not claim optional pgcrypto functions ran when unavailable. Hint ladder, rung 1: Hashing, password verification, encryption, and key management solve different threats.

## Exercise 6 — FDW boundary

Own foreign servers/mappings separately, keep credentials out of DDL/Git, import
only reviewed columns, test pushdown with EXPLAIN, bound timeouts/concurrency,
define transaction consistency, and materialize a local timestamped snapshot
when remote failure/freshness trade-offs permit. Reconcile source keys and
record extraction watermark.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 6, Use local `pro_extensions_lab.remote_snapshot`; no foreign server, user mapping, network connection, or credential is created. Choose the latest row per `source_key` by `fetched_at DESC, snapshot_id DESC`.
- **Expected result/shape:** For sql-ext-01 Exercise 6, One row per `source_key`, with `source_key`, `snapshot_id`, `fetched_at`, and `payload`, ordered by `source_key`.
- **Independent verification:** For sql-ext-01 Exercise 6, Add two same-time snapshots and prove greater `snapshot_id` wins. Separately review server ownership, secret location/rotation, imported columns, pushdown, transaction consistency, timeout, failure isolation, and snapshot fallback before any approved FDW deployment. Hint ladder, rung 1: Capability inventory and a local snapshot are safe evidence; neither proves a remote FDW connection is authorized or healthy.

## Exercise 7 — Search

Prefix `LIKE 'post%'` can use a compatible pattern index; full-text search uses
lexemes/language; pg_trgm supports similarity and many wildcard patterns through
its `%`, distance, LIKE/ILIKE operator support. Pick the operator first, then
the matching GIN/GiST trigram operator class and measured threshold.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 7, Build a reviewed matrix for prefix `LIKE 'term%'`, optional pg_trgm similarity/operators, and built-in full-text search. Name the query operator and matching index/operator class together.
- **Expected result/shape:** For sql-ext-01 Exercise 7, One row per `search_method`, with `search_method`, `query_operator`, `index_strategy`, `ranking_semantics`, `strength`, and `limitation`.
- **Independent verification:** For sql-ext-01 Exercise 7, Use one exact prefix, one misspelling, and one multi-token document to show the methods answer different questions. If `pg_trgm` is absent, record that capability as unavailable and run only built-in comparisons. Hint ladder, rung 1: An index helps only operators supported by its operator class; “fuzzy,” “prefix,” and “linguistic” are not synonyms.

## Exercise 8 — Extension lifecycle inventory

Join `pg_extension` to available versions and dependency catalogs; add owner,
installed/default/available version, update paths, trust, package/image source,
supported platforms, backup behavior, replica compatibility, approver, patch
owner, and tested removal/rollback.

An extension is executable code and schema objects, not a feature flag. Binary
availability on every restore/replica node matters. The executable answer only
inventories capabilities and never changes them.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 8, Extend Exercise 1's read-only requested-extension inventory with available versions/trusted flag, installed schema/owner, dependencies, update path, publisher/package provenance, approval, backup/restore needs, rollback test, and named owner.
- **Expected result/shape:** For sql-ext-01 Exercise 8, One row per requested `extension_name`, with catalog facts kept separate from reviewed policy fields. No `CREATE EXTENSION`, `ALTER EXTENSION`, or `DROP EXTENSION` runs.
- **Independent verification:** For sql-ext-01 Exercise 8, Every installed extension has an exact version, owner, schema, dependency inventory, package source, upgrade and restore rehearsal, and rollback limit. Unavailable extensions remain visible with an explicit fallback instead of disappearing. Hint ladder, rung 1: Catalog state is observed evidence; approval, provenance, rollback, and operational ownership are separate decisions.

## Exercise 9 — Collation version drift

Compare recorded provider versions with current actual versions. A mismatch
means sort keys may have changed after libc/ICU updates; it does not identify
every affected index automatically.

Inventory indexes, constraints, partitions, and materialized results using that
collation; plan controlled REINDEX/refresh, conflict handling, capacity/locks,
and post-checks. Refresh version metadata only after remediation is validated.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 9, Read `pg_collation` and compare non-NULL recorded `collversion` with `pg_collation_actual_version(oid)`. This query detects; it does not reindex or refresh metadata.
- **Expected result/shape:** For sql-ext-01 Exercise 9, One row per mismatched `(collation_schema, collation_name, encoding)`, with those identity fields, `collprovider`, `recorded_version`, and `actual_version`, ordered by all three identity fields.
- **Independent verification:** For sql-ext-01 Exercise 9, An empty result means no mismatch was detected, not that every dependent index was inspected. For each returned collation, inventory dependent indexes, rehearse `REINDEX`, validate ordering/uniqueness, and only then refresh version metadata under an approved runbook. Hint ladder, rung 1: `collname` alone is not globally unique; preserve its namespace and encoding.

## Exercise 10 — PostGIS nearest-resource design

Use geography point SRID 4326 (or a reviewed transformed geometry). Apply
`ST_DWithin` in meters so GiST can prefilter, then order candidates by exact
`ST_Distance` and a stable resource ID.

Validate coordinate order/range, SRID, units, empty geometry, poles,
antimeridian, and spheroid accuracy. This is design-only unless PostGIS is
already approved in an isolated environment.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 10, Write but do not execute a PostGIS query unless capability and approval are confirmed. Use `geography` with a declared SRID, a GiST indexable `ST_DWithin` radius prefilter, exact `ST_Distance`, and stable `resource_id` tie-break.
- **Expected result/shape:** For sql-ext-01 Exercise 10, A reviewed query contract names parameters, coordinate validation, meters as units, output grain/columns/order, antimeridian/pole cases, maximum radius, timeout, fallback, and owner.
- **Independent verification:** For sql-ext-01 Exercise 10, In an approved isolated PostGIS environment, compare the indexed query with a small exact control set, inspect `EXPLAIN (ANALYZE, BUFFERS)`, and test equal distances plus antimeridian/pole fixtures. Otherwise report `not executed: capability unavailable`. Hint ladder, rung 1: Prefilter for indexable radius, then calculate exact distance and order by distance plus stable identity.

## Exercise 11 — pgvector metric and ANN evidence

Choose L2, negative inner product, or cosine from the embedding model contract.
Normalize when required and enforce comparable model/version/dimension.

Measure exact top-k ground truth against HNSW/IVFFlat recall with real filters,
concurrency, mutations, build time, memory, disk, and latency. Tune search
parameters and retain an exact fallback; index use is not relevance evidence.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 11, Use validated arrays and `checked_l2` as the built-in exact fallback; separately define optional pgvector cosine, inner-product, and L2 semantics plus HNSW/IVFFlat evaluation.
- **Expected result/shape:** For sql-ext-01 Exercise 11, One row per `item_id`, with `item_id`, `item_name`, and `exact_l2`, ordered by `exact_l2, item_id`.
- **Independent verification:** For sql-ext-01 Exercise 11, Compare every ANN candidate set with this exact ordering and report recall at the chosen `k`, filtered recall, latency, build memory/time, update cost, and index size. State normalization assumptions and use `item_id` to keep equal distances deterministic. Hint ladder, rung 1: A fast plan is not sufficient; ANN adoption needs a correctness benchmark against the exact metric.

## Exercise 12 — Operable FDW boundary

Use external secret storage and a narrow mapping owner with rotation rehearsal;
bound connections/timeouts and remote resources. Validate imported schema,
inspect pushdown, and monitor latency, rows, errors, and freshness.

Define transaction and retry semantics. Maintain a timestamped reconciled
last-known-good snapshot when stale local data is safer than live dependency
failure. Never commit credentials in SQL.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 12, Aggregate local `pro_extensions_lab.remote_snapshot` by `source_key`; accompany it with an FDW operations contract for secrets, connections, schema drift, timeouts, pushdown, partial failure, and fallback.
- **Expected result/shape:** For sql-ext-01 Exercise 12, One row per `source_key`, with `source_key`, `snapshot_watermark`, and `retained_versions`, ordered by `source_key`.
- **Independent verification:** For sql-ext-01 Exercise 12, Independently compare `max(fetched_at)` and counts per key; add a same-time version and confirm the latest-row query uses `snapshot_id` for its tie, while this aggregate correctly increments `retained_versions`. Simulate remote unavailability by using only the timestamped local fallback. Hint ladder, rung 1: A watermark says when the snapshot was fetched, not that the remote source is current or complete.

## Exercise 13 — Extension supply-chain review

Require approved publisher/source, pinned checksums, reproducible or trusted
packages, dependency/SBOM and CVE/license review, native-code privilege analysis,
platform support, patch owner/SLA, backup/restore, and removal rehearsal.

Compiling successfully is not approval. Native code runs inside the database
process; prefer a maintained external service or built-in fallback when
lifecycle ownership is absent.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 13, For one unavailable requested extension, assemble observed package availability plus reviewed source/build provenance, SBOM/native dependencies, CVEs, license, reproducibility, signer/hash, patch owner/SLA, restore compatibility, removal test, and approving authority.
- **Expected result/shape:** For sql-ext-01 Exercise 13, One row per `review_item`, with `review_item`, `observed_evidence`, `status`, `owner`, and `blocking_reason`. Unknown or missing evidence remains visible and blocks approval.
- **Independent verification:** For sql-ext-01 Exercise 13, A successful local compile is not sufficient. Remove the source signature/SBOM or make the removal rehearsal fail; the final decision must remain `rejected`/`blocked` without installing anything. Hint ladder, rung 1: Native extension code executes inside the database server process, so provenance and patch ownership are security controls.

## Exercise 14 — Upgrade rehearsal

Restore a representative disposable database with old binaries, inventory
dependent objects/functions/plans and data checks, then follow a supported
update path. Run catalog, correctness, application, and performance canaries.

Confirm dump/restore and replica compatibility. Many upgrades are not reversibly
transactional, so rollback may require traffic fencing and restore rather than
an attempted downgrade.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 14, Plan an extension upgrade only in a separately restored disposable database. Capture installed/target versions, package build, dependency graph, objects, query plans/results, backup compatibility, application canaries, elapsed/lock/WAL evidence, rollback limit, owner, and cleanup.
- **Expected result/shape:** For sql-ext-01 Exercise 14, One row per `phase_number`, with `phase_name`, `before_evidence`, `after_evidence`, `status`, `owner`, and `failure_response`; this transaction emits a plan and changes no extension.
- **Independent verification:** For sql-ext-01 Exercise 14, Every before/after correctness and performance check must pass within explicit tolerances. Inject a changed result or incompatible backup restore and prove approval remains blocked; record when downgrade is not a safe rollback and restore/forward-fix is required. Hint ladder, rung 1: Extension DDL success does not prove application semantics, plans, backup compatibility, or reversibility.

## Edge cases

- Pre-existing extensions are legitimate environment state; the solution
  inspects and never drops them.
- Extension dump/restore ordering and binary availability require rehearsal.
- FDW remote schema drift can break local prepared queries.
- Embedding backfills need dual-version compatibility like schema migrations.
