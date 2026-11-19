-- Prepares the NOLOGIN roles that the sql-sec-01 security lab acts as.
-- The official PostgreSQL image runs this once for an empty volume, and
-- ./classroom reruns it through the container's local administrator socket on
-- every start, so older volumes gain the roles too. Every step is idempotent.
-- The roles have no password, login or administrative attribute. The course
-- login may SET ROLE to them but gains no ADMIN OPTION and keeps NOCREATEROLE.
\set ON_ERROR_STOP on
BEGIN;
DO $security_lab_roles$
DECLARE
  lab_role text;
  course_login text;
BEGIN
  IF current_database() <> 'advanced_sql_training' OR NOT COALESCE((
    SELECT rolsuper FROM pg_catalog.pg_roles WHERE rolname = current_user
  ), false) THEN
    RAISE EXCEPTION 'Prepare the security lab roles as an administrator in advanced_sql_training';
  END IF;
  FOREACH lab_role IN ARRAY ARRAY[
    'ds60_sec_owner', 'ds60_sec_other_owner', 'ds60_sec_north',
    'ds60_sec_south', 'ds60_sec_auditor', 'ds60_sec_writer'
  ] LOOP
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = lab_role) THEN
      EXECUTE format('CREATE ROLE %I NOLOGIN', lab_role);
    END IF;
    EXECUTE format(
      'ALTER ROLE %I WITH NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION '
      'NOBYPASSRLS PASSWORD NULL',
      lab_role
    );
  END LOOP;
  -- Grant only to the limited course logins that this classroom accepts.
  FOR course_login IN
    SELECT rolname FROM pg_catalog.pg_roles
    WHERE rolname IN ('admin', 'ds60') AND rolcanlogin AND NOT rolsuper
  LOOP
    -- Objects are created as an owner, so the course login inherits the owners.
    EXECUTE format(
      'GRANT ds60_sec_owner, ds60_sec_other_owner TO %I WITH INHERIT TRUE, SET TRUE',
      course_login
    );
    -- Tenant and service roles are only adopted explicitly with SET ROLE.
    EXECUTE format(
      'GRANT ds60_sec_north, ds60_sec_south, ds60_sec_auditor, ds60_sec_writer TO %I '
      'WITH INHERIT FALSE, SET TRUE',
      course_login
    );
  END LOOP;
END
$security_lab_roles$;

COMMIT;
