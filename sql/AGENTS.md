# SQL curriculum guidance

This file extends the root [AGENTS.md](../AGENTS.md) for `sql/`.

## Dialect and environment

- Target PostgreSQL 16 or newer.
- Canonical automation uses PostgreSQL 17.
- Run against the disposable `advanced_sql_training` database.
- Use the `training` schema unless a lesson explicitly creates another disposable schema.
- Execute files with `psql -X -v ON_ERROR_STOP=1`.

Do not present MySQL, SQL Server, or Oracle syntax as runnable PostgreSQL. Portable alternatives may appear only when clearly labeled.

## Safety and state

- `postgres-60day/00_setup.sql` drops and recreates the `training` schema. Treat it as destructive.
- Never run reset or lesson DDL against production, shared, or personally valuable data.
- Daily lessons should use `BEGIN` and `ROLLBACK` unless persistence is an explicit objective.
- Do not make a later lesson depend on objects rolled back by an earlier lesson.
- Multi-part projects need an idempotent fixture or explicit, validated persistence instructions.
- Days 52–54 are the declared stateful warehouse sequence: Day 52 resets and commits the course-owned `dwh` schema, then Days 53 and 54 run in order.
- Superuser-only operations must be optional and labeled.
- The two `sql-found-*` modules precede SQL Day 1. Other named modules under
  `sql/professional/` extend the track without renumbering established days.
- Role administration, extensions, physical recovery, and replication need a
  capability check plus a useful default path when the local server cannot
  perform the optional operation.

## Lesson SQL

- Qualify ambiguous columns and use consistent aliases.
- State assumptions about NULLs, time zones, money, status codes, and ordering.
- Use deterministic ordering when examples claim a stable result.
- Explain PostgreSQL-specific operators and functions before using them.
- Keep destructive statements inside the disposable transaction or setup path.
- `EXPLAIN ANALYZE` executes a query; disclose that fact around writes.
- Performance claims require evidence from a representative environment and should not promise a universal plan.

## Documentation and solutions

- Keep the lesson script, companion guide, Markdown solution, executable solution when present, catalog-builder inputs, and generated catalog entry aligned.
- Use Markdown solutions for explanation and `.sql` solutions for executable coverage.
- Do not claim an executable solution exists when only prose is present.
- Use repository-root commands in documentation.
- Provide PowerShell-safe alternatives for pipes, file redirection, and API examples.

## Validation

Start from a freshly reset disposable database:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_verify.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
```

Then run:

```text
python scripts/course.py validate
```

Verify that:

- Setup completes without ignored errors.
- `00_verify.sql` confirms deterministic counts, coverage, chronology, totals, and foreign keys.
- Each independent lesson succeeds in a clean session.
- Rollback leaves no unexpected persistent objects.
- The Days 52–54 stateful sequence succeeds in order.
- Catalog and solution availability are accurate.

When an artifact filename, stateful group, or solution availability changes, run `python scripts/build_catalog.py` before validation.
