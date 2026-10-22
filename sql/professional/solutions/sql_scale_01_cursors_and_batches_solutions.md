# SQL-SCALE-01: solution reasoning

Use this after an honest attempt at the [guide](../companion-guides/sql_scale_01_cursors_and_batches.md)
and [learner script](../lessons/sql_scale_01_cursors_and_batches.sql). The separate
[executable solution](sql_scale_01_cursors_and_batches_solutions.sql) runs all six answers and independent
fail-fast checks with `psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_scale_01_cursors_and_batches_solutions.sql`.
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

## Exercise 1: Record an exact first-page boundary

```sql
SELECT event_id,occurred_at FROM scale_events ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2;
```

The query establishes a complete order before limiting the page. Known timestamps descend, NULL values are postponed, and event_id breaks all remaining ties. Capture the last returned pair, not the largest ID in the table or an independently calculated timestamp. The assertion checks the first-page identity sequence. Although the tiny table may choose a sequential scan, that says nothing about the semantic correctness of its page boundary. A representative performance exercise belongs in a separate controlled dataset. Keep cursor format and timestamp zone explicit when an application serializes it, and reject malformed or incompatible cursors before composing a query.

**Inputs/evidence:** For sql-scale-01 Exercise 1, Return the first two event rows with event_id, occurred_at. Record both cursor fields and explain why timestamp alone is insufficient.

**Expected result/shape:** For sql-scale-01 Exercise 1, Two rows keyed by event_id, columns event_id, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: IDs 6,3. Cursor is (11:00 UTC on January 1 2024,3).

**Verify:** For sql-scale-01 Exercise 1, Inspect page IDs 6,3 and save both values from the last returned row, timestamp 11:00 UTC and ID 3. A separately computed maximum ID is not this cursor.

## Exercise 2: Traverse a timestamp tie without overlap

```sql
SELECT event_id,occurred_at FROM scale_events WHERE (occurred_at,event_id) < (TIMESTAMPTZ '2024-01-01 11:00+00',3) ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2;
```

Lexicographic less-than matches the two descending keys for these non-NULL rows. At the cursor timestamp, smaller IDs qualify; at earlier timestamps, any ID qualifies. Strict comparison excludes the cursor itself. The returned pair at 10:00 demonstrates that ties must be resolved in both ORDER BY and the continuation condition. The assertion checks the full ordered identity list and also checks that none belongs to page one. This exercise intentionally handles known timestamps only. Presenting it as a complete all-row export would be wrong because a NULL timestamp does not participate in ordinary tuple inequality the way ORDER BY places it.

**Inputs/evidence:** For sql-scale-01 Exercise 2, Continue after (2024-01-01 11:00+00,3) for two known-timestamp rows, projecting event_id, occurred_at. Use a strict compound boundary.

**Expected result/shape:** For sql-scale-01 Exercise 2, Two rows keyed by event_id, columns event_id, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: IDs 2,1. Neither appears on page one; both timestamp ties survive.

**Verify:** For sql-scale-01 Exercise 2, Compare ordered IDs 2,1, require no overlap with first-page IDs 6,3, and retain both equal 10:00 timestamps. A timestamp-only or non-strict boundary fails these controls.

## Exercise 3: Cross into the unknown-timestamp phase

```sql
SELECT event_id,occurred_at FROM scale_events
WHERE occurred_at < TIMESTAMPTZ '2024-01-01 09:00+00'
   OR (occurred_at = TIMESTAMPTZ '2024-01-01 09:00+00' AND event_id < 5)
   OR occurred_at IS NULL
ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2;
```

The expanded predicate names the two known-value continuation cases and the separate unknown phase. This matches the presentation policy rather than relying on an arbitrary sentinel timestamp. Once the saved cursor itself is NULL, remaining known timestamps are already behind the traversal and must not be revisited; compare event_id only among NULL timestamp rows. The assertion verifies that ID 4 is returned with its missing timestamp intact and that the next phase is empty on the fixture. A real cursor should encode enough state to choose the appropriate predicate safely. Adding NULLS LAST to ORDER BY alone never repairs a WHERE predicate that excludes every NULL.

**Inputs/evidence:** For sql-scale-01 Exercise 3, Continue after the last known boundary (2024-01-01 09:00+00,5) and include the NULL tail. Return event_id, occurred_at. Explain the follow-on predicate after a NULL cursor at ID 4.

**Expected result/shape:** For sql-scale-01 Exercise 3, One event row keyed by event_id, columns event_id, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: ID 4 with NULL. After that NULL cursor, occurred_at IS NULL AND event_id < 4 returns zero rows.

**Verify:** For sql-scale-01 Exercise 3, Require ID 4 with occurred_at NULL, then inspect the follow-on NULL-only identity predicate and confirm it returns zero rows for this fixture.

## Exercise 4: Expose positional drift after an insertion

```sql
WITH changed AS (
 SELECT event_id,occurred_at FROM scale_events
 UNION ALL SELECT 7,TIMESTAMPTZ '2024-01-01 13:00+00'
), positional AS (
 SELECT event_id,occurred_at FROM changed ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2 OFFSET 2
), continuation AS (
 SELECT event_id,occurred_at FROM changed WHERE (occurred_at,event_id)<(TIMESTAMPTZ '2024-01-01 11:00+00',3)
 ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2
)
SELECT 'offset' AS path,event_id,occurred_at FROM positional
UNION ALL SELECT 'cursor',event_id,occurred_at FROM continuation
ORDER BY path,occurred_at DESC NULLS LAST,event_id DESC;
```

The CTE builds a changed input where a new leading event shifts every old position. OFFSET 2 now starts at original page-one row 3, so that row repeats. The saved cursor still filters below the old boundary and returns IDs 2 and 1. This is evidence for a specific mutation case, not proof against all mutations: changing a previously returned row's sort timestamp could still move it across the cursor. The assertion checks each labeled page independently. No permanent insert is needed to demonstrate the counterexample, so the default script stays single-session and rollback-safe. Explain the mutation policy along with the query whenever promising traversal behavior.

**Inputs/evidence:** For sql-scale-01 Exercise 4, Model inserting event 7 at 13:00 after page one. Compare an OFFSET 2 page with the original compound cursor page. Return path, event_id, occurred_at for both two-row pages.

**Expected result/shape:** For sql-scale-01 Exercise 4, Four path-event rows identified by (path,event_id), columns path, event_id, occurred_at; final ORDER BY path, occurred_at DESC NULLS LAST, event_id DESC. cursor gives 2,1; offset gives 3,2, repeating page-one ID 3.

**Verify:** For sql-scale-01 Exercise 4, Compare offset page IDs 3,2 with cursor page IDs 2,1. Only the offset result repeats first-page ID 3, and a separate source count still equals six.

## Exercise 5: Exclude a late arrival with a declared sealed prefix

```sql
WITH incoming AS (
 SELECT event_id,received_seq,occurred_at FROM scale_events
 UNION ALL SELECT 7,7,TIMESTAMPTZ '2024-01-01 10:30+00'
)
SELECT event_id,received_seq,occurred_at FROM incoming
WHERE received_seq <= 6 AND ((occurred_at,event_id)<(TIMESTAMPTZ '2024-01-01 11:00+00',3) OR occurred_at IS NULL)
ORDER BY occurred_at DESC NULLS LAST,event_id DESC;
```

The fence defines input membership, while the cursor defines position inside that membership. The late event's timestamp fits below the cursor, but its received_seq lies beyond the sealed prefix, so it is excluded. Parentheses prevent the NULL alternative from bypassing the fence. The assertion checks all remaining IDs in presentation order. This fixture's prefix is explicitly complete and immutable. It is not a general guarantee of PostgreSQL sequence values: values can be allocated in a transaction that commits after a later allocation, and sequence gaps are normal. A real export must establish a valid snapshot or application seal before interpreting a numeric cutoff as complete input.

**Inputs/evidence:** For sql-scale-01 Exercise 5, Add an illustrative event 7 received_seq 7 with event timestamp 10:30. Continue after (11:00,3) under the sealed received_seq <= 6 fence, including NULLs. Return event_id, received_seq, occurred_at.

**Expected result/shape:** For sql-scale-01 Exercise 5, Four event rows keyed by event_id, columns event_id, received_seq, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: IDs 2,1,5,4. Late event 7 is excluded despite fitting the time cursor.

**Verify:** For sql-scale-01 Exercise 5, Inspect returned event_id values 2,1,5,4 under the sealed prefix and confirm incoming ID 7 is excluded despite fitting the timestamp cursor. Explain why allocated sequence order is not committed-prefix completeness.

## Exercise 6: Prove bounded traversal covers the static fixture

```sql
WITH ordered AS (
 SELECT event_id,row_number() OVER (ORDER BY occurred_at DESC NULLS LAST,event_id DESC) AS position FROM scale_events
)
SELECT ((position-1)/2+1)::integer AS batch_no,array_agg(event_id ORDER BY position) AS event_ids,count(*) AS row_count
FROM ordered GROUP BY (position-1)/2+1 ORDER BY batch_no;
```

ROW_NUMBER assigns a unique position under the same total order, and integer division groups consecutive pairs into manifest batches. This makes a simple independent oracle for a fixed fixture: compare actual cursor pages against the listed batches. Computing positions for the whole input on every request would give up the bounded continuation behavior being taught, so the oracle is a verification tool rather than the implementation. The assertion checks the complete expected manifest and total row coverage. For real workloads separately measure representative EXPLAIN plans and latency without forcing an index choice. EXPLAIN ANALYZE executes its statement; do not adapt the example to writes without acknowledging that effect.

**Inputs/evidence:** For sql-scale-01 Exercise 6, Build a deterministic batch manifest over all six rows with a batch size of two using row_number only as a validation oracle. Return batch_no, event_ids, row_count. Explain why this oracle is not the production cursor algorithm.

**Expected result/shape:** For sql-scale-01 Exercise 6, Three manifest rows keyed by batch_no, columns batch_no, event_ids, row_count; final ORDER BY batch_no: (1,{6,3},2),(2,{2,1},2),(3,{5,4},2). Concatenated identities cover all six exactly once.

**Verify:** For sql-scale-01 Exercise 6, Inspect batch arrays {6,3},{2,1},{5,4}, each size two. Their concatenation must contain all six source event_id values exactly once, including the unknown timestamp row.

## Cleanup and evidence boundary

The final rollback removes every temporary table, helper function, index, and modeled change. Running this file twice starts from the same fixture and should produce the same logical evidence. No extension, external dataset, current timestamp, or administrator capability is required. For the optional two-session concurrency lab, use its separate explicit cleanup because that fixture is deliberately committed; the default script never prepares that shared state. A static content check can validate contracts and file structure, while only a live PostgreSQL transcript validates SQL execution. Retain that distinction when reporting completion.
