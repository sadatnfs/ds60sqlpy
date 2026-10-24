-- Idempotent reference-data seed. It never deletes unrecognized rows.
\set ON_ERROR_STOP on

INSERT INTO pro_migration_lab.priority_levels (
    priority_code,
    display_name,
    sort_rank
)
VALUES
    ('low', 'Low priority', 1),
    ('normal', 'Normal priority', 2),
    ('high', 'High priority', 3)
ON CONFLICT (priority_code) DO UPDATE
SET display_name = EXCLUDED.display_name,
    sort_rank = EXCLUDED.sort_rank;

