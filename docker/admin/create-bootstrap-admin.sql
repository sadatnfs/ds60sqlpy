-- Explicit legacy-volume step 1. Run as the current local cluster superuser.
-- Creates a separate course administrator; never replaces an existing login.
\set ON_ERROR_STOP on
BEGIN;
DO $bootstrap$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
  IF NOT (SELECT rolsuper FROM pg_catalog.pg_roles WHERE rolname=current_user) THEN
    RAISE EXCEPTION 'A current cluster administrator must create the separate bootstrap role';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname='ds60' AND oid=10) THEN
    RAISE EXCEPTION 'The legacy ds60 login is the PostgreSQL bootstrap superuser (OID 10)'
      USING HINT = 'No administrator was created. Preserve this volume and use the side-by-side dump/restore procedure in docs/offline-app.md.';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname='ds60_admin') THEN
    RAISE NOTICE 'ds60_admin already exists; its password and attributes remain unchanged';
  ELSE
    CREATE ROLE ds60_admin WITH LOGIN SUPERUSER PASSWORD 'ds60_admin';
  END IF;
END
$bootstrap$;
COMMIT;
