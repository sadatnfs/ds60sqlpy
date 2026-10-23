# ROWS, RANGE, GROUPS, Exclusions, and Sessionization

**Stable ID:** `sql-deep-03`. **Estimated time:** 150 minutes, split across reading and query investigation.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **PostgreSQL** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Use the private reader's **Create/open guided SQL notebook** action. It creates the ignored editable copy at `.learning/sql/sql-deep-03/lesson/workspace/sql/professional/lessons/sql_deep_03.sql`. Read the supplied fixture, write a prediction, edit that copy and run the complete script. The prepared target must be the local disposable `advanced_sql_training` database. These lessons never require a production connection or a new cloud service.

The learner file starts a transaction, checks the database name, creates only temporary tables, runs two worked examples and ends with ROLLBACK. Your six query attempts belong before that final rollback. Re-run the complete file after an error so the fixture and transaction state are known. Output appears in the notebook or terminal as named columns and bounded rows; a command tag alone does not verify a SELECT result.

Windows PowerShell fallback, from the repository root:

```powershell
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql/professional/lessons/sql_deep_03.sql"
```

macOS/Linux fallback, from the repository root:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_deep_03.sql
```

If the prepared database is unavailable, return to classroom setup rather than changing the target. Keep credentials outside lesson files and command text. Read the [learner SQL](../lessons/sql_deep_03.sql); keep [explanatory solutions](../solutions/sql_deep_03_solutions.md) and [executable solutions](../solutions/sql_deep_03_solutions.sql) closed until an attempt or an explicit worked comparison. PostgreSQL 16+ syntax is used; the canonical runtime is PostgreSQL 17.

## Level and prerequisites

- **Level:** Advanced. The guide defines each new mechanism before relying on it.
- **Prerequisites:** [`sql-22`](../../postgres-60day/companion-guides/day22_advanced_windows.md), [`sql-analytics-01`](sql_analytics_01_query_patterns.md).
- **Artifacts:** [Learner SQL](../lessons/sql_deep_03.sql), [explained reference](../solutions/sql_deep_03_solutions.md), and [executable reference](../solutions/sql_deep_03_solutions.sql). Every fixture is local, deterministic and rolled back; no prior lesson state is required.

## Learning objectives

- State the output grain and identity before writing a query, including the NULL and duplicate policies.
- Explain the new SQL mechanism, produce each exact projected result and expose the listed counterexample.
- Verify rollback-safe behavior from inspected result rows and assertions without relying on a final success message.

## Vocabulary and concepts

- **Window partition:** The rows eligible to contribute to a window function before ordering and frame restrictions are applied.

- **Peer group:** Rows equal on all expressions in the window ORDER BY; adding a unique ID changes which rows are peers.

- **Frame:** The subset of a partition used for the current row, defined by ROWS, RANGE or GROUPS boundaries and optional exclusions.

- **Session boundary:** A derived start flag based on a stated inactivity rule, which must be accumulated in a separate window stage.

A window function can preserve the input row count while calculating over a different set of rows for each event. PARTITION BY defines independent entities, ORDER BY defines sequence or peers, and the frame defines the contributing neighborhood. These clauses have separate responsibilities. A final ORDER BY controls presentation and does not retroactively change a window's calculation.

ROWS counts physical ordered rows. When its result depends on position, add a deterministic tie break to the window ordering. RANGE works with ordering values and peer groups; an offset RANGE frame over timestamps uses an elapsed-time interval and requires an appropriate single ordering expression. GROUPS counts peer groups rather than individual rows or elapsed duration. A two-row frame, two-peer-group frame and thirty-minute frame answer different questions.

The default ordered aggregate frame commonly extends through the current peer group. Equal timestamps can therefore receive the same running total even when they appear on separate rows. Adding event_id to that ORDER BY removes the timestamp peers and changes the result. Do not add a tie breaker blindly when the intended metric is peer-aware; choose ROWS for row semantics or preserve the peer key for group semantics.

EXCLUDE CURRENT ROW removes only the current event. EXCLUDE GROUP removes every peer of the current ordering value, including the current row. EXCLUDE TIES removes other peers while retaining the current row. These distinctions matter for prior-time features: removing only one row can leave another event at the same timestamp in the history. SUM over an empty frame is NULL, so converting it to zero requires an explicit complete-log interpretation.

LAST_VALUE is especially sensitive to frame boundaries. Under a frame ending at the current row or peer group, it reports that frame's last value, not necessarily the partition's final event. To obtain the final value for the full customer sequence, explicitly extend the frame to UNBOUNDED FOLLOWING and use a deterministic order.

Sessionization combines multiple window stages. First calculate the prior timestamp with LAG, then mark the first event or a gap exceeding the threshold, then cumulatively sum those flags. A window result cannot be nested directly inside another window expression in the same SELECT level. Named CTE stages expose the changing columns while preserving event grain until the final session aggregation.

## Worked example / walkthrough

### Example 1

```sql
WITH samples(event_id,tick,amount) AS (VALUES(1,1,4),(2,1,6),(3,2,3))
SELECT event_id,
 sum(amount) OVER(ORDER BY tick,event_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS row_total,
 sum(amount) OVER(ORDER BY tick RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS peer_total
FROM samples ORDER BY event_id;
```

The output remains one row per event_id with row_total and peer_total. Row totals are 4,10,13 while peer totals are 10,10,13. The first frame advances one deterministic event at a time; the second includes the entire current tick peer group. The final ordering prints identities consistently without changing either frame.

### Example 2

```sql
WITH samples(event_id,amount) AS (VALUES(1,3),(2,9))
SELECT event_id,last_value(amount) OVER(ORDER BY event_id) AS default_last,
 last_value(amount) OVER(ORDER BY event_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS partition_last
FROM samples ORDER BY event_id;
```

One output row per event_id has default_last3 then 9, while partition_last is 9 for both. Explicit UNBOUNDED FOLLOWING makes the second frame cover the entire partition. The function name alone does not determine whether last means current prefix or complete sequence.

## Exercises

1. **Compare row and peer running totals.** For customer a only, return event_id, row_total, peer_total. Use ROWS with occurred_at, event_id for row_total and RANGE with occurred_at alone for peer_total. Both frames start at UNBOUNDED PRECEDING and end at CURRENT ROW. Order final rows by event_id.

**Inputs/evidence:** For sql-deep-03 Exercise 1, For customer a only, return event_id, row_total, peer_total. Use ROWS with occurred_at, event_id for row_total and RANGE with occurred_at alone for peer_total. Both frames start at UNBOUNDED PRECEDING and end at CURRENT ROW. Order final rows by event_id.

**Expected result/shape:** For sql-deep-03 Exercise 1, IDs 1..5 have row_total[1,3,6,10,15] and peer_total[3,3,6,10,15]. The two 10:00 events share only the peer-aware total.

**Verify:** For sql-deep-03 Exercise 1, inspect the tied timestamp rows together: ROWS advances by the full ordering while RANGE includes all peers at the same timestamp.

2. **Compare neighboring rows with neighboring peer groups.** For customer a, return event_id, two_rows, two_groups. The first frame is ROWS BETWEEN 1 PRECEDING AND CURRENT ROW ordered by timestamp, event_id; the second is GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW ordered by timestamp alone. Final order is event_id.

**Inputs/evidence:** For sql-deep-03 Exercise 2, For customer a, return event_id, two_rows, two_groups. The first frame is ROWS BETWEEN 1 PRECEDING AND CURRENT ROW ordered by timestamp, event_id; the second is GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW ordered by timestamp alone. Final order is event_id.

**Expected result/shape:** For sql-deep-03 Exercise 2, two_rows is[1,3,5,7,9] and two_groups is[3,3,6,7,9]. At event 3 the previous peer group contains both events 1 and 2.

**Verify:** For sql-deep-03 Exercise 2, write each frame membership as a set of event IDs for the tied rows and boundary rows; sum amounts from those memberships independently.

3. **Distinguish the three exclusion policies.** For customer a, return event_id, without_current, without_group, without_other_ties using a RANGE unbounded-preceding-to-current frame ordered by timestamp. Apply EXCLUDE CURRENT ROW, EXCLUDE GROUP and EXCLUDE TIES respectively. Preserve NULL for empty frames and order by event_id.

**Inputs/evidence:** For sql-deep-03 Exercise 3, For customer a, return event_id, without_current, without_group, without_other_ties using a RANGE unbounded-preceding-to-current frame ordered by timestamp. Apply EXCLUDE CURRENT ROW, EXCLUDE GROUP and EXCLUDE TIES respectively. Preserve NULL for empty frames and order by event_id.

**Expected result/shape:** For sql-deep-03 Exercise 3, ID 1 gives 2, NULL,1; ID 2 gives 1, NULL,2; ID 3 gives 3,3,6; ID 4 gives 6,6,10; ID 5 gives 10,10,15.

**Verify:** For sql-deep-03 Exercise 3, compare CURRENT ROW, GROUP and TIES using the same base frame; confirm TIES retains the current row while removing its other peers.

4. **Make LAST_VALUE refer to the intended horizon.** For customer a, return event_id, prefix_last, partition_last. Order both windows by timestamp, event_id. Use the default ordered frame for prefix_last and explicit ROWS UNBOUNDED PRECEDING TO UNBOUNDED FOLLOWING for partition_last. Final order is event_id.

**Inputs/evidence:** For sql-deep-03 Exercise 4, For customer a, return event_id, prefix_last, partition_last. Order both windows by timestamp, event_id. Use the default ordered frame for prefix_last and explicit ROWS UNBOUNDED PRECEDING TO UNBOUNDED FOLLOWING for partition_last. Final order is event_id.

**Expected result/shape:** For sql-deep-03 Exercise 4, prefix_last is[1,2,3,4,5], while partition_last is 5 for every row. No row is removed or collapsed.

**Verify:** For sql-deep-03 Exercise 4, compare the default frame last value with a frame extending to UNBOUNDED FOLLOWING; check both peer groups and the final row.

5. **Build a strictly prior elapsed-time feature.** For all customers return event_id, prior_30m over [occurred_at-30minutes, occurred_at), excluding every event at the current timestamp. Use a timestamp RANGE frame plus EXCLUDE GROUP and partition by customer_id. Treat an empty complete-log window as zero. Order by event_id.

**Inputs/evidence:** For sql-deep-03 Exercise 5, For all customers return event_id, prior_30m over [occurred_at-30minutes, occurred_at), excluding every event at the current timestamp. Use a timestamp RANGE frame plus EXCLUDE GROUP and partition by customer_id. Treat an empty complete-log window as zero. Order by event_id.

**Expected result/shape:** For sql-deep-03 Exercise 5, IDs 1..7 yield prior_30m[0,0,3,3,0,0,10]. Event 4 includes the exact 10:10 lower boundary; event 5 excludes 10:40 because it is 31 minutes old.

**Verify:** For sql-deep-03 Exercise 5, enumerate timestamps inside the elapsed-time interval and exclude every event at the current timestamp; confirm a prior physical row with the same timestamp cannot leak.

6. **Derive sessions in separate window stages.** Define a new session for a customer's first event or a gap strictly greater than 30 minutes. Return customer_id, session_id, event_count, first_event_id, last_event_id, one row per customer/session, ordered by customer_id, session_id. Use deterministic timestamp, event_id ordering and separate lag, flag, cumulative stages.

**Inputs/evidence:** For sql-deep-03 Exercise 6, Define a new session for a customer's first event or a gap strictly greater than 30 minutes. Return customer_id, session_id, event_count, first_event_id, last_event_id, one row per customer/session, ordered by customer_id, session_id. Use deterministic timestamp, event_id ordering and separate lag, flag, cumulative stages.

**Expected result/shape:** For sql-deep-03 Exercise 6, Rows are(a,1,4,1,4),(a,2,1,5,5),(b,1,2,6,7). Exact 30-minute gaps stay in the same session; the 31-minute a gap starts session 2.

**Verify:** For sql-deep-03 Exercise 6, compute each lag gap, then the break flag, then its cumulative sum in separate stages; check exactly the threshold and the first event of each user.

## Common mistakes and diagnosis

If a running total jumps across tied timestamps, inspect RANGE peers before assuming duplicate ingestion. If adding a tie breaker changes a peer-aware result, recognize that the peer definition changed. If a prior feature includes same-time events, compare EXCLUDE CURRENT ROW with EXCLUDE GROUP. If LAST_VALUE returns the current value, inspect its frame end. If session logic raises a nested-window error, separate the lag and cumulative calculations into CTEs. Always distinguish the inner window order from the final result order.

## Self-check

- Explain the row grain after each FROM, JOIN, filter, grouping or window step. Name the identity columns that prove rows were neither lost nor multiplied.
- Reconstruct a boundary result by hand, then compare with the query output. Explain why the tempting wrong query fails even if it returns the same total on an easier fixture.

## Next step

Transfer the same reasoning to a new small fixture before using it on larger data, then continue with [the next deepening lesson](sql_deep_04.md). Keep the result columns, ordering, NULL policy and observation horizon explicit. The [professional SQL track](../README.md) provides the wider route.

## Primary sources and official APIs

- [PostgreSQL17 window-frame syntax and exclusions](https://www.postgresql.org/docs/17/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS).

- [PostgreSQL17 window functions](https://www.postgresql.org/docs/17/functions-window.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through sql-deep-03: ROWS, RANGE, GROUPS, Exclusions, and Sessionization.
Read sql/professional/companion-guides/sql_deep_03.md and sql/professional/lessons/sql_deep_03.sql. Direct prerequisites: sql-22, sql-analytics-01.
Explain the row grain and SQL clauses, then ask me to predict a concrete result before my attempt. Give one hint at a time and review my exact result rows, identity, NULL behavior and boundary evidence. Ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt.
Use only the prepared local disposable advanced_sql_training database and the complete rollback-safe script. Preserve my ignored working copy and do not start services or redirect to another database.
Done when all six projected-result contracts and their counterexamples have inspected evidence and I can explain why the wrong query fails.
```
