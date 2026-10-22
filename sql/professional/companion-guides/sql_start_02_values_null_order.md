# SQL-START-02: Values NULL and Deterministic Order

## How to run this lesson

Use only the local disposable `advanced_sql_training` database on PostgreSQL
16 or newer. The lesson page is a readable preview. In the private course
portal, choose **Create/open guided SQL notebook**, run readiness, acknowledge
only the explicitly offered course reset if needed, and edit the notebook's
ignored `.learning/sql/sql-start-02/` SQL copy. Its exact path is
`.learning/sql/sql-start-02/lesson/workspace/sql/professional/lessons/sql_start_02_values_null_order.sql`. Save the copy and run its complete-script
cell. Output appears below that cell as a full `psql` transcript. A successful
run ends in `ROLLBACK`, exits 0, and has the example identities stated below.
The setup uses temporary tables and no external data or extension.

If using VS Code directly, run from the repository root. These fallbacks work
in terminals after PostgreSQL setup:

```powershell
# Windows PowerShell
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql/professional/lessons/sql_start_02_values_null_order.sql"
```

```bash
# macOS/Linux
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_start_02_values_null_order.sql
```

Keep `-X` to ignore personal client startup changes and `ON_ERROR_STOP` to
stop at the first unexpected error. If `psql` is missing, return to the
operating-system setup and `scripts/course.py doctor`. An authentication
failure needs the local setup workflow, never a password pasted into a lesson.
If the database-name guard rejects the run, inspect your target instead of
removing the guard. After an unexpected transaction error, fix that first
error and rerun the whole file in a fresh connection. To try an exercise, put
its SQL before the final `ROLLBACK` in your private copy; temporary tables
exist only in that connection and transaction. Running this official learner
file demonstrates the examples; exercises remain answer-free until you add an
attempt. Do not edit the separate official solutions while studying.

## Level and prerequisites

- **Level:** foundation
- **Direct catalog prerequisites:** [`sql-start-01`](sql_start_01_tables_and_grain.md)
- **Artifacts:** [learner SQL](../lessons/sql_start_02_values_null_order.sql), [solution reasoning](../solutions/sql_start_02_values_null_order_solutions.md), [executable solution](../solutions/sql_start_02_values_null_order_solutions.sql).

Direct prerequisites name the required boundary. The fixture setup is supplied; do not mistake its table-definition syntax for extra unstated prerequisite work.

## Learning objectives

- Separate an unknown value from zero and empty text.
- Predict true, false, and unknown predicates before filtering.
- Construct a stable order with explicit missing-value placement and a unique tie-breaker.

## Vocabulary and concepts

A missing measurement is a statement about knowledge. Zero is a known number;
an empty string is a known text value containing no characters. SQL uses NULL
to represent a missing or unknown value. Filling it with zero changes the
claim being made, so missing-value handling belongs to the question rather
than to cosmetic cleanup. The fixture has five shipments, including two
with unknown measured weight and one with a known zero weight.



- **Null:** NULL is the SQL marker for an unknown or absent field value. It is not a
number or a quoted word. 

- **Predicate:** A predicate is an expression used to decide
whether a row qualifies. 

- **Boolean:** A Boolean value is true or false, but a SQL
Boolean expression can also evaluate to NULL, which represents unknown.


- **Three-valued logic:** Three-valued logic describes calculations involving true, false, and
unknown. 

- **Tie-breaker:** A tie-breaker is an additional ordering column that distinguishes
rows whose first sort value is equal. 

- **Coalesce:** COALESCE chooses the first non-NULL
expression from left to right; it does not discover the original missing value.

Imagine asking whether an unopened box weighs more than zero. Without its
weight you cannot answer yes or no. `weight > 0` is unknown for that box,
and `NOT (weight > 0)` remains unknown. WHERE keeps only true, so neither
predicate selects the unknown box. `IS NULL` directly asks whether the value
is missing and always yields true or false. This distinction explains many
queries that silently omit rows without raising an error.

## Syntax anatomy and query reasoning

`SELECT shipment_id, weight, weight > 0 AS is_positive FROM start_shipments`
shows the predicate result as a column. It is a useful debugging step before
moving the predicate into WHERE. `= NULL` asks an equality question with an
unknown operand; `IS NULL` tests the missing marker. `IS NOT NULL` finds
present values. `IS DISTINCT FROM` is a comparison that treats missingness as
a comparable state: two NULLs are not distinct, and NULL differs from zero.
Use it when the question genuinely means "different, including missing".

`ORDER BY weight DESC NULLS LAST, shipment_id` has three decisions. The first
expression ranks larger known weights first. NULLS LAST places unknown
weights after all known ones. The final unique ID orders ties, including the
two unknown weights. Without it, the order between equal weights is not
promised. A filter and a sort have different jobs: sorting NULLs last does
not remove them. LIMIT 2 then takes the first two rows from that declared
order; it does not choose a meaningful top two without the order.

`COALESCE(label, '(missing)')` preserves empty text because empty text is
present. `NULLIF(label, '')` converts exactly an empty string to NULL; it
does not trim whitespace automatically. Combining them is an explicit
display policy. Keep the original label beside the display version when
inspecting a repair. Arithmetic with NULL usually remains NULL, so a derived
weight must retain an unknown state unless a justified policy replaces it.

## Worked example / walkthrough

Run these in the complete learner file so the temporary fixture and transaction are present. The fixture values are fixed; the examples never depend on the current clock. Predict each result before running it.

### Example 1: Inspect truth before filtering

```sql
SELECT shipment_id, weight, weight > 0 AS is_positive,
       weight IS NULL AS is_missing
FROM start_shipments
ORDER BY shipment_id;
```

Every output row still represents one shipment. The comparison is false for ID 1, unknown for IDs 2 and 5, and true for IDs 3 and 4. IS NULL instead produces true for IDs 2 and 5 and false elsewhere. Looking at the predicate as a column exposes information that WHERE would discard. No string comparison or implicit conversion is required.

**Expected:** Five shipment rows; columns shipment_id, weight, is_positive, is_missing. True positive IDs are 3 and 4; missing IDs are 2 and 5.

### Example 2: Rank known values while preserving unknowns

```sql
SELECT shipment_id, weight, label
FROM start_shipments
ORDER BY weight DESC NULLS LAST, shipment_id;
```

The result contains all five shipments. Weights 5,5,0 precede unknowns, and identity orders the tied 5s and the unknown pair. PostgreSQL has a default NULL placement, but writing the policy avoids relying on remembering it. A known zero stays ahead of unknown measurements. This presentation does not impute or update any weight.

**Expected:** IDs 3,4,1,2,5, with columns shipment_id, weight, label. The NULL weights remain NULL.

## Exercises

Attempt these in order in the ignored working copy, before its final rollback. Write the output grain and a prediction before execution. Compare the actual identities and values with each contract. A query merely running is not sufficient evidence. Hints are optional and leave the answer construction to you.

1. **Inspect missingness.**

   **Inputs/evidence:** For sql-start-02 Exercise 1, Return shipment_id, weight, and weight IS NULL named is_missing for every shipment. Predict the Boolean column before executing.

   **Expected result/shape:** For sql-start-02 Exercise 1, Five shipment rows with columns shipment_id, weight, is_missing; final ORDER BY shipment_id. is_missing is true only for IDs 2 and 5.

   **Verify:** For sql-start-02 Exercise 1, Inspect true only at shipment_id 2 and 5; ID 1 has zero weight and a false is_missing flag. The missingness test itself never produces unknown.

   **Progressive hint:** Show the missingness test in SELECT before trying a WHERE condition.

2. **Compare a complement with missingness.**

   **Inputs/evidence:** For sql-start-02 Exercise 2, Return shipment_id, weight for NOT (weight > 0). Explain why the result is not the complement of the positive-weight result over all five shipments.

   **Expected result/shape:** For sql-start-02 Exercise 2, One row keyed by shipment_id with columns shipment_id, weight, final ORDER BY shipment_id: (1,0). Unknown IDs 2 and 5 are absent from both positive and negated filters.

   **Verify:** For sql-start-02 Exercise 2, Inspect the projected predicate values for all five input rows: ID 1 is false, IDs 3 and 4 true, IDs 2 and 5 unknown. Only ID 1 qualifies after ordinary negation.

   **Progressive hint:** NOT unknown is still unknown.

3. **Keep unknown and zero as separate categories.**

   **Inputs/evidence:** For sql-start-02 Exercise 3, Return shipment_id, weight for weights that are known zero or missing. Use explicit predicates rather than replacing unknown weights with zero.

   **Expected result/shape:** For sql-start-02 Exercise 3, Three shipment rows with columns shipment_id, weight, final ORDER BY shipment_id: IDs 1,2,5. ID 1 is zero; IDs 2 and 5 remain NULL.

   **Verify:** For sql-start-02 Exercise 3, Require identities 1,2,5 and exactly two NULL weights. Inspect the original measurements to prove selection did not replace unknown values with zero.

   **Progressive hint:** Combine the zero comparison and missingness test with OR.

4. **Specify every ordering decision.**

   **Inputs/evidence:** For sql-start-02 Exercise 4, Return the top two known weights with shipment_id, weight. Use descending weight, NULLS LAST, and ascending shipment_id before LIMIT 2.

   **Expected result/shape:** For sql-start-02 Exercise 4, Two rows keyed by shipment_id, columns shipment_id, weight, final ORDER BY weight DESC NULLS LAST, shipment_id: IDs 3 and 4, each weight 5.

   **Verify:** For sql-start-02 Exercise 4, Inspect ordered IDs 3 then 4 and both weights 5; repeat on unchanged input and justify the unique identity tie-breaker rather than relying on one observed storage order.

   **Progressive hint:** Tied measurements require an identity even with a small LIMIT.

5. **Debug an empty text display policy.**

   **Inputs/evidence:** For sql-start-02 Exercise 5, Return shipment_id, label, and a display_label that uses (unlabeled) for both NULL and empty text. Explain why COALESCE(label, '(unlabeled)') alone misses IDs 1 and 4.

   **Expected result/shape:** For sql-start-02 Exercise 5, Five shipment rows with columns shipment_id, label, display_label; final ORDER BY shipment_id. Display labels in ID order are (unlabeled),(unlabeled),ready,(unlabeled),hold; original empty labels remain empty.

   **Verify:** For sql-start-02 Exercise 5, Compare all five display_label values and inspect original labels beside them: IDs 1 and 4 remain empty strings, while ID 2 remains NULL.

   **Progressive hint:** Convert exactly empty text to NULL before selecting a fallback.

6. **Transfer to a NULL-safe change detector.**

   **Inputs/evidence:** For sql-start-02 Exercise 6, Compare old and new weights (10,NULL,NULL), (11,0,NULL), (12,5,5), (13,NULL,0), named shipment_id, old_weight, new_weight. Return shipment_id, old_weight, new_weight only for changed values, including missingness transitions.

   **Expected result/shape:** For sql-start-02 Exercise 6, Two changed shipment rows, columns shipment_id, old_weight, new_weight, final ORDER BY shipment_id: IDs 11 and 13. Two unknowns at ID 10 do not count as a change.

   **Verify:** For sql-start-02 Exercise 6, Require changed IDs 11 and 13. Check that both negative controls are absent: ID 10 has two unknown values, and ID 12 has the same known value twice.

   **Progressive hint:** IS DISTINCT FROM gives a definite result when either operand is NULL.

## Self-check

- Why do weight > 0 and NOT (weight > 0) fail to cover all shipments?
- Does sorting unknown values last make them known or remove them?
- When should a display fallback remain separate from a stored field?

Keep your actual query and transcript. Explain one incorrect alternative and the exact fixture row that exposes it. A passing worked example does not prove an unattempted exercise. Revisit a failed prediction after taking a break, then answer the retrieval questions without looking at the code.

## Common pitfalls

- If = NULL returns no matches, project that expression alongside IS NULL to see the unknown result directly.

- If NULL shipments appear first in a descending report, write NULLS LAST and a unique identity; rerunning alone cannot prove a stable tie policy.

- If an empty label survives a fallback, inspect its length and distinguish empty text from NULL before choosing NULLIF or trimming.

## Next step

Continue to `sql-start-03` to build and debug a query in small stages.

Concrete next target: [Query construction and debugging](sql_start_03_query_debugging.md).

## Reference

The course works offline after setup. These optional official references describe the PostgreSQL semantics used here:

- [PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/functions-comparisons.html)
- [PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/queries-limit.html)

## Ask Codex about this lesson

The lesson and expected observations are sufficient offline. For optional coaching, copy:

```text
Tutor me through sql-start-02: Values NULL and Deterministic Order using the checked-in $guide-ds60sqlpy-learning skill.
Guide: sql/professional/companion-guides/sql_start_02_values_null_order.md
Answer-free learner: sql/professional/lessons/sql_start_02_values_null_order.sql
Direct prerequisite boundary: sql-start-01.
Teach at the foundation level, defining each new term before relying on it.
Focus on Separate an unknown value from zero and empty text. Predict true, false, and unknown predicates before filtering.
Use the guide -> explain -> predict -> my attempt -> one hint at a time -> evidence review -> retrieval loop.
Keep solutions/ closed until I ask after an honest attempt. Do not read, quote,
or summarize the official solution before that boundary.
Prefer Create/open guided SQL notebook and its ignored .learning/sql/sql-start-02/ working copy.
Run live SQL only against the local disposable advanced_sql_training database.
Never request a password or point a reset at shared or valuable data.
Ask for my actual SQL and complete psql transcript, compare identities and values
with each Expected contract, and explain the first discrepancy before editing.
Done when my attempted exercises have inspectable matching evidence and I can
answer the guide's retrieval questions and a small transfer question in my own words.
```
