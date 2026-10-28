-- End both interactive transactions before running this explicit cleanup.
-- No CASCADE: unexpected extra objects cause a visible failure.
BEGIN;
DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
END
$course_target$;

SET LOCAL lock_timeout = '2s';

SET LOCAL statement_timeout = '10s';

DROP TABLE sql_concurrency_live.stock;

DROP SCHEMA sql_concurrency_live;

COMMIT;
