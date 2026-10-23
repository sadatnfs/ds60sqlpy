# sql-deep-03: Explained reference solutions

Read [ROWS, RANGE, GROUPS, Exclusions, and Sessionization](../companion-guides/sql_deep_03.md) and attempt its six queries before comparing. The [complete reference script](sql_deep_03_solutions.sql) recreates the same temporary fixture, runs every answer inside its own savepoint, compares exact JSON row sets with fail-fast assertions, then rolls back. No permanent table, role or service is changed.

## Exercises and reasoning

## Exercise 1: Compare row and peer running totals

For customer a only, return event_id, row_total, peer_total. Use ROWS with occurred_at, event_id for row_total and RANGE with occurred_at alone for peer_total. Both frames start at UNBOUNDED PRECEDING and end at CURRENT ROW. Order final rows by event_id.

**Inputs/evidence:** For sql-deep-03 Exercise 1, For customer a only, return event_id, row_total, peer_total. Use ROWS with occurred_at, event_id for row_total and RANGE with occurred_at alone for peer_total. Both frames start at UNBOUNDED PRECEDING and end at CURRENT ROW. Order final rows by event_id.

**Expected result/shape:** For sql-deep-03 Exercise 1, IDs 1..5 have row_total[1,3,6,10,15] and peer_total[3,3,6,10,15]. The two 10:00 events share only the peer-aware total.

**Verify:** For sql-deep-03 Exercise 1, inspect the tied timestamp rows together: ROWS advances by the full ordering while RANGE includes all peers at the same timestamp.

```sql
SELECT event_id,
 sum(amount) OVER(ORDER BY occurred_at,event_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS row_total,
 sum(amount) OVER(ORDER BY occurred_at RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS peer_total
FROM deep3_events WHERE customer_id='a' ORDER BY event_id;
```

Filtering to customer a occurs before window evaluation, so the frame contains only those five events. The row-based ordering includes event_id to resolve equal timestamps deterministically. The peer-based ordering deliberately omits it so both 10:00 rows are peers. The different first result is the required counterexample: identical source grain and aggregate function do not imply identical frame semantics.

## Exercise 2: Compare neighboring rows with neighboring peer groups

For customer a, return event_id, two_rows, two_groups. The first frame is ROWS BETWEEN 1 PRECEDING AND CURRENT ROW ordered by timestamp, event_id; the second is GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW ordered by timestamp alone. Final order is event_id.

**Inputs/evidence:** For sql-deep-03 Exercise 2, For customer a, return event_id, two_rows, two_groups. The first frame is ROWS BETWEEN 1 PRECEDING AND CURRENT ROW ordered by timestamp, event_id; the second is GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW ordered by timestamp alone. Final order is event_id.

**Expected result/shape:** For sql-deep-03 Exercise 2, two_rows is[1,3,5,7,9] and two_groups is[3,3,6,7,9]. At event 3 the previous peer group contains both events 1 and 2.

**Verify:** For sql-deep-03 Exercise 2, write each frame membership as a set of event IDs for the tied rows and boundary rows; sum amounts from those memberships independently.

```sql
SELECT event_id,
 sum(amount) OVER(ORDER BY occurred_at,event_id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS two_rows,
 sum(amount) OVER(ORDER BY occurred_at GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW) AS two_groups
FROM deep3_events WHERE customer_id='a' ORDER BY event_id;
```

The GROUPS offset counts distinct ordering-value groups, so one preceding group may contribute several rows. A ROWS offset counts individual ordered positions. Neither frame represents a fixed elapsed duration: the gap from 10:10 to 10:40 is irrelevant to their membership. Use an interval RANGE frame when the scientific question refers to time rather than row or peer count.

## Exercise 3: Distinguish the three exclusion policies

For customer a, return event_id, without_current, without_group, without_other_ties using a RANGE unbounded-preceding-to-current frame ordered by timestamp. Apply EXCLUDE CURRENT ROW, EXCLUDE GROUP and EXCLUDE TIES respectively. Preserve NULL for empty frames and order by event_id.

**Inputs/evidence:** For sql-deep-03 Exercise 3, For customer a, return event_id, without_current, without_group, without_other_ties using a RANGE unbounded-preceding-to-current frame ordered by timestamp. Apply EXCLUDE CURRENT ROW, EXCLUDE GROUP and EXCLUDE TIES respectively. Preserve NULL for empty frames and order by event_id.

**Expected result/shape:** For sql-deep-03 Exercise 3, ID 1 gives 2, NULL,1; ID 2 gives 1, NULL,2; ID 3 gives 3,3,6; ID 4 gives 6,6,10; ID 5 gives 10,10,15.

**Verify:** For sql-deep-03 Exercise 3, compare CURRENT ROW, GROUP and TIES using the same base frame; confirm TIES retains the current row while removing its other peers.

```sql
SELECT event_id,
 sum(amount) OVER(ORDER BY occurred_at RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE CURRENT ROW) AS without_current,
 sum(amount) OVER(ORDER BY occurred_at RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE GROUP) AS without_group,
 sum(amount) OVER(ORDER BY occurred_at RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE TIES) AS without_other_ties
FROM deep3_events WHERE customer_id='a' ORDER BY event_id;
```

At 10:00, excluding only the current row leaves the other same-time event, excluding the group leaves no rows, and excluding ties retains only the current event. Later unique timestamps have no other peers, so EXCLUDE TIES retains the full prefix. NULL is the actual SUM result over the empty group-excluded frame. These outputs prevent an accidental claim that current-row exclusion means all strictly earlier times.

## Exercise 4: Make LAST_VALUE refer to the intended horizon

For customer a, return event_id, prefix_last, partition_last. Order both windows by timestamp, event_id. Use the default ordered frame for prefix_last and explicit ROWS UNBOUNDED PRECEDING TO UNBOUNDED FOLLOWING for partition_last. Final order is event_id.

**Inputs/evidence:** For sql-deep-03 Exercise 4, For customer a, return event_id, prefix_last, partition_last. Order both windows by timestamp, event_id. Use the default ordered frame for prefix_last and explicit ROWS UNBOUNDED PRECEDING TO UNBOUNDED FOLLOWING for partition_last. Final order is event_id.

**Expected result/shape:** For sql-deep-03 Exercise 4, prefix_last is[1,2,3,4,5], while partition_last is 5 for every row. No row is removed or collapsed.

**Verify:** For sql-deep-03 Exercise 4, compare the default frame last value with a frame extending to UNBOUNDED FOLLOWING; check both peer groups and the final row.

```sql
SELECT event_id,
 last_value(amount) OVER(ORDER BY occurred_at,event_id) AS prefix_last,
 last_value(amount) OVER(ORDER BY occurred_at,event_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS partition_last
FROM deep3_events WHERE customer_id='a' ORDER BY event_id;
```

The unique event_id tie break makes each current ordered position distinct, so the default frame ends at that event and LAST_VALUE returns its amount. The explicit following bound changes the frame horizon without changing output grain. This is useful for retrospective sequence summaries but would leak future information if partition_last were used as a feature at an earlier event time.

## Exercise 5: Build a strictly prior elapsed-time feature

For all customers return event_id, prior_30m over [occurred_at-30minutes, occurred_at), excluding every event at the current timestamp. Use a timestamp RANGE frame plus EXCLUDE GROUP and partition by customer_id. Treat an empty complete-log window as zero. Order by event_id.

**Inputs/evidence:** For sql-deep-03 Exercise 5, For all customers return event_id, prior_30m over [occurred_at-30minutes, occurred_at), excluding every event at the current timestamp. Use a timestamp RANGE frame plus EXCLUDE GROUP and partition by customer_id. Treat an empty complete-log window as zero. Order by event_id.

**Expected result/shape:** For sql-deep-03 Exercise 5, IDs 1..7 yield prior_30m[0,0,3,3,0,0,10]. Event 4 includes the exact 10:10 lower boundary; event 5 excludes 10:40 because it is 31 minutes old.

**Verify:** For sql-deep-03 Exercise 5, enumerate timestamps inside the elapsed-time interval and exclude every event at the current timestamp; confirm a prior physical row with the same timestamp cannot leak.

```sql
SELECT event_id,COALESCE(sum(amount) OVER(
 PARTITION BY customer_id ORDER BY occurred_at
 RANGE BETWEEN INTERVAL '30 minutes' PRECEDING AND CURRENT ROW EXCLUDE GROUP),0) AS prior_30m
FROM deep3_events ORDER BY event_id;
```

The interval RANGE lower bound uses elapsed timestamp distance rather than a fixed number of events. EXCLUDE GROUP removes every current-timestamp peer, preserving strict prior-time semantics. COALESCE to zero is justified only because this fixture represents a complete nonmissing event log and an empty contributing set has known zero activity. Partitioning prevents customer b from borrowing customer a's history.

## Exercise 6: Derive sessions in separate window stages

Define a new session for a customer's first event or a gap strictly greater than 30 minutes. Return customer_id, session_id, event_count, first_event_id, last_event_id, one row per customer/session, ordered by customer_id, session_id. Use deterministic timestamp, event_id ordering and separate lag, flag, cumulative stages.

**Inputs/evidence:** For sql-deep-03 Exercise 6, Define a new session for a customer's first event or a gap strictly greater than 30 minutes. Return customer_id, session_id, event_count, first_event_id, last_event_id, one row per customer/session, ordered by customer_id, session_id. Use deterministic timestamp, event_id ordering and separate lag, flag, cumulative stages.

**Expected result/shape:** For sql-deep-03 Exercise 6, Rows are(a,1,4,1,4),(a,2,1,5,5),(b,1,2,6,7). Exact 30-minute gaps stay in the same session; the 31-minute a gap starts session 2.

**Verify:** For sql-deep-03 Exercise 6, compute each lag gap, then the break flag, then its cumulative sum in separate stages; check exactly the threshold and the first event of each user.

```sql
WITH previous AS (
 SELECT e.*,lag(occurred_at) OVER(PARTITION BY customer_id ORDER BY occurred_at,event_id) AS prior_at
 FROM deep3_events AS e
), flags AS (
 SELECT previous.*,CASE WHEN prior_at IS NULL OR occurred_at-prior_at>INTERVAL '30 minutes' THEN 1 ELSE 0 END AS begins
 FROM previous
), sessions AS (
 SELECT flags.*,sum(begins) OVER(PARTITION BY customer_id ORDER BY occurred_at,event_id ROWS UNBOUNDED PRECEDING) AS session_id
 FROM flags
)
SELECT customer_id,session_id,count(*) AS event_count,
 (array_agg(event_id ORDER BY occurred_at,event_id))[1] AS first_event_id,
 (array_agg(event_id ORDER BY occurred_at DESC,event_id DESC))[1] AS last_event_id
FROM sessions GROUP BY customer_id,session_id ORDER BY customer_id,session_id;
```

The first CTE adds prior timestamps without collapsing events. The next creates start flags, and the third cumulatively numbers them within each customer. Only the final GROUP BY changes grain to one session. Ordered array aggregates select entire event identities at sequence endpoints rather than assuming the smallest or largest numeric ID always corresponds to time. The strict greater-than boundary is verified by both exact 30-minute and 31-minute gaps.

## Verification and transaction boundary

Every answer is materialized into a temporary answer table and compared with a literal expected row set, including column names, NULL values and deterministic order. The assertion function rejects both false and unknown Boolean results, so a NULL comparison cannot silently pass. Each exercise rolls back to its own savepoint, ensuring mutations used for one boundary case do not alter the next. The final ROLLBACK removes the full fixture. Read the first error if a contract fails; a later row count or command tag cannot repair an earlier failed assertion.
