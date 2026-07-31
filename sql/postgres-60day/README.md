# PostgreSQL track

This track contains 60 ordered PostgreSQL lessons, companion guides, and
projects. New learners start with Day 1. Two named relational-engineering
modules form the milestones between Days 15–16 and Days 39–40, and ten
professional modules extend the shared core. The number is a sequence, not a
deadline.

Start at the repository [README](../../README.md), and run every command from the repository root.

## Requirements

- PostgreSQL 16 or newer
- PostgreSQL client tools, including `psql`
- PostgreSQL 17 for the canonical Docker Compose environment

Use the operating-system guide for native installation:

- [Windows](../../docs/setup/windows.md)
- [macOS](../../docs/setup/macos.md)
- [Linux](../../docs/setup/linux.md)

## Safety

> [!WARNING]
> `sql/postgres-60day/00_setup.sql` drops and recreates the course-owned `training` schema. Run it only in the disposable `advanced_sql_training` database. Never point it at production, shared, or valuable data.

Daily lessons normally start a transaction and end with `ROLLBACK`. The explicit
exception is the warehouse project: Day 52 drops and rebuilds the course-owned
`dwh` schema and commits it so Days 53 and 54 can use it. Run those three days
in order. Do not remove `ROLLBACK` merely to make any other undeclared
dependency work.

## Option A: Canonical Docker Compose environment

This is the most reproducible route across operating systems:

```text
docker compose up -d postgres
docker compose run --rm sql-runner -f sql/postgres-60day/00_setup.sql
docker compose run --rm sql-runner -f sql/postgres-60day/00_verify.sql
docker compose run --rm sql-runner -f sql/postgres-60day/day01_select_where_orderby.sql
```

The Compose environment uses a local-only course role, password, database, and persistent volume. Stop containers without deleting the training volume:

```text
docker compose down
```

Deleting the volume is a destructive reset and is not required for normal lessons.

## Option B: Native PostgreSQL

Create `advanced_sql_training` using your OS guide, then reset and verify:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_verify.sql
```

Your OS guide shows the correct host and role flags. macOS and Linux installations often use a role matching the operating-system username; do not create an unnecessary `postgres` superuser merely to copy an old command.

The seed is deterministic: relationships and categorical values are derived
from row numbers, while dates remain relative to the day setup runs so recent
date exercises stay useful. `00_verify.sql` fails immediately if expected
coverage, chronology, totals, or foreign-key relationships are broken.
The seed deliberately leaves BR as an event-only market and products 276–300
unsold, giving outer joins, `EXCEPT`, and `NOT EXISTS` visible examples.

## Cross-platform course CLI

With `psql` on `PATH`, the course CLI avoids shell-specific pipes:

```text
python scripts/course.py sql setup --yes
python scripts/course.py sql run 1
```

The explicit `--yes` acknowledges that setup resets the training schema. Override the default local Compose URL with `DS60_DATABASE_URL` or `--database`.

Run all lessons only when the database has been prepared for the full sequence:

```text
python scripts/course.py sql all --reset
```

After attempting the exercises, run the complete executable answer track with
the same fail-fast, state-aware runner:

```text
python scripts/course.py sql solutions --reset
```

Both `--reset` commands recreate the disposable `training` schema first.

## Study a lesson

1. Read the matching [companion guide](companion-guides/README.md).
2. Run the learner SQL file with stop-on-error behavior.
3. Inspect results and query plans where requested.
4. Attempt exercises in your own scratch file or transaction.
5. Read the separate solution only after an honest attempt.

If you are new to relational databases, begin with Day 1 and the supplied
training schema. Add the named relational-engineering modules only after their
declared prerequisites:

- after Day 15: [relational design guide](../professional/companion-guides/sql_found_01_relational_design.md)
  and [learner SQL](../professional/lessons/sql_found_01_relational_design.sql);
- after Day 39 and relational design: [versioned migrations guide](../professional/companion-guides/sql_found_02_versioned_migrations.md)
  and [learner SQL](../professional/lessons/sql_found_02_versioned_migrations.sql).

Run a named module through the cross-platform course CLI:

```text
python scripts/course.py sql run-id sql-found-01
python scripts/course.py sql run-id sql-found-02
```

Then continue with:

- [Day 1 guide](companion-guides/day01_select_where_orderby.md)
- [Day 1 SQL](day01_select_where_orderby.sql)
- [Day 1 explanation](solutions/day01_solutions.md)
- [Day 1 executable solution](solutions/day01_solutions.sql)

Native example:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
```

`-X` ignores personal `psqlrc` settings; `ON_ERROR_STOP=1` prevents later statements from hiding the first error.

## Track map

- Foundations: relational design, integrity constraints, and versioned schema
  migration
- Days 1–15: relational querying, joins, subqueries, DML, functions, and a report project
- Days 16–30: windows, CTEs, recursion, pivots, JSON/XML, patterns, and a project
- Days 31–45: plans, indexes, optimization, partitioning, transactions, locks, quality, and operations
- Days 46–60: e-commerce, finance, data warehouse, BI, and capstone projects
- Professional modules: roles and row security, routines and triggers,
  PostgreSQL-native types and search, physical design and maintenance, SQL
  contracts, analytical patterns, recovery, extensions, replication/CDC, and
  temporal modelling

See the [professional paths](../../docs/professional-paths.md), the
[curriculum map](../../docs/curriculum-map.md), or:

```text
python scripts/course.py catalog --track sql
```

## Artifact coverage

- Learner SQL scripts: 72 (two foundations, Days 1–60, and ten professional modules)
- Companion guides: 72
- Markdown solutions: 72
- Executable solution SQL: 72

Use the catalog for the exact learner, guide, and solution paths.

## Connect PostgreSQL with Python

After SQL Day 15 and Python Day 15, the optional
[engineering bridge](../../bridge/README.md) teaches parameterized Psycopg
queries, transaction and retry ownership, database test doubles, ETL,
concurrency, and production failure recovery.

## Progress and Codex

```text
python scripts/course.py progress show
python scripts/course.py progress complete sql-01 --notes "Explained filtering and query order."
```

Tutor prompt:

```text
Use $guide-ds60sqlpy-learning to guide SQL Day 1. Use the disposable training database, give hints before solutions, and explain my first failing statement.
```

See [Learning with Codex](../../docs/learning-with-codex.md).

## Troubleshooting and validation

- [Troubleshooting](../../docs/troubleshooting.md)
- [Validation](../../docs/validation.md)

Run:

```text
python scripts/course.py validate
```

Structural validation is not a substitute for executing SQL against PostgreSQL.
