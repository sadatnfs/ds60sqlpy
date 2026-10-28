-- Optional two-session fixture. Commits course-owned state deliberately.
-- Refuses to replace an existing schema. Use cleanup.sql after both sessions end.
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

CREATE SCHEMA sql_concurrency_live;

CREATE TABLE sql_concurrency_live.stock (
  sku text PRIMARY KEY,
  available integer NOT NULL CHECK (available >= 0),
  version integer NOT NULL CHECK (version > 0)
);

INSERT INTO sql_concurrency_live.stock
  VALUES ('A', 5, 1);

COMMIT;
