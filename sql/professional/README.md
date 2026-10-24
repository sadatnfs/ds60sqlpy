# PostgreSQL professional modules

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **PostgreSQL** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work. Native terminal/editor commands below are optional alternatives.


These named modules extend the numbered PostgreSQL track without renumbering
Days 1–60. They teach database responsibilities that are normally encountered
in application and production work: owning a relational model, evolving it
through reviewed migrations, and enforcing least privilege.

All runnable work targets PostgreSQL 16 or newer and the disposable
`advanced_sql_training` database. Run commands from the repository root. Never
substitute a production, shared, or personally valuable database.

## Learning path

A complete beginner starts with the small-fixture on-ramp:

1. [Reading tables and result grain](companion-guides/sql_start_01_tables_and_grain.md) teaches identity, projection, and the difference between an observation and a repeated visible value.
2. [Values, NULL, and deterministic order](companion-guides/sql_start_02_values_null_order.md) separates missing values from zero and empty text, then constructs a complete order.
3. [Query construction and debugging](companion-guides/sql_start_03_query_debugging.md) builds one clause at a time and distinguishes syntax, names, and business-logic mistakes.

Then follow historical `sql-01` through `sql-60`. Complete `sql-found-01`
after Day 15 before beginning windows on Day 16, and `sql-found-02` after
Day 39 before the operational and schema-evolution modules. These milestones
keep table design and transactions ahead of lessons that depend on them.
The existing security, routines, types, maintenance, testing, analytical,
recovery, extension, replication, and temporal modules remain available through
the generated catalog, with their direct prerequisite chains intact.

The advanced correctness path adds three focused labs:

- [Bag reconciliation and join fanout](companion-guides/sql_quality_01_bags_and_fanout.md) exposes equal-total counterexamples, duplicate multiplicity, and independent-child overcounting.
- [Cursor pagination and bounded batches](companion-guides/sql_scale_01_cursors_and_batches.md) handles timestamp ties, NULL phases, mutation cases, and the difference between a cursor and a snapshot.
- [Isolation traces and optimistic concurrency](companion-guides/sql_concurrency_01_isolation_and_versions.md) tests versioned writes and supplies a separately prepared, optional two-session visibility experiment.

Use the generated catalog for the exact inventory, ordering, levels, direct
prerequisites, and artifact paths rather than copying a second module table:

```text
python scripts/course.py catalog --track sql
```

The professional modules' default paths are deliberately single-database and offline. The extension
module detects optional packages but never installs one. The replication module
models change capture locally but never creates a publication, subscription,
replication slot, or standby. The temporal module reads `btree_gist`
availability but uses a trigger fallback, so it never enables an extension.
Optional extension and multi-node labs are operator-reviewed follow-ons, not
prerequisites.

## Running a learner script

The same command works in Windows PowerShell, macOS, and Linux:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_start_01_tables_and_grain.sql
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

## Optional shared concurrency fixture

The concurrency module's default learner and solution are single-session,
transactional models. Its guide separately documents an optional real
READ COMMITTED versus REPEATABLE READ observation using
`fixtures/concurrency/prepare.sql`, two interactive sessions, and explicit
`cleanup.sql` followed by `verify_cleanup.sql`. That optional preparation
commits its one table so the sessions can share it, refuses to overwrite an
existing schema, and needs no superuser capability. Do not treat the default
model as proof of actual blocking or concurrent visibility.
