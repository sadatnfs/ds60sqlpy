-- Destructive only to the isolated course fixture schema.
\set ON_ERROR_STOP on
\echo 'Removing course-owned schema pro_migration_lab'
DROP SCHEMA IF EXISTS pro_migration_lab CASCADE;

