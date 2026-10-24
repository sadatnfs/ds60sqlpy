# NULL-Aware Quantification, Anti-Joins, and Relational Division

**Stable ID:** `sql-deep-01`. **Estimated time:** 150 minutes, split across reading and query investigation.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **PostgreSQL** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Use the private reader's **Create/open guided SQL notebook** action. It creates the ignored editable copy at `.learning/sql/sql-deep-01/lesson/workspace/sql/professional/lessons/sql_deep_01.sql`. Read the supplied fixture, write a prediction, edit that copy and run the complete script. The prepared target must be the local disposable `advanced_sql_training` database. These lessons never require a production connection or a new cloud service.

The learner file starts a transaction, checks the database name, creates only temporary tables, runs two worked examples and ends with ROLLBACK. Your six query attempts belong before that final rollback. Re-run the complete file after an error so the fixture and transaction state are known. Output appears in the notebook or terminal as named columns and bounded rows; a command tag alone does not verify a SELECT result.

Windows PowerShell fallback, from the repository root:

```powershell
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql/professional/lessons/sql_deep_01.sql"
```

macOS/Linux fallback, from the repository root:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_deep_01.sql
```

If the prepared database is unavailable, return to classroom setup rather than changing the target. Keep credentials outside lesson files and command text. Read the [learner SQL](../lessons/sql_deep_01.sql); keep [explanatory solutions](../solutions/sql_deep_01_solutions.md) and [executable solutions](../solutions/sql_deep_01_solutions.sql) closed until an attempt or an explicit worked comparison. PostgreSQL 16+ syntax is used; the canonical runtime is PostgreSQL 17.

## Level and prerequisites

- **Level:** Advanced. The guide defines each new mechanism before relying on it.
- **Prerequisites:** [`sql-09`](../../postgres-60day/companion-guides/day09_correlated_subqueries.md), [`sql-quality-01`](sql_quality_01_bags_and_fanout.md).
- **Artifacts:** [Learner SQL](../lessons/sql_deep_01.sql), [explained reference](../solutions/sql_deep_01_solutions.md), and [executable reference](../solutions/sql_deep_01_solutions.sql). Every fixture is local, deterministic and rolled back; no prior lesson state is required.

## Learning objectives

- State the output grain and identity before writing a query, including the NULL and duplicate policies.
- Explain the new SQL mechanism, produce each exact projected result and expose the listed counterexample.
- Verify rollback-safe behavior from inspected result rows and assertions without relying on a final success message.

## Vocabulary and concepts

- **Three-valued logic:** SQL predicates can be true, false or unknown; WHERE retains only true rows.

- **Existential quantification:** A claim that at least one matching row exists, expressed naturally with EXISTS.

- **Universal quantification:** A claim that every relevant row satisfies a condition, often expressed by ruling out a counterexample.

- **Vacuous truth:** A universal condition over an empty requirement set is true because no counterexample exists.

SQL comparisons involving NULL usually produce unknown rather than false. This means NOT does not turn an unknown comparison into true, and WHERE removes both false and unknown rows. A query can therefore return no rows for two very different reasons: every candidate is forbidden, or some comparisons are unknowable under the chosen predicate.

NOT IN is particularly important. If the right-hand list contains a NULL and no equality match is found, the result can remain unknown. A NULL in a blocklist can consequently prevent ordinary nonmatching candidates from passing a WHERE condition. NOT EXISTS asks whether a qualifying row exists and can express a clearer policy, but its inner comparison still needs a deliberate NULL rule. Unknown candidate identifiers should not automatically be treated as known permitted values.

IS DISTINCT FROM and IS NOT DISTINCT FROM provide total Boolean comparisons that treat two NULL values as not distinct. They are useful for reconciliation when missing-to-known or known-to-missing transitions matter. They do not prove that two records with missing identifiers represent the same entity. NULL-safe value comparison and entity identity are separate decisions.

ANY and ALL quantify a predicate over a set or array. ANY is true when at least one comparison is true; ALL is false when at least one comparison is false. Empty arrays give ANY false and ALL true. A NULL array differs from an empty array: it represents unknown collection information, so the quantified result is unknown. NULL elements can also preserve unknown results when no decisive true or false comparison exists.

Relational division asks which entities satisfy every requirement. A robust formulation selects a person for whom there does not exist a required skill that the person does not possess. This double NOT EXISTS structure models the logic directly, ignores duplicate possession rows and remains correct when extra skills exist. Counting joined rows without handling duplicates can award false completeness.

The empty requirement set exposes a policy choice. Pure universal logic selects everyone, while an operational approval process might require at least one declared requirement before approving anyone. Express that nonempty condition separately rather than pretending the SQL engine made a mistake. Every exercise states exact output columns and identity so these logical differences are visible in results.

## Worked example / walkthrough

### Example 1

```sql
SELECT 'ordinary_inequality' AS comparison, (NULL::integer <> 2) AS result
UNION ALL
SELECT 'null_safe_distinction', (NULL::integer IS DISTINCT FROM 2)
ORDER BY comparison;
```

The output grain is one row per named comparison, with columns comparison and result ordered by comparison. ordinary_inequality is NULL while null_safe_distinction is true. The explicit cast gives NULL an integer type. The comparison names are the output identity; the Boolean measure is not a key.

### Example 2

```sql
SELECT 'empty_array' AS case_name,
       5 < ANY(ARRAY[]::integer[]) AS any_larger,
       5 < ALL(ARRAY[]::integer[]) AS all_larger;
```

The one-row output has case_name, any_larger and all_larger. ANY is false because no comparison succeeds; ALL is true because no comparison fails. The typed empty array is a known collection with zero elements, not an unknown array value. This distinction is the basis of the final requirement-set case.

## Exercises

1. **Inspect unknown and NULL-safe comparison side by side.** Using deep 1_values, return one row per row_id with columns row_id, value, not_two, not_in_block, null_safe_different. Compare value<>2, value NOT IN the blocklist and value IS DISTINCT FROM 2. Order by row_id and preserve all three source rows.

**Inputs/evidence:** For sql-deep-01 Exercise 1, Using deep 1_values, return one row per row_id with columns row_id, value, not_two, not_in_block, null_safe_different. Compare value<>2, value NOT IN the blocklist and value IS DISTINCT FROM 2. Order by row_id and preserve all three source rows.

**Expected result/shape:** For sql-deep-01 Exercise 1, Row 1 has true, NULL, true; row 2 has false, false, false; row 3 has NULL, NULL, true. value is 1,2, NULL respectively. A WHERE filter is not part of this diagnostic.

**Verify:** For sql-deep-01 Exercise 1, project predicates before filtering and compare all three row IDs. In particular, test NULL with IS NULL instead of equality and confirm the blocklist NULL makes the nonmatch unknown.

2. **Express a known-value anti-join policy.** Return row_id, value for nonmissing candidate values that have no equal nonmissing blocklist value. Use NOT EXISTS and explicitly exclude missing candidate values. The result grain is one source row per row_id, ordered by row_id.

**Inputs/evidence:** For sql-deep-01 Exercise 2, Return row_id, value for nonmissing candidate values that have no equal nonmissing blocklist value. Use NOT EXISTS and explicitly exclude missing candidate values. The result grain is one source row per row_id, ordered by row_id.

**Expected result/shape:** For sql-deep-01 Exercise 2, Only(row_id1, value 1) remains. Value 2 is blocked; row 3 is excluded because its candidate value is unknown, not because it matched a known blocklist value.

**Verify:** For sql-deep-01 Exercise 2, check the returned ID against the known-value set difference {1,2} minus {2}; separately confirm row 3 is excluded by the outer nonmissing policy.

3. **Distinguish empty, mixed and unknown quantified collections.** For five named integer-array cases, return case_id, any_larger, all_larger using 5<ANY and 5<ALL. Cases are empty,[6,7],[4,7],[4, NULL], and a NULL array. One row represents one case, ordered by case_id.

**Inputs/evidence:** For sql-deep-01 Exercise 3, For five named integer-array cases, return case_id, any_larger, all_larger using 5<ANY and 5<ALL. Cases are empty,[6,7],[4,7],[4, NULL], and a NULL array. One row represents one case, ordered by case_id.

**Expected result/shape:** For sql-deep-01 Exercise 3, Case 1 gives false, true; case 2 true, true; case 3 true, false; case 4 NULL, false; case 5 NULL, NULL. A false element decides ALL even when another comparison is unknown.

**Verify:** For sql-deep-01 Exercise 3, evaluate each array element by hand and apply the decisive true rule for ANY and decisive false rule for ALL; inspect both Boolean result columns for the empty and unknown-array cases.

4. **Compare missing values under an explicit reconciliation rule.** Return row_id, value for candidates having a blocklist value that is not distinct from the candidate, using EXISTS and IS NOT DISTINCT FROM. Keep one row per row_id and order by row_id. Explain that this is value reconciliation, not an identity join.

**Inputs/evidence:** For sql-deep-01 Exercise 4, Return row_id, value for candidates having a blocklist value that is not distinct from the candidate, using EXISTS and IS NOT DISTINCT FROM. Keep one row per row_id and order by row_id. Explain that this is value reconciliation, not an identity join.

**Expected result/shape:** For sql-deep-01 Exercise 4, Rows 2 and 3 remain, with values 2 and NULL. The NULL candidate matches the NULL blocklist value under this explicit value-comparison rule.

**Verify:** For sql-deep-01 Exercise 4, count all input reconciliation rows and inspect the missing-to-known and missing-to-missing cases independently, using IS DISTINCT FROM as a total Boolean comparison.

5. **Find people satisfying every required skill.** Return person_id, person_name for people possessing every skill in deep 1_required. Use double NOT EXISTS so duplicate skill rows and extra skills do not alter completeness. One row represents one person, ordered by person_id.

**Inputs/evidence:** For sql-deep-01 Exercise 5, Return person_id, person_name for people possessing every skill in deep 1_required. Use double NOT EXISTS so duplicate skill rows and extra skills do not alter completeness. One row represents one person, ordered by person_id.

**Expected result/shape:** For sql-deep-01 Exercise 5, People 1 Ada and 4 Dee pass. Ada has a duplicate sql record, Dee has extra rust, and neither changes the all-requirements result. Ben, Cy, Eli fail.

**Verify:** For sql-deep-01 Exercise 5, list the required skill set for each returned person row, ignoring duplicate possessions; verify that an extra skill cannot compensate for a missing required skill.

6. **Make empty-requirement policy visible.** Inside the temporary fixture, empty deep 1_required and return one row per person with person_id, all_requirements, nonempty_policy. The first flag uses pure universal logic; the second also requires that at least one requirement exists. Order by person_id and roll back this mutation after the case.

**Inputs/evidence:** For sql-deep-01 Exercise 6, Inside the temporary fixture, empty deep 1_required and return one row per person with person_id, all_requirements, nonempty_policy. The first flag uses pure universal logic; the second also requires that at least one requirement exists. Order by person_id and roll back this mutation after the case.

**Expected result/shape:** For sql-deep-01 Exercise 6, All five people have all_requirements=true and nonempty_policy=false. The original two required skills must be restored by the exercise savepoint rollback.

**Verify:** For sql-deep-01 Exercise 6, run the empty-requirement case inside a savepoint; compare the universal-logic population with the explicit nonempty-policy population and restore the fixture afterward.

## Common mistakes and diagnosis

If NOT IN unexpectedly removes every candidate, project its Boolean result and inspect NULLs on both sides. If an anti-join admits unknown IDs, state whether that is the intended policy and add a known-identity condition if required. If a completeness count changes after duplicate ingestion, replace raw row counting with distinct requirements or a counterexample formulation. If an empty requirement set approves everyone, decide whether vacuous truth or a nonempty approval precondition matches the business rule. Do not replace unknown predicates with false merely to make a result look cleaner.

## Self-check

- Explain the row grain after each FROM, JOIN, filter, grouping or window step. Name the identity columns that prove rows were neither lost nor multiplied.
- Reconstruct a boundary result by hand, then compare with the query output. Explain why the tempting wrong query fails even if it returns the same total on an easier fixture.

## Next step

Transfer the same reasoning to a new small fixture before using it on larger data, then continue with [the next deepening lesson](sql_deep_02.md). Keep the result columns, ordering, NULL policy and observation horizon explicit. The [professional SQL track](../README.md) provides the wider route.

## Primary sources and official APIs

- [PostgreSQL17 subquery quantification](https://www.postgresql.org/docs/17/functions-subquery.html).

- [PostgreSQL17 array comparisons](https://www.postgresql.org/docs/17/functions-comparisons.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through sql-deep-01: NULL-Aware Quantification, Anti-Joins, and Relational Division.
Read sql/professional/companion-guides/sql_deep_01.md and sql/professional/lessons/sql_deep_01.sql. Direct prerequisites: sql-09, sql-quality-01.
Explain the row grain and SQL clauses, then ask me to predict a concrete result before my attempt. Give one hint at a time and review my exact result rows, identity, NULL behavior and boundary evidence. Ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt.
Use only the prepared local disposable advanced_sql_training database and the complete rollback-safe script. Preserve my ignored working copy and do not start services or redirect to another database.
Done when all six projected-result contracts and their counterexamples have inspected evidence and I can explain why the wrong query fails.
```
