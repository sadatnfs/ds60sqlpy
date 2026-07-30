# Isolated migration fixture

This fixture upgrades only the disposable `pro_migration_lab` schema. It is a
small SQL-only model of a migration runner, not a recommendation to replace a
reviewed production migration tool.

The ordered files are immutable examples:

1. `001_create_service_requests.sql` creates the baseline table and stable API
   view.
2. `002_expand_priority.sql` adds a nullable replacement column and reference
   table while preserving the old representation.
3. `003_backfill_priority.sql` migrates old rows and validates the foreign key.
4. `004_contract_priority.sql` enforces the new representation and removes the
   legacy column after compatibility checks.
5. `005_forward_fix_priority_rank.sql` changes an already-deployed rule with a
   new migration rather than editing migration 002.

`seed_priority_levels.sql` is an independently idempotent reference-data seed.
Each migration records an educational content tag. A real migration tool should
also hash file bytes and reject a changed checksum for an applied version.

From the repository root:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/fixtures/migrations/reset.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/fixtures/migrations/run_all.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/fixtures/migrations/run_all.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/fixtures/migrations/cleanup.sql
```

The second run reports metadata-based skips and leaves the same final state.
`reset.sql` and `cleanup.sql` are destructive only to the named course schema.

