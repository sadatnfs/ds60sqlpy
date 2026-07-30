# PostgreSQL professional modules

These named modules extend the numbered PostgreSQL track without renumbering
Days 1–60. They teach database responsibilities that are normally encountered
in application and production work: owning a relational model, evolving it
through reviewed migrations, and enforcing least privilege.

All runnable work targets PostgreSQL 16 or newer and the disposable
`advanced_sql_training` database. Run commands from the repository root. Never
substitute a production, shared, or personally valuable database.

## Learning path

| Module | Level | Catalog prerequisites | Start here | What you will practise |
| --- | --- | --- | --- | --- |
| `sql-found-01` | Foundation | None | [Relational design guide](companion-guides/sql_found_01_relational_design.md) | Grain, cardinality, keys, constraints, generated values, NULL uniqueness, and normalization decisions |
| `sql-found-02` | Intermediate | `sql-found-01` | [Migration guide](companion-guides/sql_found_02_versioned_migrations.md) | Ordered immutable migrations, metadata, seeds, expand–migrate–contract, backfills, verification, and forward fixes |
| `sql-sec-01` | Advanced | `sql-found-02`, `sql-39` | [Security guide](companion-guides/sql_sec_01_roles_privileges_rls.md) | Ownership, schema access, grants, default privileges, safe execution context, and row-level security |
| `sql-prog-01` | Advanced | `sql-found-02` | [Routines and triggers guide](companion-guides/sql_prog_01_routines_triggers.md) | Functions, procedures, volatility/security attributes, row/statement triggers, transition tables, and audit tests |
| `sql-types-01` | Advanced | `sql-29` | [Native types and search guide](companion-guides/sql_types_01_native_types_search.md) | Domains, enums, UUIDs, arrays, ranges, JSONB/JSONPath, full-text search, GIN, and GiST |
| `sql-ops-01` | Advanced | `sql-35`, `sql-types-01` | [Index and maintenance guide](companion-guides/sql_ops_01_indexes_statistics_maintenance.md) | B-tree, GIN, GiST, SP-GiST, BRIN, extended statistics, VACUUM/ANALYZE, and index lifecycle |
| `sql-test-01` | Advanced | `sql-found-02`, `sql-42` | [SQL contracts and tests guide](companion-guides/sql_test_01_contracts_migrations.md) | Fail-fast assertions, fixtures, schema contracts, migration regressions, invariants, and reconciliation |
| `sql-analytics-01` | Advanced | `sql-30`, `sql-test-01` | [Analytical patterns guide](companion-guides/sql_analytics_01_query_patterns.md) | Deduplication, sessions, gaps/islands, funnels, attribution, as-of joins, and cohort retention |
| `sql-ops-02` | Advanced | `sql-43`, `sql-ops-01` | [Backup and recovery guide](companion-guides/sql_ops_02_backup_restore_recovery.md) | Logical restore verification, RPO/RTO, physical backups, WAL, PITR, retention, and recovery rehearsals |
| `sql-ext-01` | Advanced specialization | `sql-types-01`, `sql-ops-01` | [Extensions, spatial, and vector guide](companion-guides/sql_ext_01_extensions_spatial_vector.md) | Extension governance, built-in fallbacks, text search, planar spatial data, exact vector distance, cryptographic hashes, and FDW boundaries |
| `sql-repl-01` | Advanced specialization | `sql-ops-02`, `sql-prog-01`, `sql-test-01` | [CDC, replication, and high-availability guide](companion-guides/sql_repl_01_cdc_high_availability.md) | Transactional outbox, idempotent consumers, ordering, physical/logical replication boundaries, failover, and recovery objectives |
| `sql-temporal-01` | Advanced specialization | `sql-found-01`, `sql-types-01`, `sql-prog-01`, `sql-test-01`, `sql-39` | [Temporal and domain-modelling guide](companion-guides/sql_temporal_01_domain_modelling.md) | Valid/system time, ranges, overlap enforcement, corrections, immutable ledgers, reversals, retention, and legal holds |

Complete `sql-found-01` before the numbered SQL track if you want to design the
tables that later lessons query. Complete `sql-found-02` after relational
foundations. Attempt `sql-sec-01` after the transaction and locking material in
SQL Day 39.

The P1 modules are checkpoint-based rather than one rigid sequence. Follow the
direct prerequisites in the table; numbered days are sequential, so a later
day also includes its earlier-day background. The P2 specializations then
build on the named operational, programming, and test modules shown above.

Their default paths are deliberately single-database and offline. The extension
module detects optional packages but never installs one. The replication module
models change capture locally but never creates a publication, subscription,
replication slot, or standby. The temporal module reads `btree_gist`
availability but uses a trigger fallback, so it never enables an extension.
Optional extension and multi-node labs are operator-reviewed follow-ons, not
prerequisites.

## Running a learner script

The same command works in Windows PowerShell, macOS, and Linux:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_found_01_relational_design.sql
```

Replace the filename with the module you are studying. The relational-design
lesson rolls back its schema. The security lesson either rolls back its roles
and schema or prints a safe instructional skip when the connected role cannot
administer roles. Every P1 learner and solution script rolls back its lab
schema. The operations lessons inspect settings/statistics but do not change
host configuration, enable extensions, run VACUUM, create backup files, or
perform cluster recovery.

The migration lesson uses the isolated `pro_migration_lab` schema. Its learner
script resets that schema, runs every migration, verifies the result, and
removes the schema on normal completion:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_found_02_versioned_migrations.sql
```

To inspect the fixture between steps, run its files directly:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/fixtures/migrations/reset.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/fixtures/migrations/run_all.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/fixtures/migrations/verify.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/fixtures/migrations/cleanup.sql
```

`reset.sql` and `cleanup.sql` drop only the course-owned
`pro_migration_lab` schema. The second command intentionally leaves that
isolated schema in place so you can rerun the migration runner and observe
metadata-based skips; always run the cleanup command afterward.

Maintainers can execute the six P1 learner/solution pairs and a final cleanup
assertion with:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/tests/run_p1.sql
```

The test runner invokes no optional dump, container, VACUUM, extension, or
server-administration command.

Run the three P2 learner/solution pairs and the same cleanup assertion with:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/tests/run_p2.sql
```

This runner is also safe for the default local database: it performs only
read-only capability inspection outside transaction-scoped labs and leaves
extensions, replication configuration, roles, and the filesystem unchanged.

## Solutions and safe experimentation

Attempt the commented exercises before opening `solutions/`. Every executable
solution cleans up its normal-run objects. Keep `-X` so personal `psql`
configuration cannot alter a lesson, and keep `ON_ERROR_STOP=1` so unexpected
errors stop immediately.

Default SQL work needs no network access after PostgreSQL is installed. The
optional physical/PITR specialization may require a one-time container-image
pull and explicit operator approval; it is documentation-only in this track.
No connection string or password belongs in these files. If `psql` prompts for
credentials, use the local authentication method from the operating-system
setup guide; do not save secrets in the repository.
