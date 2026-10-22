\set ON_ERROR_STOP on
DO $verify$
BEGIN
  IF current_database()<>'advanced_sql_training' OR current_user<>'ds60' THEN
    RAISE EXCEPTION 'Verify with the course ds60 login in advanced_sql_training';
  END IF;
  IF EXISTS (
    SELECT 1 FROM pg_catalog.pg_roles WHERE rolname=current_user
      AND (rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls)
  ) THEN
    RAISE EXCEPTION 'The course login still has administrative privileges';
  END IF;
  IF EXISTS (
    SELECT 1 FROM pg_catalog.pg_roles
    WHERE rolname IN ('pg_execute_server_program','pg_read_server_files','pg_write_server_files',
                     'pg_read_all_data','pg_write_all_data')
      AND pg_has_role(current_user,oid,'MEMBER')
  ) THEN
    RAISE EXCEPTION 'The course login retains an elevated predefined-role membership';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_database AS database
    JOIN pg_catalog.pg_roles AS owner ON owner.oid=database.datdba
    WHERE database.datname=current_database() AND owner.rolname=current_user
  ) THEN
    RAISE EXCEPTION 'The disposable course database must be owned by the course login';
  END IF;
  IF EXISTS (
    SELECT 1 FROM pg_catalog.pg_database AS database
    JOIN pg_catalog.pg_roles AS owner ON owner.oid=database.datdba
    WHERE owner.rolname=current_user AND database.datname<>current_database()
  ) THEN
    RAISE EXCEPTION 'The course login owns another database; review its ownership manually';
  END IF;
END
$verify$;
SELECT current_user AS course_login, current_database() AS disposable_database;
