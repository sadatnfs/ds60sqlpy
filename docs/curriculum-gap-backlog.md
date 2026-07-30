# Curriculum gap backlog

**Status:** implemented; all 25 audited gaps have runnable learner and solution artifacts.  
**Reviewed:** 2026-07-30  
**Audience:** curriculum maintainers, learners choosing an advanced path, and Codex agents planning future changes.

DS60 now has 70 Python/data-science lessons, 72 PostgreSQL lessons, and a
12-lesson Python/PostgreSQL engineering bridge. This backlog records the
*dedicated, executable learning experiences* identified by the 2026-07 audit
and the implementation state of each one. A term mentioned in a guide does not
count as coverage unless a learner can practise it, check the result, and
review a separate solution.

This is a finite planning backlog, not a claim that any repository can teach literally every feature of Python, PostgreSQL, and their ecosystems. The core course remains beginner-friendly and offline after the documented bootstrap. Specializations stay opt-in.

## How to use this backlog

- [x] means implemented with artifacts, catalog entries, navigation, and
  validation. A reopened item should return to [ ] and explain the regression
  or missing evidence.
- **P0** closes a material professional-skill gap and should be implemented before expanding into more optional topics.
- **P1** is a worthwhile advanced extension after P0.
- **P2** is a specialization, not a prerequisite for course completion.
- “Revise” means strengthen the named lesson(s) instead of creating duplicate content. “New” means a separately navigable lesson or tightly scoped mini-module is warranted.

Do not renumber existing Days 1–60. A future implementer should select stable catalog IDs and place additions at clear checkpoints, as described in [the curriculum map](curriculum-map.md#adding-lessons-beyond-60).

## Evidence and non-duplication notes

The current course is stronger than a title-only audit suggests:

| Existing coverage | Consequence for this backlog |
| --- | --- |
| Python Day 10 teaches parametrization, pytest.raises, and tmp_path; Bridge Day 5 adds database fakes and rollback fixtures. | A testing extension must start with fixture design, isolation boundaries, and property-based testing—not repeat assertions. |
| Bridge Day 7 uses asyncio TaskGroup, cancellation, and bounded database concurrency. | A Python concurrency lesson must cover the choice among async I/O, threads, and processes, plus queues and Windows process-start behavior. |
| Python Day 18 explicitly identifies Parquet as engine-dependent; Days 52–56 cover Dask, MLflow, and orchestration. | A new data-engine lesson should teach the local Parquet/Arrow/DuckDB boundary, not another pandas introduction. |
| Python Day 44 creates a local FastAPI service but explicitly defers authentication, rate limiting, TLS, secrets, audit logs, and rollback. | Client reliability and service hardening remain valid gaps. |
| SQL Day 28 teaches JSON/JSONB basics and Day 29 includes a small full-text-search exercise. | A dedicated PostgreSQL types/search lesson can go beyond an isolated prompt. |
| SQL Days 32–33 teach B-tree, composite, covering, and partial indexes; Day 39 covers SKIP LOCKED and advisory locks. | Index maintenance/type selection and queue-operation patterns need only extension work, not a restart. |
| SQL Day 43 teaches logical COPY and client-side \copy staging and explicitly excludes production PITR; Day 44 safely reads pg_stat_activity and optional pg_stat_statements. | Disaster recovery and deeper operations can be added without weakening the existing safe defaults. |

The external references below helped calibrate the scope. They are design references, not a requirement that learners browse while studying:

- [Python concurrency overview](https://docs.python.org/3/library/concurrency.html) and [structured asyncio tasks](https://docs.python.org/3/library/asyncio-task.html) distinguish CPU-bound, I/O-bound, cooperative, and preemptive work.
- The [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) defines a practical pyproject.toml/build/distribution workflow.
- PostgreSQL’s [data-definition chapter](https://www.postgresql.org/docs/18/ddl.html) groups constraints, privileges, row security, schemas, and table changes; its [constraints section](https://www.postgresql.org/docs/18/ddl-constraints.html) makes clear why integrity belongs in the schema.
- PostgreSQL documents [routines](https://www.postgresql.org/docs/18/xproc.html), [index types](https://www.postgresql.org/docs/18/indexes-types.html), [JSON types](https://www.postgresql.org/docs/current/datatype-json.html), [full-text-search types](https://www.postgresql.org/docs/current/datatype-textsearch.html), [COPY](https://www.postgresql.org/docs/18/sql-copy.html), and [point-in-time recovery](https://www.postgresql.org/docs/18/continuous-archiving.html).

## P0 — implemented professional foundations

### Python and data engineering

- [x] **PY-PRO-01 — Package engineering and local release workflow** *(new; after Python Day 15)*

  Teach a src layout; the project, build-system, and tool tables in pyproject.toml; dependency groups and environment markers; console-script entry points; wheels versus source distributions; and a clean local install/test. Keep publishing to a public package index out of the default exercise. The existing modules, tooling, and capstone lessons mention parts of this workflow but do not take a learner from source tree to a verified artifact.

  **Done when:** an offline fixture project builds a wheel, installs into a fresh local target, exposes a command, and proves that its installed import rather than the working tree is used.

- [x] **PY-PRO-02 — Concurrency and parallelism decision lab** *(new; after Python Day 15 and before/alongside Bridge Day 7)*

  Teach the distinction between concurrency and parallelism; I/O-bound versus CPU-bound work; asyncio, ThreadPoolExecutor, and ProcessPoolExecutor; cancellation, timeout, backpressure, queues, shared-state hazards, and failure propagation. Include Windows spawn and main-guard behaviour. Reuse Bridge Day 7 only as the database-specific follow-on.

  **Done when:** deterministic local workloads demonstrate why the wrong model is slower or unsafe, bounded work never exceeds its declared limit, and cancellation cleans up without hanging a notebook or PowerShell session.

- [x] **PY-DATA-01 — Columnar data, Arrow, and embedded analytical SQL** *(new; after Python Day 23 or Day 30)*

  Teach CSV versus Parquet trade-offs, schema and null preservation, partition-aware layout, and a small local DuckDB query over Parquet. Explain predicate/column pushdown as an observed plan or measured result, not magic. PyArrow/DuckDB must be an explicit optional profile with a deterministic small local fixture and a pandas-only fallback.

  **Done when:** a learner writes and reads Parquet locally, validates a schema round trip, queries it with SQL without a server, and can say when CSV is the more portable choice.

- [x] **PY-SVC-01 — Reliable HTTP clients and external-service boundaries** *(new; after Python Day 15; pairs with Bridge Days 3–4)*

  Teach timeouts, status/error classification, pagination, retry eligibility, exponential backoff with jitter, rate limits, idempotency keys, request correlation IDs, and safe authentication configuration. The entire exercise should use a local fake server or injected transport; no public API key or network account is needed.

  **Done when:** tests prove that only safe failures retry, pagination stops, secrets never appear in logs, and a timeout/error reports enough context for diagnosis without exposing credentials.

### PostgreSQL foundations and application safety

- [x] **SQL-FOUND-01 — Relational design, DDL, and integrity constraints** *(new foundation module before SQL Day 1)*

  The SQL track starts with querying a supplied schema. Add an intentional schema-design lesson covering table grain, cardinality, keys, NOT NULL, CHECK, UNIQUE, primary and foreign keys, defaults, identities/generated columns, NULL semantics, and normalization versus deliberate denormalization. Use a small domain that learners model from requirements before they query it.

  **Done when:** a learner can create a normalized schema, load valid rows, predict and observe constraint failures, and explain why a constraint rather than application code protects a stated invariant.

- [x] **SQL-FOUND-02 — Versioned schema migrations and safe evolution** *(new; after SQL-FOUND-01 and before advanced operations)*

  Teach immutable ordered migrations, migration metadata, idempotent seed boundaries, expand–migrate–contract changes, data backfills, compatibility, transactional DDL limits, and forward fixes versus unsafe rollback. The existing capstones correctly warn about reviewed migrations but do not give a learner a controlled migration workflow.

  **Done when:** a clean disposable database upgrades through multiple migrations, verification queries prove its final version and invariants, and a simulated application remains compatible during an additive change.

- [x] **SQL-SEC-01 — Schemas, roles, privileges, and row-level security** *(new advanced module; after SQL-FOUND-01 and SQL Day 39)*

  Teach role ownership, GRANT/REVOKE, schema USAGE and search_path, default privileges, least privilege, security-invoker/definer boundaries, and row-level-security policy tests. A learner must see both an allowed and a denied action. The default course database should remain disposable; a capability check and read-only explanation are required where local PostgreSQL does not allow role administration.

  **Done when:** two disposable roles demonstrably see different permitted rows/actions, policies are tested as those roles, and the guide explains why table owners and superusers are special cases.

## P1 — implemented advanced extensions

### Python

- [x] **PY-TEST-01 — Test architecture, doubles, and generative testing** *(new; after Python Day 10 and Bridge Day 5)*

  Add fixture scope/lifetime, monkeypatch for environment and clock seams, mock-versus-fake choice, contract tests at I/O boundaries, property-based testing, and failure shrinking. Use only local fixtures and explicit seeds where randomness is not the subject.

- [x] **PY-LANG-01 — Advanced typing and the Python data model** *(new elective core; after Python Day 12 and Bridge Day 2)*

  Cover generics, Protocol, TypedDict, overloads, variance at a practical level, iterator/context-manager protocols, descriptors, MRO, and the limits of runtime versus static contracts. Keep metaclasses as a bounded survey, not a default design pattern.

- [x] **PY-STATS-01 — Resampling, experiments, and causal boundaries** *(new; after Python Day 32)*

  Build bootstrap and permutation intervals/tests, effect sizes, power/sample planning, multiple-comparison control, A/B-test design, randomization checks, sequential-peeking risk, and the difference between experimental and observational claims. Existing Day 32 warns about several of these risks; this addition makes the decisions executable.

- [x] **PY-ML-01 — Reproducible data/model delivery** *(revise Days 53–55 or add a cumulative lab)*

  Strengthen artifact lineage with data snapshot identifiers/content hashes, environment and feature-schema compatibility, model registry stages, promotion/rollback evidence, and a small compatibility test. This should extend local MLflow and container material rather than require a cloud account.

- [x] **PY-SVC-02 — Service hardening and observability** *(cumulative lab after Python Day 55 and Bridge Day 8)*

  Cover health/readiness semantics, structured logs, request IDs, metrics, bounded concurrency, configuration validation, trusted artifact loading, authentication/authorization design, rate-limit policy, and a local incident drill. It should explicitly distinguish a local development example from an Internet-facing deployment.

### PostgreSQL

- [x] **SQL-PROG-01 — Functions, procedures, and triggers** *(new; after SQL-FOUND-02)*

  Teach when declarative constraints or application code are safer; SQL and PL/pgSQL routines; routine volatility/security attributes; row versus statement triggers; auditing; transition tables; and trigger tests. Include the difference between a query function and a procedure’s transaction behaviour. Avoid dynamic SQL unless identifiers are validated and quoted.

- [x] **SQL-TYPES-01 — PostgreSQL-native types and searchable documents** *(new; after SQL Day 29)*

  Deepen arrays, ranges/multiranges, domains, enums, UUIDs, JSONB/jsonpath, tsvector/tsquery, ranking, and GIN/trigram trade-offs. Day 28 and a Day 29 prompt are prerequisites; this module should concentrate on modelling and measured query behavior, not duplicate basic JSON extraction.

- [x] **SQL-OPS-01 — Index types, statistics, and maintenance lifecycle** *(new; after SQL Day 35)*

  Extend B-tree coverage with GIN, GiST, SP-GiST, and BRIN selection; expression and operator-class compatibility; ANALYZE, extended statistics, VACUUM/autovacuum, bloat, visibility, plan regression, and index maintenance cost. All interventions must run only against the disposable course database.

- [x] **SQL-OPS-02 — Backup, restore, and recovery rehearsals** *(new; after SQL Day 43)*

  Add pg_dump/pg_restore formats and restore verification before introducing physical base backups, WAL archiving, point-in-time recovery, retention, RPO, RTO, and recovery drills. The default runnable path can remain a logical restore; PITR should be a documented optional Compose-only lab with clear disk/time requirements.

- [x] **SQL-TEST-01 — SQL tests, migration checks, and data contracts** *(new; after SQL-FOUND-02 and SQL Day 42)*

  Teach repeatable test schemas, rollback isolation, invariant and reconciliation queries, migration regression tests, fixture ownership, and contract checks between a producer and table. Use the course’s 00_verify.sql approach as a starting point; do not require a third-party test framework.

- [x] **SQL-ANALYTICS-01 — Reusable analytical-query patterns lab** *(new practice pack after SQL Day 30)*

  Practise gaps-and-islands, sessionization, funnel steps, as-of joins, attribution windows, cohort retention, deduplication, and slowly changing facts with explicit grain and time-zone assumptions. The window/CTE lessons provide the syntax; this lab develops pattern recognition and validation.

### Cross-track

- [x] **BRIDGE-OPS-01 — Database migration delivery and application observability** *(new cumulative bridge lab)*

  Combine a versioned schema migration, Psycopg parameter safety, transactional retry policy, structured logs/metrics, health checks, and an evidence-based rollback/forward-fix decision. It should exercise a local Compose database and fake-backed unit tests so the learner sees the connection between Python release practices and PostgreSQL change safety.

## P2 — implemented opt-in specialization lanes

- [x] **AI application engineering:** embeddings, retrieval, structured output, evaluation datasets, prompt-injection/data-leakage boundaries, cost/latency, and deterministic local test doubles. Do not make a hosted model account a default requirement.
- [x] **Analytics engineering:** semantic models, lineage, data contracts, and a local dbt-style project. Keep it separate from portable SQL fundamentals.
- [x] **PostgreSQL extensions and spatial/vector data:** pg_trgm, citext, pgcrypto, PostGIS, pgvector, and foreign data wrappers. Use a dedicated disposable image/profile and document extension version support.
- [x] **Replication, change data capture, and high availability:** physical and logical replication, publications/subscriptions, replication slots/WAL retention, failover concepts, and consumer idempotency. This is operational specialization work, not a laptop-default prerequisite.
- [x] **Temporal and domain modelling:** bitemporal facts, range exclusion constraints, ledger/audit patterns, and policy-driven retention. Tie each example to a concrete domain rather than presenting it as universal design.
- [x] **Performance-intensive Python:** memory profiling, vectorization versus loops, process-transfer costs, native extensions/FFI boundaries, and a measurement-first optimization case study. Day 11 remains the prerequisite.

## Completed implementation order

1. **Make unseen foundations visible:** SQL-FOUND-01, SQL-FOUND-02, and PY-PRO-01. These give learners a schema and a package they can own before more sophisticated projects.
2. **Make local systems reliable:** PY-SVC-01, PY-PRO-02, and PY-DATA-01. Each can run using deterministic local services/files after bootstrap.
3. **Teach database responsibility:** SQL-SEC-01, SQL-PROG-01, SQL-TYPES-01, SQL-OPS-01, and SQL-TEST-01.
4. **Add cumulative professional practice:** PY-TEST-01, PY-STATS-01, PY-ML-01, PY-SVC-02, SQL-OPS-02, SQL-ANALYTICS-01, and BRIDGE-OPS-01.
5. **Offer P2 lanes only after the shared core remains easy to navigate.**

All five waves are now represented by stable catalog entries. The
implementation also added `bridge-jupyter-01`, a focused PostgreSQL-in-Jupyter
module requested during delivery. See
[professional paths](professional-paths.md) for the artifact-by-artifact
index and exact prerequisite routes.

## Maintenance rules for every backlog item

- Decide whether the item is a new stable catalog ID, a revision to an existing lesson, or a multi-session project before creating artifacts.
- Follow [content authoring](content-authoring.md): guide, learner artifact, separate solution, prerequisites, exercises, self-check, diagnostics, and explicit dependency/network metadata must agree.
- Supply Windows PowerShell and macOS/Linux commands whenever they differ.
- Default execution must work offline after the documented bootstrap. Optional engines, images, models, and admin privileges need a local fallback or a clear capability boundary.
- Run dangerous database work only against the disposable course database. Do not grant broad privileges, change local server configuration, or enable extensions merely to make a lesson pass.
- Do not use live credentials, public service keys, private data, or hidden caches in examples or validation fixtures.
- Regenerate the catalog and run the repository validation described in [AGENTS.md](../AGENTS.md) before marking an item done.

## Implementation decision record

The course was deliberately **not** renumbered into a “90-day” linear
sequence. A small relational-foundations path now precedes SQL Day 1, while
named professional and advanced modules sit at relevant checkpoints. Learners
can choose a Python/data, SQL/database, or integrated engineering path without
being forced through every specialization.

Future changes should preserve the stable IDs, executable separation between
learner and solution artifacts, offline default, and explicit capability
boundaries established by this implementation.
