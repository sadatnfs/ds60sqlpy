-- sql-deep-01: NULL-Aware Quantification, Anti-Joins, and Relational Division
-- Guide: sql/professional/companion-guides/sql_deep_01.md
-- Use the complete file in the disposable advanced_sql_training database.

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

-- Worked example 1
SELECT 'ordinary_inequality' AS comparison, (NULL::integer <> 2) AS result
UNION ALL
SELECT 'null_safe_distinction', (NULL::integer IS DISTINCT FROM 2)
ORDER BY comparison;

-- Worked example 2
SELECT 'empty_array' AS case_name,
       5 < ANY(ARRAY[]::integer[]) AS any_larger,
       5 < ALL(ARRAY[]::integer[]) AS all_larger;

-- Exercises
-- Write attempts in your ignored working copy before the final ROLLBACK.

-- 1. Inspect unknown and NULL-safe comparison side by side
-- Prompt: Using deep 1_values, return one row per row_id with columns row_id, value, not_two, not_in_block, null_safe_different. Compare value<>2, value NOT IN the blocklist and value IS DISTINCT FROM 2. Order by row_id and preserve all three source rows.
-- Expected: Row 1 has true, NULL, true; row 2 has false, false, false; row 3 has NULL, NULL, true. value is 1,2, NULL respectively. A WHERE filter is not part of this diagnostic.

-- 2. Express a known-value anti-join policy
-- Prompt: Return row_id, value for nonmissing candidate values that have no equal nonmissing blocklist value. Use NOT EXISTS and explicitly exclude missing candidate values. The result grain is one source row per row_id, ordered by row_id.
-- Expected: Only(row_id1, value 1) remains. Value 2 is blocked; row 3 is excluded because its candidate value is unknown, not because it matched a known blocklist value.

-- 3. Distinguish empty, mixed and unknown quantified collections
-- Prompt: For five named integer-array cases, return case_id, any_larger, all_larger using 5<ANY and 5<ALL. Cases are empty,[6,7],[4,7],[4, NULL], and a NULL array. One row represents one case, ordered by case_id.
-- Expected: Case 1 gives false, true; case 2 true, true; case 3 true, false; case 4 NULL, false; case 5 NULL, NULL. A false element decides ALL even when another comparison is unknown.

-- 4. Compare missing values under an explicit reconciliation rule
-- Prompt: Return row_id, value for candidates having a blocklist value that is not distinct from the candidate, using EXISTS and IS NOT DISTINCT FROM. Keep one row per row_id and order by row_id. Explain that this is value reconciliation, not an identity join.
-- Expected: Rows 2 and 3 remain, with values 2 andNULL. The NULL candidate matches the NULL blocklist value under this explicit value-comparison rule.

-- 5. Find people satisfying every required skill
-- Prompt: Return person_id, person_name for people possessing every skill in deep 1_required. Use double NOT EXISTS so duplicate skill rows and extra skills do not alter completeness. One row represents one person, ordered by person_id.
-- Expected: People 1 Ada and 4 Dee pass. Ada has a duplicate sql record, Dee has extra rust, and neither changes the all-requirements result. Ben, Cy, Eli fail.

-- 6. Make empty-requirement policy visible
-- Prompt: Inside the temporary fixture, empty deep 1_required and return one row per person with person_id, all_requirements, nonempty_policy. The first flag uses pure universal logic; the second also requires that at least one requirement exists. Order by person_id and roll back this mutation after the case.
-- Expected: All five people have all_requirements=true and nonempty_policy=false. The original two required skills must be restored by the exercise savepoint rollback.

ROLLBACK;
