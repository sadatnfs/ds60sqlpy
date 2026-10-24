-- Runs only when the official PostgreSQL image initializes an empty volume.
-- These credentials are local disposable-course defaults, not production secrets.
\set ON_ERROR_STOP on
BEGIN;
DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' OR current_user <> 'ds60_admin' THEN
    RAISE EXCEPTION 'Fresh course initialization requires ds60_admin in advanced_sql_training';
  END IF;
END
$course_target$;
CREATE ROLE admin WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
  NOREPLICATION NOBYPASSRLS PASSWORD 'admin';
ALTER DATABASE advanced_sql_training OWNER TO admin;
GRANT USAGE, CREATE ON SCHEMA public TO admin;
COMMIT;
