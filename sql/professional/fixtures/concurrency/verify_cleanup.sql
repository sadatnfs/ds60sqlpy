DO $verify$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
  IF to_regnamespace('sql_concurrency_live') IS NOT NULL THEN
    RAISE EXCEPTION 'sql_concurrency_live remains; end transactions and run cleanup.sql';
  END IF;
END
$verify$;
