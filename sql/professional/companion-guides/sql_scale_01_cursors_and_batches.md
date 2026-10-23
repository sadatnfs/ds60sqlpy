# SQL-SCALE-01: Cursor Pagination and Bounded Batches

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **PostgreSQL** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Use only the local disposable `advanced_sql_training` database on PostgreSQL
16 or newer. The lesson page is a readable preview. In the private course
portal, choose **Create/open guided SQL notebook**, run readiness, acknowledge
only the explicitly offered course reset if needed, and edit the notebook's
ignored `.learning/sql/sql-scale-01/` SQL copy. Its exact path is
`.learning/sql/sql-scale-01/lesson/workspace/sql/professional/lessons/sql_scale_01_cursors_and_batches.sql`. Save the copy and run its complete-script
cell. Output appears below that cell as a full `psql` transcript. A successful
run ends in `ROLLBACK`, exits 0, and has the example identities stated below.
The setup uses temporary tables and no external data or extension.

If using VS Code directly, run from the repository root. These fallbacks work
in terminals after PostgreSQL setup:

```powershell
# Windows PowerShell
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql/professional/lessons/sql_scale_01_cursors_and_batches.sql"
```

```bash
# macOS/Linux
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_scale_01_cursors_and_batches.sql
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

- **Level:** advanced
- **Direct catalog prerequisites:** [`sql-35`](../../postgres-60day/companion-guides/day35_avoiding_pitfalls.md), [`sql-38`](../../postgres-60day/companion-guides/day38_transactions_isolation.md), [`sql-test-01`](sql_test_01_contracts_migrations.md)
- **Artifacts:** [learner SQL](../lessons/sql_scale_01_cursors_and_batches.sql), [solution reasoning](../solutions/sql_scale_01_cursors_and_batches_solutions.md), [executable solution](../solutions/sql_scale_01_cursors_and_batches_solutions.sql).

Direct prerequisites name the required boundary. The fixture setup is supplied; do not mistake its table-definition syntax for extra unstated prerequisite work.

## Learning objectives

- Build a compound continuation predicate that matches a complete result order.
- Handle nullable sort columns explicitly and test page boundaries.
- Separate traversal correctness, snapshot policy, and measured plan behavior.

## Vocabulary and concepts

A page is a bounded portion of an ordered result. OFFSET names a position;
a cursor names the last returned sort value and identity. Positions shift
when earlier rows are inserted or deleted. A cursor can continue from its
boundary without counting how many rows currently precede it. That solves
one traversal problem, but it does not freeze the dataset or make mutable
ordering columns safe. This lesson treats those as separate contracts.



- **Cursor:** A cursor is a saved continuation boundary containing every field needed
to reproduce the final order. 

- **Keyset pagination:** Keyset pagination filters strictly beyond
that boundary before taking another bounded page. 

- **Total order:** A total order resolves
all ties so two distinct result rows never compare equally under the declared
ordering columns. 

- **Snapshot:** A snapshot is the database visibility view used for a
statement or transaction. 

- **Watermark:** A watermark is an application-defined boundary
declaring which input belongs to a run. 

- **Sealed prefix:** A sealed prefix is an ingestion
segment that its owner promises is complete and immutable.

The six events have unique event_id, explicit event timestamps in UTC, and
an illustrative received_seq belonging to a sealed prefix. Two events share
a timestamp and one has no event timestamp. The main order is occurred_at
descending, unknown timestamps last, event_id descending. Event_id resolves
ties but is not a claim about event time. Record the cursor from the final
returned row, not from a maximum computed independently of the page. Do not
turn the cursor into executable SQL; application code binds its typed values.

## Syntax anatomy and query reasoning

For two non-NULL descending keys, `(occurred_at, event_id) < (cursor_time,
cursor_id)` expresses lexicographic continuation: earlier timestamp, or equal
timestamp and smaller identity. The WHERE inequality must agree with the
final ORDER BY direction. A timestamp-only boundary would skip the second
event at a tie. Using <= would repeat the cursor row. Reversing one sort
direction requires an expanded Boolean predicate rather than blindly using
the same row-comparison shortcut.

Row comparison with a NULL field does not supply the explicit missing-value
order of ORDER BY. Handle the NULL tail as a deliberate phase. From a known
timestamp cursor, include known values below the cursor plus every NULL
timestamp. From a NULL cursor, remain in the NULL phase and compare only
event_id. Store the phase and the identity as part of the cursor contract.
This keeps traversal aligned with DESC NULLS LAST without inventing a fake
timestamp that could collide with real data.

An immutable sealed-prefix fence can exclude later arrivals in this fixture.
A bare PostgreSQL sequence maximum is not generally such a fence: sequence
allocation order is not commit order, and a transaction with an earlier value
can commit later. A fixed cutoff also does not prevent deletion or sort-key
updates within its range. For a stable export, consider a bounded REPEATABLE
READ transaction or an explicitly materialized immutable input. Long snapshots
have operational costs, so the owner must define duration, failure recovery,
and retention. A cursor alone promises continuation under stated mutations,
never an automatically exact snapshot of changing business data.

## Worked example / walkthrough

Run these in the complete learner file so the temporary fixture and transaction are present. The fixture values are fixed; the examples never depend on the current clock. Predict each result before running it.

### Example 1: Save the whole boundary from the first page

```sql
SELECT event_id, occurred_at
FROM scale_events
ORDER BY occurred_at DESC NULLS LAST, event_id DESC
LIMIT 2;
```

The first page returns IDs 6 and 3. The continuation boundary is the second row, timestamp 11:00 UTC and event_id 3. Both values are required by the complete order. LIMIT bounds the result, and the index is a possible access path rather than a guarantee that this six-row example will use it. The event timestamp can differ from arrival order.

**Expected:** Two event rows, columns event_id, occurred_at: IDs 6 then 3; cursor (2024-01-01 11:00+00,3).

### Example 2: Continue across a tied timestamp

```sql
SELECT event_id, occurred_at
FROM scale_events
WHERE (occurred_at,event_id) < (TIMESTAMPTZ '2024-01-01 11:00+00',3)
ORDER BY occurred_at DESC NULLS LAST,event_id DESC
LIMIT 2;
```

The known-value comparison admits IDs 2,1,5, then the row cap returns 2 and 1. Their equal timestamps remain distinct because identity is the second comparison key. This short example deliberately does not finish the NULL phase; the later exercise adds that policy. The final returned boundary becomes (10:00,1), so continuing from timestamp alone would lose or repeat a tied event.

**Expected:** Two event rows, columns event_id, occurred_at: IDs 2 then 1, both 10:00 UTC.

## Exercises

Attempt these in order in the ignored working copy, before its final rollback. Write the output grain and a prediction before execution. Compare the actual identities and values with each contract. A query merely running is not sufficient evidence. Hints are optional and leave the answer construction to you.

1. **Record an exact first-page boundary.**

   **Inputs/evidence:** For sql-scale-01 Exercise 1, Return the first two event rows with event_id, occurred_at. Record both cursor fields and explain why timestamp alone is insufficient.

   **Expected result/shape:** For sql-scale-01 Exercise 1, Two rows keyed by event_id, columns event_id, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: IDs 6,3. Cursor is (11:00 UTC on January 1 2024,3).

   **Verify:** For sql-scale-01 Exercise 1, Inspect page IDs 6,3 and save both values from the last returned row, timestamp 11:00 UTC and ID 3. A separately computed maximum ID is not this cursor.

   **Progressive hint:** The cursor comes from the last row actually returned.

2. **Traverse a timestamp tie without overlap.**

   **Inputs/evidence:** For sql-scale-01 Exercise 2, Continue after (2024-01-01 11:00+00,3) for two known-timestamp rows, projecting event_id, occurred_at. Use a strict compound boundary.

   **Expected result/shape:** For sql-scale-01 Exercise 2, Two rows keyed by event_id, columns event_id, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: IDs 2,1. Neither appears on page one; both timestamp ties survive.

   **Verify:** For sql-scale-01 Exercise 2, Compare ordered IDs 2,1, require no overlap with first-page IDs 6,3, and retain both equal 10:00 timestamps. A timestamp-only or non-strict boundary fails these controls.

   **Progressive hint:** Compare the row pair in the same direction as the final sort.

3. **Cross into the unknown-timestamp phase.**

   **Inputs/evidence:** For sql-scale-01 Exercise 3, Continue after the last known boundary (2024-01-01 09:00+00,5) and include the NULL tail. Return event_id, occurred_at. Explain the follow-on predicate after a NULL cursor at ID 4.

   **Expected result/shape:** For sql-scale-01 Exercise 3, One event row keyed by event_id, columns event_id, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: ID 4 with NULL. After that NULL cursor, occurred_at IS NULL AND event_id < 4 returns zero rows.

   **Verify:** For sql-scale-01 Exercise 3, Require ID 4 with occurred_at NULL, then inspect the follow-on NULL-only identity predicate and confirm it returns zero rows for this fixture.

   **Progressive hint:** A known boundary admits its earlier known rows plus the NULL phase.

4. **Expose positional drift after an insertion.**

   **Inputs/evidence:** For sql-scale-01 Exercise 4, Model inserting event 7 at 13:00 after page one. Compare an OFFSET 2 page with the original compound cursor page. Return path, event_id, occurred_at for both two-row pages.

   **Expected result/shape:** For sql-scale-01 Exercise 4, Four path-event rows identified by (path,event_id), columns path, event_id, occurred_at; final ORDER BY path, occurred_at DESC NULLS LAST, event_id DESC. cursor gives 2,1; offset gives 3,2, repeating page-one ID 3.

   **Verify:** For sql-scale-01 Exercise 4, Compare offset page IDs 3,2 with cursor page IDs 2,1. Only the offset result repeats first-page ID 3, and a separate source count still equals six.

   **Progressive hint:** Use a CTE that UNION ALL adds event 7 without changing the fixture.

5. **Exclude a late arrival with a declared sealed prefix.**

   **Inputs/evidence:** For sql-scale-01 Exercise 5, Add an illustrative event 7 received_seq 7 with event timestamp 10:30. Continue after (11:00,3) under the sealed received_seq <= 6 fence, including NULLs. Return event_id, received_seq, occurred_at.

   **Expected result/shape:** For sql-scale-01 Exercise 5, Four event rows keyed by event_id, columns event_id, received_seq, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: IDs 2,1,5,4. Late event 7 is excluded despite fitting the time cursor.

   **Verify:** For sql-scale-01 Exercise 5, Inspect returned event_id values 2,1,5,4 under the sealed prefix and confirm incoming ID 7 is excluded despite fitting the timestamp cursor. Explain why allocated sequence order is not committed-prefix completeness.

   **Progressive hint:** Apply membership and continuation as separate AND conditions; group the OR continuation cases.

6. **Prove bounded traversal covers the static fixture.**

   **Inputs/evidence:** For sql-scale-01 Exercise 6, Build a deterministic batch manifest over all six rows with a batch size of two using row_number only as a validation oracle. Return batch_no, event_ids, row_count. Explain why this oracle is not the production cursor algorithm.

   **Expected result/shape:** For sql-scale-01 Exercise 6, Three manifest rows keyed by batch_no, columns batch_no, event_ids, row_count; final ORDER BY batch_no: (1,{6,3},2),(2,{2,1},2),(3,{5,4},2). Concatenated identities cover all six exactly once.

   **Verify:** For sql-scale-01 Exercise 6, Inspect batch arrays {6,3},{2,1},{5,4}, each size two. Their concatenation must contain all six source event_id values exactly once, including the unknown timestamp row.

   **Progressive hint:** Number the fixed ordered input and group each consecutive pair.

## Self-check

- Which mutation did the cursor example handle, and which mutation could still break it?
- Why does a unique final ID belong in both the ordering and cursor?
- What evidence makes a watermark a complete input boundary rather than a hopeful numeric cutoff?

Keep your actual query and transcript. Explain one incorrect alternative and the exact fixture row that exposes it. A passing worked example does not prove an unattempted exercise. Revisit a failed prediction after taking a break, then answer the retrieval questions without looking at the code.

## Common pitfalls

- If a timestamp tie is skipped or repeated, inspect both the inequality and the final identity direction; adding only ORDER BY does not fix the boundary.

- If NULL events disappear, write the known and NULL cursor phases explicitly; row comparison does not inherit NULLS LAST.

- If late rows leak into a run, distinguish a genuine sealed input prefix from a maximum sequence value and from a stable database snapshot.

## Next step

Continue to `sql-concurrency-01` to reason about competing writers and visibility evidence.

Concrete next target: [Isolation traces and optimistic concurrency](sql_concurrency_01_isolation_and_versions.md).

## Reference

The course works offline after setup. These optional official references describe the PostgreSQL semantics used here:

- [PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/queries-limit.html)
- [PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/functions-comparisons.html)
- [PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/transaction-iso.html)

## Ask Codex about this lesson

The lesson and expected observations are sufficient offline. For optional coaching, copy:

```text
Tutor me through sql-scale-01: Cursor Pagination and Bounded Batches using the checked-in $guide-ds60sqlpy-learning skill.
Guide: sql/professional/companion-guides/sql_scale_01_cursors_and_batches.md
Answer-free learner: sql/professional/lessons/sql_scale_01_cursors_and_batches.sql
Direct prerequisite boundary: sql-35, sql-38, sql-test-01.
Teach at the advanced level, defining each new term before relying on it.
Focus on Build a compound continuation predicate that matches a complete result order. Handle nullable sort columns explicitly and test page boundaries.
Use the guide -> explain -> predict -> my attempt -> one hint at a time -> evidence review -> retrieval loop.
Keep solutions/ closed until I ask after an honest attempt. Do not read, quote,
or summarize the official solution before that boundary.
Prefer Create/open guided SQL notebook and its ignored .learning/sql/sql-scale-01/ working copy.
Run live SQL only against the local disposable advanced_sql_training database.
Never request a password or point a reset at shared or valuable data.
Ask for my actual SQL and complete psql transcript, compare identities and values
with each Expected contract, and explain the first discrepancy before editing.
Done when my attempted exercises have inspectable matching evidence and I can
answer the guide's retrieval questions and a small transfer question in my own words.
```
