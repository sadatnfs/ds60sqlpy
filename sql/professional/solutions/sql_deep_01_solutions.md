# sql-deep-01: Explained reference solutions

Read [NULL-Aware Quantification, Anti-Joins, and Relational Division](../companion-guides/sql_deep_01.md) and attempt its six queries before comparing. The [complete reference script](sql_deep_01_solutions.sql) recreates the same temporary fixture, runs every answer inside its own savepoint, compares exact JSON row sets with fail-fast assertions, then rolls back. No permanent table, role or service is changed.

## Exercises and reasoning

## Exercise 1: Inspect unknown and NULL-safe comparison side by side

Using deep 1_values, return one row per row_id with columns row_id, value, not_two, not_in_block, null_safe_different. Compare value<>2, value NOT IN the blocklist and value IS DISTINCT FROM 2. Order by row_id and preserve all three source rows.

**Inputs/evidence:** For sql-deep-01 Exercise 1, Using deep 1_values, return one row per row_id with columns row_id, value, not_two, not_in_block, null_safe_different. Compare value<>2, value NOT IN the blocklist and value IS DISTINCT FROM 2. Order by row_id and preserve all three source rows.

**Expected result/shape:** For sql-deep-01 Exercise 1, Row 1 has true, NULL, true; row 2 has false, false, false; row 3 has NULL, NULL, true. value is 1,2, NULL respectively. A WHERE filter is not part of this diagnostic.

**Verify:** For sql-deep-01 Exercise 1, project predicates before filtering and compare all three row IDs. In particular, test NULL with IS NULL instead of equality and confirm the blocklist NULL makes the nonmatch unknown.

```sql
SELECT row_id,value,value<>2 AS not_two,
       value NOT IN(SELECT value FROM deep1_blocklist) AS not_in_block,
       value IS DISTINCT FROM 2 AS null_safe_different
FROM deep1_values ORDER BY row_id;
```

Projecting the predicates instead of immediately filtering preserves evidence about why a later WHERE would remove a row. The blocklist contains NULL, so candidate one has no equality match but still cannot establish every required inequality. Candidate two has a decisive match and NOT IN is false. The null-safe comparison is a total Boolean statement about value distinction, while ordinary inequality preserves unknown information.

## Exercise 2: Express a known-value anti-join policy

Return row_id, value for nonmissing candidate values that have no equal nonmissing blocklist value. Use NOT EXISTS and explicitly exclude missing candidate values. The result grain is one source row per row_id, ordered by row_id.

**Inputs/evidence:** For sql-deep-01 Exercise 2, Return row_id, value for nonmissing candidate values that have no equal nonmissing blocklist value. Use NOT EXISTS and explicitly exclude missing candidate values. The result grain is one source row per row_id, ordered by row_id.

**Expected result/shape:** For sql-deep-01 Exercise 2, Only(row_id1, value 1) remains. Value 2 is blocked; row 3 is excluded because its candidate value is unknown, not because it matched a known blocklist value.

**Verify:** For sql-deep-01 Exercise 2, check the returned ID against the known-value set difference {1,2} minus {2}; separately confirm row 3 is excluded by the outer nonmissing policy.

```sql
SELECT v.row_id,v.value FROM deep1_values AS v
WHERE v.value IS NOT NULL
  AND NOT EXISTS(SELECT 1 FROM deep1_blocklist AS b WHERE b.value=v.value)
ORDER BY v.row_id;
```

The outer nonmissing condition defines the operational policy for unknown candidates. The inner equality can only create a qualifying row for an actual known equal value, so the blocklist NULL does not poison every nonmatch. EXISTS ignores what the subquery projects; SELECT 1 is conventional because only row existence matters. Omitting the outer condition would also retain the NULL candidate, which would be a different approval policy.

## Exercise 3: Distinguish empty, mixed and unknown quantified collections

For five named integer-array cases, return case_id, any_larger, all_larger using 5<ANY and 5<ALL. Cases are empty,[6,7],[4,7],[4, NULL], and a NULL array. One row represents one case, ordered by case_id.

**Inputs/evidence:** For sql-deep-01 Exercise 3, For five named integer-array cases, return case_id, any_larger, all_larger using 5<ANY and 5<ALL. Cases are empty,[6,7],[4,7],[4, NULL], and a NULL array. One row represents one case, ordered by case_id.

**Expected result/shape:** For sql-deep-01 Exercise 3, Case 1 gives false, true; case 2 true, true; case 3 true, false; case 4 NULL, false; case 5 NULL, NULL. A false element decides ALL even when another comparison is unknown.

**Verify:** For sql-deep-01 Exercise 3, evaluate each array element by hand and apply the decisive true rule for ANY and decisive false rule for ALL; inspect both Boolean result columns for the empty and unknown-array cases.

```sql
WITH cases(case_id,items) AS (VALUES
 (1,ARRAY[]::integer[]),(2,ARRAY[6,7]),(3,ARRAY[4,7]),
 (4,ARRAY[4,NULL]::integer[]),(5,NULL::integer[]))
SELECT case_id,5<ANY(items) AS any_larger,5<ALL(items) AS all_larger
FROM cases ORDER BY case_id;
```

ANY combines comparisons like an OR, while ALL combines them like an AND, including SQL unknown values. A true comparison makes ANY true even if another is unknown; a false comparison makes ALL false. The empty collection supplies the logical identities false for OR and true for AND. A NULL collection has no known elements to quantify and therefore does not share those empty-set identities.

## Exercise 4: Compare missing values under an explicit reconciliation rule

Return row_id, value for candidates having a blocklist value that is not distinct from the candidate, using EXISTS and IS NOT DISTINCT FROM. Keep one row per row_id and order by row_id. Explain that this is value reconciliation, not an identity join.

**Inputs/evidence:** For sql-deep-01 Exercise 4, Return row_id, value for candidates having a blocklist value that is not distinct from the candidate, using EXISTS and IS NOT DISTINCT FROM. Keep one row per row_id and order by row_id. Explain that this is value reconciliation, not an identity join.

**Expected result/shape:** For sql-deep-01 Exercise 4, Rows 2 and 3 remain, with values 2 andNULL. The NULL candidate matches the NULL blocklist value under this explicit value-comparison rule.

**Verify:** For sql-deep-01 Exercise 4, count all input reconciliation rows and inspect the missing-to-known and missing-to-missing cases independently, using IS DISTINCT FROM as a total Boolean comparison.

```sql
SELECT v.row_id,v.value FROM deep1_values AS v
WHERE EXISTS(SELECT 1 FROM deep1_blocklist AS b
             WHERE b.value IS NOT DISTINCT FROM v.value)
ORDER BY v.row_id;
```

The NULL-safe predicate treats two missing value states as not distinct, which is useful for comparing corresponding attributes. EXISTS prevents duplicate blocklist rows from multiplying the candidate output. The rule must not be generalized to unknown entity keys: equal missingness is not evidence that two unknown people are the same person. The query states exactly which equality notion is intended for this bounded reconciliation.

## Exercise 5: Find people satisfying every required skill

Return person_id, person_name for people possessing every skill in deep 1_required. Use double NOT EXISTS so duplicate skill rows and extra skills do not alter completeness. One row represents one person, ordered by person_id.

**Inputs/evidence:** For sql-deep-01 Exercise 5, Return person_id, person_name for people possessing every skill in deep 1_required. Use double NOT EXISTS so duplicate skill rows and extra skills do not alter completeness. One row represents one person, ordered by person_id.

**Expected result/shape:** For sql-deep-01 Exercise 5, People 1 Ada and 4 Dee pass. Ada has a duplicate sql record, Dee has extra rust, and neither changes the all-requirements result. Ben, Cy, Eli fail.

**Verify:** For sql-deep-01 Exercise 5, list the required skill set for each returned person row, ignoring duplicate possessions; verify that an extra skill cannot compensate for a missing required skill.

```sql
SELECT p.person_id,p.person_name FROM deep1_people AS p
WHERE NOT EXISTS(
 SELECT 1 FROM deep1_required AS r
 WHERE NOT EXISTS(SELECT 1 FROM deep1_skills AS s
                  WHERE s.person_id=p.person_id AND s.skill=r.skill))
ORDER BY p.person_id;
```

The inner subquery asks whether the current person has one particular required skill. The middle WHERE identifies a missing requirement, and the outer NOT EXISTS rules out all such counterexamples. Duplicate possessions do not matter because existence is Boolean, and extra skills never become requirements. A raw joined-row count could incorrectly treat Ada's duplicate SQL row as evidence of another distinct required skill.

## Exercise 6: Make empty-requirement policy visible

Inside the temporary fixture, empty deep 1_required and return one row per person with person_id, all_requirements, nonempty_policy. The first flag uses pure universal logic; the second also requires that at least one requirement exists. Order by person_id and roll back this mutation after the case.

**Inputs/evidence:** For sql-deep-01 Exercise 6, Inside the temporary fixture, empty deep 1_required and return one row per person with person_id, all_requirements, nonempty_policy. The first flag uses pure universal logic; the second also requires that at least one requirement exists. Order by person_id and roll back this mutation after the case.

**Expected result/shape:** For sql-deep-01 Exercise 6, All five people have all_requirements=true and nonempty_policy=false. The original two required skills must be restored by the exercise savepoint rollback.

**Verify:** For sql-deep-01 Exercise 6, run the empty-requirement case inside a savepoint; compare the universal-logic population with the explicit nonempty-policy population and restore the fixture afterward.

```sql
TRUNCATE deep1_required;
SELECT p.person_id,
 NOT EXISTS(SELECT 1 FROM deep1_required AS r
            WHERE NOT EXISTS(SELECT 1 FROM deep1_skills AS s
                             WHERE s.person_id=p.person_id AND s.skill=r.skill)) AS all_requirements,
 EXISTS(SELECT 1 FROM deep1_required)
 AND NOT EXISTS(SELECT 1 FROM deep1_required AS r
                WHERE NOT EXISTS(SELECT 1 FROM deep1_skills AS s
                                 WHERE s.person_id=p.person_id AND s.skill=r.skill)) AS nonempty_policy
FROM deep1_people AS p ORDER BY p.person_id;
```

No missing requirement can exist when the requirement table is empty, so the universal statement is true for every person. The second flag adds a separate business precondition and is false for everyone. This makes the policy choice auditable instead of disguising it inside an accidental count formula. The reference wraps the temporary truncation in a savepoint and restores it before the final transaction rollback, keeping this boundary case isolated.

## Verification and transaction boundary

Every answer is materialized into a temporary answer table and compared with a literal expected row set, including column names, NULL values and deterministic order. The assertion function rejects both false and unknown Boolean results, so a NULL comparison cannot silently pass. Each exercise rolls back to its own savepoint, ensuring mutations used for one boundary case do not alter the next. The final ROLLBACK removes the full fixture. Read the first error if a contract fails; a later row count or command tag cannot repair an earlier failed assertion.
