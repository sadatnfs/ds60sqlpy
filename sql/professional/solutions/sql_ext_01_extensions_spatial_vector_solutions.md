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

- **Inputs/evidence:** For sql-ext-01 Exercise 1, complete the capability matrix written analysis and support its claims with read-only evidence from `pg_available_extensions`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-ext-01 Exercise 1, expected output: a completed the capability matrix written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `installed_version`.
- **Independent verification:** For sql-ext-01 Exercise 1, check the capability matrix written analysis against `installed_version`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-ext-01 Exercise 1, check the capability matrix written analysis against `installed_version`.
- **Clause check:** For sql-ext-01 Exercise 1, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_available_extensions` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ext-01 Exercise 1, the chosen form is justified by this lesson-specific rationale: Join a requested-extension list to `pg_available_extensions`. Evaluate another form against the concrete expected result (a completed the capability matrix written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 2 — Case-insensitive identity

A generated lower-case key centralizes one invariant and supports a unique
index. It differs from citext across operators, implicit casts, joins,
collations, Unicode case folding, and schema type contracts. Choose a documented
normalization/collation and test real-language edge cases rather than assuming
lowercase equals identity.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 2, read from `pro_extensions_lab.items`, `items_normalized_name_uk`, and `pro_extensions_lab.checked_l2`. Build the answer toward `result`; keep `result` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ext-01 Exercise 2, expected output: one row per `result`. The final columns are `result`.
- **Independent verification:** For sql-ext-01 Exercise 2, project `result` plus the raw source columns from `pro_extensions_lab.items`, `items_normalized_name_uk`, and `pro_extensions_lab.checked_l2` at each join stage; record row count and distinct `result`, then assert the final `result` values match those staged rows without unintended fanout or loss. Add one source row with a new `result`; verify the result gains exactly one row carrying that `result` value.
- **Intermediate relation check:** For sql-ext-01 Exercise 2, start with the first relation in `pro_extensions_lab.items`, `items_normalized_name_uk`, and `pro_extensions_lab.checked_l2`; after each join, record total rows and distinct `result` so the exact fanout or loss is visible.
- **Clause check:** For sql-ext-01 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, and `SELECT`. Read only those operations: begin at `pro_extensions_lab.items`, `items_normalized_name_uk`, and `pro_extensions_lab.checked_l2`, preserve one row per `result`, and finish with `result`.
- **Alternative/trade-off:** For sql-ext-01 Exercise 2, the chosen form is justified by this lesson-specific rationale: A generated lower-case key centralizes one invariant and supports a unique index. Evaluate another form against the concrete expected result (one row per `result`) and the verification above.
- **Edge case:** Add one source row with a new `result`; verify the result gains exactly one row carrying that `result` value.

## Exercise 3 — Spatial semantics

Built-in `point <-> point` returns planar units on an abstract coordinate grid.
PostGIS geometry adds SRID-aware planar operations and transformations;
geography models Earth distance. Longitude/latitude degrees are not meters and
cross dateline/poles; select SRID/type before distance/index design.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 3, read from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Build the answer toward `point`; keep `point` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ext-01 Exercise 3, expected output: one row per `point`. The final columns are `point`.
- **Independent verification:** For sql-ext-01 Exercise 3, reselect the returned keys directly from the source; require unique `point` where the expected grain is one row per key and confirm the projected `point` against `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Add one source row with a new `point`; verify the result gains exactly one row carrying that `point` value.
- **Intermediate relation check:** For sql-ext-01 Exercise 3, select `point` from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` before adding derived columns.
- **Clause check:** For sql-ext-01 Exercise 3, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ext-01 Exercise 3, the chosen form is justified by this lesson-specific rationale: Built-in `point <-> point` returns planar units on an abstract coordinate grid. Evaluate another form against the concrete expected result (one row per `point`) and the verification above.
- **Edge case:** Add one source row with a new `point`; verify the result gains exactly one row carrying that `point` value.

## Exercise 4 — Vectors

`checked_l2` rejects unequal dimensions and computes exact L2 by matching array
ordinality. This is adequate only for tiny fixtures. pgvector adds typed
dimensions/operators and exact/approximate indexes. HNSW and IVFFlat differ in
build time, memory, training/list/probe/search parameters, update behavior, and
recall. Evaluate against labeled queries and pin embedding model/version.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 4, read from `pro_extensions_lab.items`. Build the answer toward `item_name`, `planar_distance`, `vector_distance`, and `payload_sha256`; keep `planar_distance` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ext-01 Exercise 4, expected output: one row per `planar_distance`. The final columns are `item_name`, `planar_distance`, `vector_distance`, and `payload_sha256`. The final order is `vector_distance, i.item_id`.
- **Independent verification:** For sql-ext-01 Exercise 4, reselect the returned keys directly from the source; require unique `planar_distance` where the expected grain is one row per key and confirm the projected `item_name`, `planar_distance`, `vector_distance`, and `payload_sha256` against `pro_extensions_lab.items`. Add one source row with a new `planar_distance`; verify the result gains exactly one row carrying that `planar_distance` value.
- **Intermediate relation check:** For sql-ext-01 Exercise 4, check `vector_distance, i.item_id` before applying the row cap.
- **Clause check:** For sql-ext-01 Exercise 4, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_extensions_lab.items`, preserve one row per `planar_distance`, and finish with `item_name`, `planar_distance`, `vector_distance`, and `payload_sha256` ordered by `vector_distance, i.item_id`.
- **Alternative/trade-off:** For sql-ext-01 Exercise 4, the chosen form is justified by this lesson-specific rationale: `checked_l2` rejects unequal dimensions and computes exact L2 by matching array ordinality. Evaluate another form against the concrete expected result (one row per `planar_distance`) and the verification above.
- **Edge case:** Add one source row with a new `planar_distance`; verify the result gains exactly one row carrying that `planar_distance` value.

## Exercise 5 — Cryptography

Built-in SHA-256 is a deterministic integrity checksum. pgcrypto adds digest,
password `crypt`, random bytes, and PGP-style encryption, but database-side key
exposure and threat model matter. Passwords need a deliberately slow password
KDF; encryption keys should usually be managed outside the protected data and
remain recoverable under strict access.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 5, use `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-ext-01 Exercise 5, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `crypt`.
- **Independent verification:** For sql-ext-01 Exercise 5, restore into an isolated target and reconcile `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-ext-01 Exercise 5, restore into an isolated target and reconcile `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-ext-01 Exercise 5, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ext-01 Exercise 5, the chosen form is justified by this lesson-specific rationale: Built-in SHA-256 is a deterministic integrity checksum. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Exercise 6 — FDW boundary

Own foreign servers/mappings separately, keep credentials out of DDL/Git, import
only reviewed columns, test pushdown with EXPLAIN, bound timeouts/concurrency,
define transaction consistency, and materialize a local timestamped snapshot
when remote failure/freshness trade-offs permit. Reconcile source keys and
record extraction watermark.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 6, read from `pro_extensions_lab.remote_snapshot`, and `pg_catalog.pg_extension`. Build the answer toward `source_key`, `fetched_at`, and `payload`; keep `source_key` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ext-01 Exercise 6, expected output: one row per `source_key`. The final columns are `source_key`, `fetched_at`, and `payload`. The final order is `rs.source_key, rs.fetched_at DESC, rs.snapshot_id DESC`.
- **Independent verification:** For sql-ext-01 Exercise 6, reselect the returned keys directly from the source; require unique `source_key` where the expected grain is one row per key and confirm the projected `source_key`, `fetched_at`, and `payload` against `pro_extensions_lab.remote_snapshot`, and `pg_catalog.pg_extension`. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-ext-01 Exercise 6, inspect the source keys that survive `WHERE`; then check `rs.source_key, rs.fetched_at DESC, rs.snapshot_id DESC` before applying the row cap.
- **Clause check:** For sql-ext-01 Exercise 6, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_extensions_lab.remote_snapshot`, and `pg_catalog.pg_extension`, preserve one row per `source_key`, and finish with `source_key`, `fetched_at`, and `payload` ordered by `rs.source_key, rs.fetched_at DESC, rs.snapshot_id DESC`.
- **Alternative/trade-off:** For sql-ext-01 Exercise 6, the chosen form is justified by this lesson-specific rationale: Own foreign servers/mappings separately, keep credentials out of DDL/Git, import only reviewed columns, test pushdown with EXPLAIN, bound timeouts/concurrency, define transaction consistency, and materialize a. Evaluate another form against the concrete expected result (one row per `source_key`) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.

## Exercise 7 — Search

Prefix `LIKE 'post%'` can use a compatible pattern index; full-text search uses
lexemes/language; pg_trgm supports similarity and many wildcard patterns through
its `%`, distance, LIKE/ILIKE operator support. Pick the operator first, then
the matching GIN/GiST trigram operator class and measured threshold.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 7, read from `requested`, `pg_catalog.pg_available_extensions`, and `pg_catalog.pg_extension`. Build the answer toward `extension_name`, `default_version`, `installed_version`, and `installed_owner`; keep `extension_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ext-01 Exercise 7, expected output: one row per `extension_name`. The final columns are `extension_name`, `default_version`, `installed_version`, and `installed_owner`. The final order is `r.extension_name`.
- **Independent verification:** For sql-ext-01 Exercise 7, project `extension_name` plus the raw source columns from `requested`, `pg_catalog.pg_available_extensions`, and `pg_catalog.pg_extension` at each join stage; record row count and distinct `extension_name`, then assert the final `extension_name`, `default_version`, `installed_version`, and `installed_owner` values match those staged rows without unintended fanout or loss. Add one source row with a new `extension_name`; verify the result gains exactly one row carrying that `extension_name` value.
- **Intermediate relation check:** For sql-ext-01 Exercise 7, start with the first relation in `requested`, `pg_catalog.pg_available_extensions`, and `pg_catalog.pg_extension`; after each join, record total rows and distinct `extension_name` so the exact fanout or loss is visible.
- **Clause check:** For sql-ext-01 Exercise 7, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `requested`, `pg_catalog.pg_available_extensions`, and `pg_catalog.pg_extension`, preserve one row per `extension_name`, and finish with `extension_name`, `default_version`, `installed_version`, and `installed_owner` ordered by `r.extension_name`.
- **Alternative/trade-off:** For sql-ext-01 Exercise 7, the chosen form is justified by this lesson-specific rationale: Prefix `LIKE 'post%'` can use a compatible pattern index; full-text search uses lexemes/language; pg_trgm supports similarity and many wildcard patterns through its `%`, distance, LIKE/ILIKE operator support. Evaluate another form against the concrete expected result (one row per `extension_name`) and the verification above.
- **Edge case:** Add one source row with a new `extension_name`; verify the result gains exactly one row carrying that `extension_name` value.

## Exercise 8 — Extension lifecycle inventory

Join `pg_extension` to available versions and dependency catalogs; add owner,
installed/default/available version, update paths, trust, package/image source,
supported platforms, backup behavior, replica compatibility, approver, patch
owner, and tested removal/rollback.

An extension is executable code and schema objects, not a feature flag. Binary
availability on every restore/replica node matters. The executable answer only
inventories capabilities and never changes them.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 8, use `pg_extension` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-ext-01 Exercise 8, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
- **Independent verification:** For sql-ext-01 Exercise 8, restore into an isolated target and reconcile `pg_extension` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-ext-01 Exercise 8, restore into an isolated target and reconcile `pg_extension` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-ext-01 Exercise 8, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_extension` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ext-01 Exercise 8, the chosen form is justified by this lesson-specific rationale: Join `pg_extension` to available versions and dependency catalogs; add owner, installed/default/available version, update paths, trust, package/image source, supported platforms, backup behavior, replica compat. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Exercise 9 — Collation version drift

Compare recorded provider versions with current actual versions. A mismatch
means sort keys may have changed after libc/ICU updates; it does not identify
every affected index automatically.

Inventory indexes, constraints, partitions, and materialized results using that
collation; plan controlled REINDEX/refresh, conflict handling, capacity/locks,
and post-checks. Refresh version metadata only after remediation is validated.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 9, read from `pg_catalog.pg_collation`. Build the answer toward `collname`, `collprovider`, `recorded_version`, and `actual_version`; keep `collname` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ext-01 Exercise 9, expected output: one row per `collname`. The final columns are `collname`, `collprovider`, `recorded_version`, and `actual_version`. The final order is `c.collname`.
- **Independent verification:** For sql-ext-01 Exercise 9, run an anti-check that counts rows where NOT ((c.collversion IS NOT NULL AND c.collversion IS DISTINCT FROM pg_catalog.pg_collation_actual_version(c.oid))); require unique `collname` where the expected grain is one row per key and confirm the projected `collname`, `collprovider`, `recorded_version`, and `actual_version` against `pg_catalog.pg_collation`. Add one row for which `(c.collversion IS NOT NULL AND c.collversion IS DISTINCT FROM pg_catalog.pg_collation_actual_version(c.oid))` is true and one for which it is false; verify only the matching `collname` value is returned.
- **Intermediate relation check:** For sql-ext-01 Exercise 9, inspect the source keys that survive `WHERE`; then check `c.collname` before applying the row cap.
- **Clause check:** For sql-ext-01 Exercise 9, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_catalog.pg_collation`, preserve one row per `collname`, and finish with `collname`, `collprovider`, `recorded_version`, and `actual_version` ordered by `c.collname`.
- **Alternative/trade-off:** For sql-ext-01 Exercise 9, the chosen form is justified by this lesson-specific rationale: Compare recorded provider versions with current actual versions. Evaluate another form against the concrete expected result (one row per `collname`) and the verification above.
- **Edge case:** Add one row for which `(c.collversion IS NOT NULL AND c.collversion IS DISTINCT FROM pg_catalog.pg_collation_actual_version(c.oid))` is true and one for which it is false; verify only the matching `collname` value is returned.

## Exercise 10 — PostGIS nearest-resource design

Use geography point SRID 4326 (or a reviewed transformed geometry). Apply
`ST_DWithin` in meters so GiST can prefilter, then order candidates by exact
`ST_Distance` and a stable resource ID.

Validate coordinate order/range, SRID, units, empty geometry, poles,
antimeridian, and spheroid accuracy. This is design-only unless PostGIS is
already approved in an isolated environment.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 10, complete the postgis nearest written analysis and support its claims with read-only evidence from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-ext-01 Exercise 10, expected output: a completed the postgis nearest written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `st_dwithin`, and `st_distance`.
- **Independent verification:** For sql-ext-01 Exercise 10, check the postgis nearest written analysis against `st_dwithin`, and `st_distance`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-ext-01 Exercise 10, check the postgis nearest written analysis against `st_dwithin`, and `st_distance`.
- **Clause check:** For sql-ext-01 Exercise 10, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ext-01 Exercise 10, the chosen form is justified by this lesson-specific rationale: Use geography point SRID 4326 (or a reviewed transformed geometry). Evaluate another form against the concrete expected result (a completed the postgis nearest written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 11 — pgvector metric and ANN evidence

Choose L2, negative inner product, or cosine from the embedding model contract.
Normalize when required and enforce comparable model/version/dimension.

Measure exact top-k ground truth against HNSW/IVFFlat recall with real filters,
concurrency, mutations, build time, memory, disk, and latency. Tune search
parameters and retain an exact fallback; index use is not relevance evidence.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 11, read from `pro_extensions_lab.items`. Build the answer toward `item_id`, `item_name`, and `exact_l2`; keep `item_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ext-01 Exercise 11, expected output: one row per `item_id`. The final columns are `item_id`, `item_name`, and `exact_l2`. The final order is `exact_l2, i.item_id`.
- **Independent verification:** For sql-ext-01 Exercise 11, reselect the returned keys directly from the source; require unique `item_id` where the expected grain is one row per key and confirm the projected `item_id`, `item_name`, and `exact_l2` against `pro_extensions_lab.items`. Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.
- **Intermediate relation check:** For sql-ext-01 Exercise 11, check `exact_l2, i.item_id` before applying the row cap.
- **Clause check:** For sql-ext-01 Exercise 11, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_extensions_lab.items`, preserve one row per `item_id`, and finish with `item_id`, `item_name`, and `exact_l2` ordered by `exact_l2, i.item_id`.
- **Alternative/trade-off:** For sql-ext-01 Exercise 11, the chosen form is justified by this lesson-specific rationale: Choose L2, negative inner product, or cosine from the embedding model contract. Evaluate another form against the concrete expected result (one row per `item_id`) and the verification above.
- **Edge case:** Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.

## Exercise 12 — Operable FDW boundary

Use external secret storage and a narrow mapping owner with rotation rehearsal;
bound connections/timeouts and remote resources. Validate imported schema,
inspect pushdown, and monitor latency, rows, errors, and freshness.

Define transaction and retry semantics. Maintain a timestamped reconciled
last-known-good snapshot when stale local data is safer than live dependency
failure. Never commit credentials in SQL.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 12, read from `pro_extensions_lab.remote_snapshot`. Build the answer toward `source_key`, `snapshot_watermark`, and `retained_versions`; keep `source_key` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ext-01 Exercise 12, expected output: one row per `source_key`. The final columns are `source_key`, `snapshot_watermark`, and `retained_versions`. The final order is `rs.source_key`.
- **Independent verification:** For sql-ext-01 Exercise 12, independently aggregate `pro_extensions_lab.remote_snapshot` by `source_key`; require one output row for every distinct `source_key` tuple and compare `snapshot_watermark`, and `retained_versions` tuple by tuple. Tie two rows on `rs.source_key` and give them different `rs.source_key` values; verify `rs.source_key` chooses a stable first/last row.
- **Intermediate relation check:** For sql-ext-01 Exercise 12, confirm the groups are `source_key`; then check `rs.source_key` before applying the row cap.
- **Clause check:** For sql-ext-01 Exercise 12, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_extensions_lab.remote_snapshot`, preserve one row per `source_key`, and finish with `source_key`, `snapshot_watermark`, and `retained_versions` ordered by `rs.source_key`.
- **Alternative/trade-off:** For sql-ext-01 Exercise 12, the chosen form is justified by this lesson-specific rationale: Use external secret storage and a narrow mapping owner with rotation rehearsal; bound connections/timeouts and remote resources. Evaluate another form against the concrete expected result (one row per `source_key`) and the verification above.
- **Edge case:** Tie two rows on `rs.source_key` and give them different `rs.source_key` values; verify `rs.source_key` chooses a stable first/last row.

## Exercise 13 — Extension supply-chain review

Require approved publisher/source, pinned checksums, reproducible or trusted
packages, dependency/SBOM and CVE/license review, native-code privilege analysis,
platform support, patch owner/SLA, backup/restore, and removal rehearsal.

Compiling successfully is not approval. Native code runs inside the database
process; prefer a maintained external service or built-in fallback when
lifecycle ownership is absent.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 13, read from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Build the answer toward `supply_chain_answer`; keep `supply_chain_answer` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ext-01 Exercise 13, expected output: one row per `supply_chain_answer`. The final columns are `supply_chain_answer`.
- **Independent verification:** For sql-ext-01 Exercise 13, reselect the returned keys directly from the source; require unique `supply_chain_answer` where the expected grain is one row per key and confirm the projected `supply_chain_answer` against `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.
- **Intermediate relation check:** For sql-ext-01 Exercise 13, select `supply_chain_answer` from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` before adding derived columns.
- **Clause check:** For sql-ext-01 Exercise 13, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ext-01 Exercise 13, the chosen form is justified by this lesson-specific rationale: Require approved publisher/source, pinned checksums, reproducible or trusted packages, dependency/SBOM and CVE/license review, native-code privilege analysis, platform support, patch owner/SLA, backup/restore,. Evaluate another form against the concrete expected result (one row per `supply_chain_answer`) and the verification above.
- **Edge case:** Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.

## Exercise 14 — Upgrade rehearsal

Restore a representative disposable database with old binaries, inventory
dependent objects/functions/plans and data checks, then follow a supported
update path. Run catalog, correctness, application, and performance canaries.

Confirm dump/restore and replica compatibility. Many upgrades are not reversibly
transactional, so rollback may require traffic fencing and restore rather than
an attempted downgrade.

### Reasoning and verification

- **Inputs/evidence:** For sql-ext-01 Exercise 14, use `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-ext-01 Exercise 14, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
- **Independent verification:** For sql-ext-01 Exercise 14, restore into an isolated target and reconcile `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-ext-01 Exercise 14, restore into an isolated target and reconcile `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-ext-01 Exercise 14, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ext-01 Exercise 14, the chosen form is justified by this lesson-specific rationale: Restore a representative disposable database with old binaries, inventory dependent objects/functions/plans and data checks, then follow a supported update path. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Edge cases

- Pre-existing extensions are legitimate environment state; the solution
  inspects and never drops them.
- Extension dump/restore ordering and binary availability require rehearsal.
- FDW remote schema drift can break local prepared queries.
- Embedding backfills need dual-version compatibility like schema migrations.
