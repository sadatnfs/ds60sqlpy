# SQL-START-02: solution reasoning

Use this after an honest attempt at the [guide](../companion-guides/sql_start_02_values_null_order.md)
and [learner script](../lessons/sql_start_02_values_null_order.sql). The separate
[executable solution](sql_start_02_values_null_order_solutions.sql) runs all six answers and independent
fail-fast checks with `psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_start_02_values_null_order_solutions.sql`.
It uses only temporary fixtures, starts a transaction, and ends in rollback.
It must exit 0 with no contract failures. Each answer has a savepoint so an
experiment cannot silently change a later exercise's starting conditions.
The assertion helper treats false and unknown as failures, rather than allowing
a NULL assertion to pass accidentally. Keep the original fixture unchanged
when comparing your work so the stated identities remain a reliable oracle.

The code below is the answer for each numbered prompt, followed by its
reasoning. Inspect the first discrepancy in your own transcript before reading
a different answer. A solution is one defensible implementation of this contract;
an alternative is valid if its identities, values, missingness, ordering, and
transaction behavior match. Tests constrain the actual returned relation,
rather than assuming a familiar-looking query must be right.

## Exercise solutions

## Exercise 1: Inspect missingness

```sql
SELECT shipment_id, weight, weight IS NULL AS is_missing FROM start_shipments ORDER BY shipment_id;
```

IS NULL asks about the marker itself, so it produces a definite Boolean for every shipment. Equality against NULL would return unknown instead of answering that question. Keeping shipment_id visible ties each Boolean to a real source fact. The known zero for ID 1 is present and therefore not missing. The assertion compares the identities of rows marked missing with the fixed fixture expectation. This is a stronger check than merely counting two missing values, because the wrong pair of rows could otherwise pass. Nothing in the query changes the source values; it is an inspection tool for building the later filter.

**Inputs/evidence:** For sql-start-02 Exercise 1, Return shipment_id, weight, and weight IS NULL named is_missing for every shipment. Predict the Boolean column before executing.

**Expected result/shape:** For sql-start-02 Exercise 1, Five shipment rows with columns shipment_id, weight, is_missing; final ORDER BY shipment_id. is_missing is true only for IDs 2 and 5.

**Verify:** For sql-start-02 Exercise 1, Inspect true only at shipment_id 2 and 5; ID 1 has zero weight and a false is_missing flag. The missingness test itself never produces unknown.

## Exercise 2: Compare a complement with missingness

```sql
SELECT shipment_id, weight FROM start_shipments WHERE NOT (weight > 0) ORDER BY shipment_id;
```

WHERE retains only true. For ID 1 the inner comparison is false, so NOT turns it true. For IDs 3 and 4 the inner comparison is true and NOT turns it false. For IDs 2 and 5 the unknown input stays unknown, which WHERE excludes. This explains why a positive filter and its negation need not partition all rows when missing values are possible. The check requires precisely ID 1. If the business asks for every shipment that is not known to be positive, it needs an explicitly different predicate that includes missing values, rather than assuming ordinary negation already does that.

**Inputs/evidence:** For sql-start-02 Exercise 2, Return shipment_id, weight for NOT (weight > 0). Explain why the result is not the complement of the positive-weight result over all five shipments.

**Expected result/shape:** For sql-start-02 Exercise 2, One row keyed by shipment_id with columns shipment_id, weight, final ORDER BY shipment_id: (1,0). Unknown IDs 2 and 5 are absent from both positive and negated filters.

**Verify:** For sql-start-02 Exercise 2, Inspect the projected predicate values for all five input rows: ID 1 is false, IDs 3 and 4 true, IDs 2 and 5 unknown. Only ID 1 qualifies after ordinary negation.

## Exercise 3: Keep unknown and zero as separate categories

```sql
SELECT shipment_id, weight FROM start_shipments WHERE weight = 0 OR weight IS NULL ORDER BY shipment_id;
```

The OR joins two separate eligibility rules while the projection preserves the original measurement. ID 1 satisfies the equality comparison, and IDs 2 and 5 satisfy IS NULL. No imputation is needed just to select them. Replacing the displayed weight with zero would erase the difference the exercise is teaching. The assertion checks both the identities and the fact that two returned measurements remain unknown. This pattern is useful when routing zero and missing values to review while still allowing a reviewer to distinguish their causes. If the policy later treats the two categories differently, the original information remains available.

**Inputs/evidence:** For sql-start-02 Exercise 3, Return shipment_id, weight for weights that are known zero or missing. Use explicit predicates rather than replacing unknown weights with zero.

**Expected result/shape:** For sql-start-02 Exercise 3, Three shipment rows with columns shipment_id, weight, final ORDER BY shipment_id: IDs 1,2,5. ID 1 is zero; IDs 2 and 5 remain NULL.

**Verify:** For sql-start-02 Exercise 3, Require identities 1,2,5 and exactly two NULL weights. Inspect the original measurements to prove selection did not replace unknown values with zero.

## Exercise 4: Specify every ordering decision

```sql
SELECT shipment_id, weight FROM start_shipments ORDER BY weight DESC NULLS LAST, shipment_id LIMIT 2;
```

The sort places known large values first, then orders equal measurements by shipment_id. LIMIT restricts the already ordered result to two rows. NULLS LAST prevents unknown measurements from taking the leading positions under the chosen policy, but it is not a filter. Here two known maximum weights exist, so IDs 3 and 4 are returned. If the limit exceeded the number of known values, the query would eventually include unknowns; add IS NOT NULL when that is forbidden by the question. The assertion checks the ordered identity sequence, which captures both tie-breaking and selection rather than just checking that each weight is 5.

**Inputs/evidence:** For sql-start-02 Exercise 4, Return the top two known weights with shipment_id, weight. Use descending weight, NULLS LAST, and ascending shipment_id before LIMIT 2.

**Expected result/shape:** For sql-start-02 Exercise 4, Two rows keyed by shipment_id, columns shipment_id, weight, final ORDER BY weight DESC NULLS LAST, shipment_id: IDs 3 and 4, each weight 5.

**Verify:** For sql-start-02 Exercise 4, Inspect ordered IDs 3 then 4 and both weights 5; repeat on unchanged input and justify the unique identity tie-breaker rather than relying on one observed storage order.

## Exercise 5: Debug an empty text display policy

```sql
SELECT shipment_id, label, COALESCE(NULLIF(label, ''), '(unlabeled)') AS display_label FROM start_shipments ORDER BY shipment_id;
```

NULLIF compares label with the empty string and produces NULL only when they are equal. COALESCE then uses the fallback for either a converted empty string or an originally missing label. A present label such as ready or hold passes through. The original label is also selected so the display policy remains distinguishable from stored data. COALESCE alone does not treat empty text as missing. The assertion compares all five final labels rather than checking only one successful replacement. Whitespace-only labels would still pass through this specific policy; trimming them would be a separate normalization decision that should be stated and tested.

**Inputs/evidence:** For sql-start-02 Exercise 5, Return shipment_id, label, and a display_label that uses (unlabeled) for both NULL and empty text. Explain why COALESCE(label, '(unlabeled)') alone misses IDs 1 and 4.

**Expected result/shape:** For sql-start-02 Exercise 5, Five shipment rows with columns shipment_id, label, display_label; final ORDER BY shipment_id. Display labels in ID order are (unlabeled),(unlabeled),ready,(unlabeled),hold; original empty labels remain empty.

**Verify:** For sql-start-02 Exercise 5, Compare all five display_label values and inspect original labels beside them: IDs 1 and 4 remain empty strings, while ID 2 remains NULL.

## Exercise 6: Transfer to a NULL-safe change detector

```sql
SELECT shipment_id, old_weight, new_weight
FROM (VALUES (10, NULL::numeric, NULL::numeric), (11, 0, NULL),
             (12, 5, 5), (13, NULL, 0)) AS changes(shipment_id, old_weight, new_weight)
WHERE old_weight IS DISTINCT FROM new_weight
ORDER BY shipment_id;
```

The VALUES input names both versions explicitly and casts the initially unknown measurements to numeric. IS DISTINCT FROM tests whether the two states differ, treating a pair of NULLs as equal for this comparison. It catches known-to-unknown and unknown-to-known transitions that ordinary inequality would leave unknown. It does not invent a replacement weight. The output grain remains one changed shipment identified by shipment_id. The assertion checks IDs 11 and 13, so the unchanged known value and unchanged missing pair are both negative controls. This technique becomes useful for reconciliation and update detection later, but its meaning is already inspectable with these four rows.

**Inputs/evidence:** For sql-start-02 Exercise 6, Compare old and new weights (10,NULL,NULL), (11,0,NULL), (12,5,5), (13,NULL,0), named shipment_id, old_weight, new_weight. Return shipment_id, old_weight, new_weight only for changed values, including missingness transitions.

**Expected result/shape:** For sql-start-02 Exercise 6, Two changed shipment rows, columns shipment_id, old_weight, new_weight, final ORDER BY shipment_id: IDs 11 and 13. Two unknowns at ID 10 do not count as a change.

**Verify:** For sql-start-02 Exercise 6, Require changed IDs 11 and 13. Check that both negative controls are absent: ID 10 has two unknown values, and ID 12 has the same known value twice.

## Cleanup and evidence boundary

The final rollback removes every temporary table, helper function, index, and modeled change. Running this file twice starts from the same fixture and should produce the same logical evidence. No extension, external dataset, current timestamp, or administrator capability is required. For the optional two-session concurrency lab, use its separate explicit cleanup because that fixture is deliberately committed; the default script never prepares that shared state. A static content check can validate contracts and file structure, while only a live PostgreSQL transcript validates SQL execution. Retain that distinction when reporting completion.
