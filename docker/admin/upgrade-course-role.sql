-- Explicit legacy-volume step 2. Run through a separate administrative login.
-- Preserves course rows, learner work, and ds60's existing password.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL lock_timeout = '2s';

DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
  IF current_user='ds60' OR NOT (
    SELECT rolsuper FROM pg_catalog.pg_roles WHERE rolname=current_user
  ) THEN
    RAISE EXCEPTION 'Reconnect using a separate administrator before changing ds60 privileges';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname='ds60') THEN
    RAISE EXCEPTION 'The existing course login ds60 is missing; review this volume manually';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname='ds60' AND oid=10) THEN
    RAISE EXCEPTION 'The legacy ds60 login is the PostgreSQL bootstrap superuser (OID 10)'
      USING HINT = 'Its SUPERUSER attribute cannot be removed. Preserve this volume and use the side-by-side dump/restore procedure in docs/offline-app.md.';
  END IF;
  IF EXISTS (
    SELECT 1 FROM pg_catalog.pg_database AS database
    JOIN pg_catalog.pg_roles AS owner ON owner.oid=database.datdba
    WHERE owner.rolname='ds60'
      AND database.datname NOT IN ('advanced_sql_training','postgres','template0','template1')
  ) THEN
    RAISE EXCEPTION 'The course login owns additional databases; review them before upgrading';
  END IF;
END
$course_target$;

DO $maintenance_ownership$
DECLARE
  maintenance_database text;
BEGIN
  FOR maintenance_database IN
    SELECT database.datname FROM pg_catalog.pg_database AS database
    JOIN pg_catalog.pg_roles AS owner ON owner.oid=database.datdba
    WHERE owner.rolname='ds60' AND database.datname IN ('postgres','template0','template1')
  LOOP
    EXECUTE format('ALTER DATABASE %I OWNER TO %I', maintenance_database, current_user);
  END LOOP;
END
$maintenance_ownership$;

ALTER ROLE ds60 WITH NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;

DO $memberships$
DECLARE
  elevated_role text;
BEGIN
  FOREACH elevated_role IN ARRAY ARRAY[
    'pg_execute_server_program', 'pg_read_server_files', 'pg_write_server_files',
    'pg_read_all_data', 'pg_write_all_data'
  ] LOOP
    IF EXISTS (
      SELECT 1 FROM pg_catalog.pg_auth_members AS membership
      JOIN pg_catalog.pg_roles AS granted ON granted.oid=membership.roleid
      JOIN pg_catalog.pg_roles AS member ON member.oid=membership.member
      WHERE granted.rolname=elevated_role AND member.rolname='ds60'
    ) THEN
      EXECUTE format('REVOKE %I FROM ds60', elevated_role);
    END IF;
    IF pg_has_role('ds60',elevated_role,'MEMBER') THEN
      RAISE EXCEPTION 'Review inherited privileged membership in % before upgrading', elevated_role;
    END IF;
  END LOOP;
END
$memberships$;

ALTER DATABASE advanced_sql_training OWNER TO ds60;

GRANT USAGE, CREATE ON SCHEMA public TO ds60;

COMMIT;
