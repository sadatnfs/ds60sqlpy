-- sql-deep-01: complete reference queries and exact result assertions

BEGIN;
DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
END
$course_target$;
SET LOCAL TIME ZONE 'UTC';
SET LOCAL statement_timeout = '15s';

CREATE TEMP TABLE deep1_values (row_id integer PRIMARY KEY, value integer) ON COMMIT DROP;
INSERT INTO deep1_values VALUES (1,1),(2,2),(3,NULL);
CREATE TEMP TABLE deep1_blocklist (value integer) ON COMMIT DROP;
INSERT INTO deep1_blocklist VALUES (2),(NULL);
CREATE TEMP TABLE deep1_people (person_id integer PRIMARY KEY, person_name text NOT NULL) ON COMMIT DROP;
INSERT INTO deep1_people VALUES (1,'Ada'),(2,'Ben'),(3,'Cy'),(4,'Dee'),(5,'Eli');
CREATE TEMP TABLE deep1_required (skill text PRIMARY KEY) ON COMMIT DROP;
INSERT INTO deep1_required VALUES ('sql'),('python');
CREATE TEMP TABLE deep1_skills (person_id integer NOT NULL, skill text NOT NULL) ON COMMIT DROP;
INSERT INTO deep1_skills VALUES (1,'sql'),(1,'sql'),(1,'python'),(2,'sql'),(3,'python'),(4,'sql'),(4,'python'),(4,'rust');

CREATE FUNCTION pg_temp.assert_true(ok boolean, message text)
RETURNS void LANGUAGE plpgsql AS $assert$
BEGIN
  IF ok IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'Contract failed: %', message;
  END IF;
END
$assert$;

-- Exercises

-- 1. Inspect unknown and NULL-safe comparison side by side
SAVEPOINT exercise_1;
CREATE TEMP TABLE answer_1 ON COMMIT DROP AS
SELECT row_id,value,value<>2 AS not_two,
       value NOT IN(SELECT value FROM deep1_blocklist) AS not_in_block,
       value IS DISTINCT FROM 2 AS null_safe_different
FROM deep1_values ORDER BY row_id;
SELECT row_id,value,not_two,not_in_block,null_safe_different FROM answer_1 ORDER BY row_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_1) ORDER BY row_id),'[]'::jsonb) FROM answer_1) = '[{"row_id": 1, "value": 1, "not_two": true, "not_in_block": null, "null_safe_different": true}, {"row_id": 2, "value": 2, "not_two": false, "not_in_block": false, "null_safe_different": false}, {"row_id": 3, "value": null, "not_two": null, "not_in_block": null, "null_safe_different": true}]'::jsonb,'sql-deep-01 exercise 1');
ROLLBACK TO SAVEPOINT exercise_1;
RELEASE SAVEPOINT exercise_1;

-- 2. Express a known-value anti-join policy
SAVEPOINT exercise_2;
CREATE TEMP TABLE answer_2 ON COMMIT DROP AS
SELECT v.row_id,v.value FROM deep1_values AS v
WHERE v.value IS NOT NULL
  AND NOT EXISTS(SELECT 1 FROM deep1_blocklist AS b WHERE b.value=v.value)
ORDER BY v.row_id;
SELECT row_id,value FROM answer_2 ORDER BY row_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_2) ORDER BY row_id),'[]'::jsonb) FROM answer_2) = '[{"row_id": 1, "value": 1}]'::jsonb,'sql-deep-01 exercise 2');
ROLLBACK TO SAVEPOINT exercise_2;
RELEASE SAVEPOINT exercise_2;

-- 3. Distinguish empty, mixed and unknown quantified collections
SAVEPOINT exercise_3;
CREATE TEMP TABLE answer_3 ON COMMIT DROP AS
WITH cases(case_id,items) AS (VALUES
 (1,ARRAY[]::integer[]),(2,ARRAY[6,7]),(3,ARRAY[4,7]),
 (4,ARRAY[4,NULL]::integer[]),(5,NULL::integer[]))
SELECT case_id,5<ANY(items) AS any_larger,5<ALL(items) AS all_larger
FROM cases ORDER BY case_id;
SELECT case_id,any_larger,all_larger FROM answer_3 ORDER BY case_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_3) ORDER BY case_id),'[]'::jsonb) FROM answer_3) = '[{"case_id": 1, "any_larger": false, "all_larger": true}, {"case_id": 2, "any_larger": true, "all_larger": true}, {"case_id": 3, "any_larger": true, "all_larger": false}, {"case_id": 4, "any_larger": null, "all_larger": false}, {"case_id": 5, "any_larger": null, "all_larger": null}]'::jsonb,'sql-deep-01 exercise 3');
ROLLBACK TO SAVEPOINT exercise_3;
RELEASE SAVEPOINT exercise_3;

-- 4. Compare missing values under an explicit reconciliation rule
SAVEPOINT exercise_4;
CREATE TEMP TABLE answer_4 ON COMMIT DROP AS
SELECT v.row_id,v.value FROM deep1_values AS v
WHERE EXISTS(SELECT 1 FROM deep1_blocklist AS b
             WHERE b.value IS NOT DISTINCT FROM v.value)
ORDER BY v.row_id;
SELECT row_id,value FROM answer_4 ORDER BY row_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_4) ORDER BY row_id),'[]'::jsonb) FROM answer_4) = '[{"row_id": 2, "value": 2}, {"row_id": 3, "value": null}]'::jsonb,'sql-deep-01 exercise 4');
ROLLBACK TO SAVEPOINT exercise_4;
RELEASE SAVEPOINT exercise_4;

-- 5. Find people satisfying every required skill
SAVEPOINT exercise_5;
CREATE TEMP TABLE answer_5 ON COMMIT DROP AS
SELECT p.person_id,p.person_name FROM deep1_people AS p
WHERE NOT EXISTS(
 SELECT 1 FROM deep1_required AS r
 WHERE NOT EXISTS(SELECT 1 FROM deep1_skills AS s
                  WHERE s.person_id=p.person_id AND s.skill=r.skill))
ORDER BY p.person_id;
SELECT person_id,person_name FROM answer_5 ORDER BY person_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_5) ORDER BY person_id),'[]'::jsonb) FROM answer_5) = '[{"person_id": 1, "person_name": "Ada"}, {"person_id": 4, "person_name": "Dee"}]'::jsonb,'sql-deep-01 exercise 5');
ROLLBACK TO SAVEPOINT exercise_5;
RELEASE SAVEPOINT exercise_5;

-- 6. Make empty-requirement policy visible
SAVEPOINT exercise_6;
TRUNCATE deep1_required;
CREATE TEMP TABLE answer_6 ON COMMIT DROP AS
SELECT p.person_id,
 NOT EXISTS(SELECT 1 FROM deep1_required AS r
            WHERE NOT EXISTS(SELECT 1 FROM deep1_skills AS s
                             WHERE s.person_id=p.person_id AND s.skill=r.skill)) AS all_requirements,
 EXISTS(SELECT 1 FROM deep1_required)
 AND NOT EXISTS(SELECT 1 FROM deep1_required AS r
                WHERE NOT EXISTS(SELECT 1 FROM deep1_skills AS s
                                 WHERE s.person_id=p.person_id AND s.skill=r.skill)) AS nonempty_policy
FROM deep1_people AS p ORDER BY p.person_id;
SELECT person_id,all_requirements,nonempty_policy FROM answer_6 ORDER BY person_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_6) ORDER BY person_id),'[]'::jsonb) FROM answer_6) = '[{"person_id": 1, "all_requirements": true, "nonempty_policy": false}, {"person_id": 2, "all_requirements": true, "nonempty_policy": false}, {"person_id": 3, "all_requirements": true, "nonempty_policy": false}, {"person_id": 4, "all_requirements": true, "nonempty_policy": false}, {"person_id": 5, "all_requirements": true, "nonempty_policy": false}]'::jsonb,'sql-deep-01 exercise 6');
ROLLBACK TO SAVEPOINT exercise_6;
RELEASE SAVEPOINT exercise_6;

ROLLBACK;
