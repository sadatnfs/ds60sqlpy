-- Run every ordered migration. This leaves pro_migration_lab for inspection.
\set ON_ERROR_STOP on
\echo 'Running migrations 001 through 005'

\ir 001_create_service_requests.sql
\ir 002_expand_priority.sql
\ir seed_priority_levels.sql
\ir 003_backfill_priority.sql
\ir 004_contract_priority.sql
\ir 005_forward_fix_priority_rank.sql
\ir verify.sql

