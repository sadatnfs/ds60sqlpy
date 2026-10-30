# Metric Algebra Across Grains, Snapshots, and Weighted Bridges

**Stable ID:** `sql-deep-02`. **Estimated time:** 150 minutes, split across reading and query investigation.

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-deep-02**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-deep-02/lesson/workspace/sql/professional/lessons/sql_deep_02.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-deep-02
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced. The guide defines each new mechanism before relying on it.
- **Prerequisites:** [`sql-quality-01`](sql_quality_01_bags_and_fanout.md), [`sql-analytics-01`](sql_analytics_01_query_patterns.md).
- **Artifacts:** [Learner SQL](../lessons/sql_deep_02.sql), [explained reference](../solutions/sql_deep_02_solutions.md), and [executable reference](../solutions/sql_deep_02_solutions.sql). Every fixture is local, deterministic and rolled back; no prior lesson state is required.

## Learning objectives

- State the output grain and identity before writing a query, including the NULL and duplicate policies.
- Explain the new SQL mechanism, produce each exact projected result and expose the listed counterexample.
- Verify rollback-safe behavior from inspected result rows and assertions without relying on a final success message.

## Vocabulary and concepts

- **Additive measure:** A quantity that can be summed across specified dimensions without changing its meaning, such as distinct transaction amounts across customers.

- **Semi-additive measure:** A quantity that can be summed across some dimensions but not others, such as inventory across products at one time but not across dates.

- **Ratio of totals:** A ratio formed after summing its numerator and denominator, which generally differs from an unweighted mean of unit ratios.

- **Allocation bridge:** Rows assigning fractions of a fact to categories; weights must satisfy an explicit conservation rule before allocated measures are trusted.

Correct join cardinality is necessary but not sufficient for a correct metric. Even one row per customer can support several different averages. Revenue divided by visits across all customers weights each visit equally. Averaging each customer's revenue-per-visit weights each customer with a defined ratio equally. The two estimands differ when activity varies, even if neither query duplicates a row.

A zero denominator represents an undefined ratio, not automatically zero efficiency. NULLIF(denominator,0) makes that undefined result visible, while counts of eligible and ratio-defined customers reveal how the mean's population changed. Replacing the ratio with zero changes both the value and interpretation of an average. Specify which population owns the decision before choosing a convenient expression.

Snapshot measures require a time contract. Inventory at a date can be summed across products, but summing daily inventory counts the same stock repeatedly. To report inventory as of a cutoff, choose the latest eligible snapshot separately for each product, with a deterministic tie rule, then aggregate. A missing new snapshot does not necessarily mean stock zero; it may mean carry forward the last known state, subject to a freshness policy.

Allocation bridges introduce intentional one-to-many relationships. If an order is attributed 60% to email and 40% to search, multiplying its amount by each weight preserves its total only when all valid weights sum to one. A bridge summing to 0.9 loses 10% of revenue; one summing to 1.2 invents 20%. Detect bad weight groups before reporting allocations and reconcile allocated totals to original facts.

Temporal dimensions can multiply facts even when an ordinary dimension key is not meant to be unique over history. The correct relationship is entity plus valid interval. Use half-open boundaries to choose the version active at the event instant. Overlapping versions create ambiguity, and an event in a gap is missing coverage. Count matching version identities rather than COUNT(*) after a left join, because the unmatched placeholder row is not a real version.

This lesson extends the existing fanout lesson by examining the algebra of measures, denominator weighting, state over time and deliberate fractional relationships. Every answer names its row identity and projected measures. A reconciled total is useful evidence, but it must accompany a correct target definition; two different estimands can both reconcile internally.

## Worked example / walkthrough

### Example 1

```sql
WITH groups (
  group_id,
  successes,
  trials
) AS (
  VALUES ('small', 1::numeric, 2),
    ('large', 9::numeric, 10))
SELECT
  'population' AS metric_id,
  round(sum(successes) / sum(trials), 3) AS trial_weighted_rate,
  round(avg(successes / trials), 3) AS equal_group_rate
FROM
  groups;
```

One output row keyed by metric_id has trial_weighted_rate0.833 and equal_group_rate0.700. The small group rate is 0.5 and large group rate 0.9. Summing first weights by trials; averaging the two ratios gives each group equal influence. Neither formula is inherently wrong, but they answer different questions.

### Example 2

```sql
WITH states (
  day,
  product_id,
  units
) AS (
  VALUES (DATE '2026-01-01', 1, 10),
    (DATE '2026-01-01', 2, 20),
    (DATE '2026-01-02', 1, 12),
    (DATE '2026-01-02', 2, 17))
SELECT
  day,
  sum(units) AS units_at_day
FROM
  states
GROUP BY
  day
ORDER BY
  day;
```

The result grain is one snapshot day, with columns day and units_at_day, ordered by day. Totals are 30 and 29. Adding those two totals to 59 does not describe inventory at either day; it sums repeated state measurements across time. The example makes the dimension along which summation is meaningful explicit.

## Exercises

1. **Preserve undefined customer ratios.** Return customer_id, revenue, visits, revenue_per_visit, ratio_defined from `deep2_usage`, one row per customer ordered by customer_id. Use NULLIF for a zero denominator and retain the zero-visit customer.

**Inputs/evidence:** For sql-deep-02 Exercise 1, Return customer_id, revenue, visits, revenue_per_visit, ratio_defined from `deep2_usage`, one row per customer ordered by customer_id. Use NULLIF for a zero denominator and retain the zero-visit customer.

**Expected result/shape:** For sql-deep-02 Exercise 1, Customer 1 ratio 10, true; customer 2 ratio 30, true; customer 3 ratioNULL, false. Revenue/visits remain 10/1,90/3,0/0.

**Verify:** For sql-deep-02 Exercise 1, recompute each numerator and denominator from its customer rows; retain a NULL ratio when the denominator is zero rather than substituting an observed zero.

2. **Compare ratio weighting and population counts.** Return one row keyed by metric_id=all_customers with columns metric_id, customer_count, defined_ratio_count, ratio_of_totals, mean_customer_ratio. Compute both ratio targets from the same source, retaining the denominator policy from Exercise 1.

**Inputs/evidence:** For sql-deep-02 Exercise 2, Return one row keyed by metric_id=all_customers with columns metric_id, customer_count, defined_ratio_count, ratio_of_totals, mean_customer_ratio. Compute both ratio targets from the same source, retaining the denominator policy from Exercise 1.

**Expected result/shape:** For sql-deep-02 Exercise 2, The row is all_customers,3,2,25,20. Ratio of totals uses 100 revenue/4 visits, while the mean customer ratio averages 10 and 30.

**Verify:** For sql-deep-02 Exercise 2, calculate the pooled numerator divided by the pooled denominator independently of the average of defined customer ratios; report how many customer ratios each calculation includes.

3. **Choose one state per product at a cutoff.** As of 2026-01-02, return product_id, snapshot_day, units from the latest eligible stock snapshot per product. Break same-day ties by greatest snapshot_id. One row represents one product and final order is product_id. Exclude the future January 3 snapshot.

**Inputs/evidence:** For sql-deep-02 Exercise 3, As of 2026-01-02, return product_id, snapshot_day, units from the latest eligible stock snapshot per product. Break same-day ties by greatest snapshot_id. One row represents one product and final order is product_id. Exclude the future January 3 snapshot.

**Expected result/shape:** For sql-deep-02 Exercise 3, Product 1 uses January 2 units 12 and product 2 uses January 2 units 17. Their as-of total is 29; product 1 future units 99 must not enter.

**Verify:** For sql-deep-02 Exercise 3, check the chosen timestamp is at or before the cutoff and no later eligible snapshot exists for the same product; sum only those chosen states.

4. **Audit allocation conservation before aggregation.** Return order_id, weight_sum only for orders whose total bridge weight is not exactly 1, including orders with no bridge rows. Preserve one diagnostic row per invalid order and order by order_id. Use exact numeric weights from the fixture.

**Inputs/evidence:** For sql-deep-02 Exercise 4, Return order_id, weight_sum only for orders whose total bridge weight is not exactly 1, including orders with no bridge rows. Preserve one diagnostic row per invalid order and order by order_id. Use exact numeric weights from the fixture.

**Expected result/shape:** For sql-deep-02 Exercise 4, Only order 3 appears with weight_sum0.9. Orders 1 and 2 sum to 1. The diagnostic must exist before any channel totals are treated as complete allocations.

**Verify:** For sql-deep-02 Exercise 4, sum the bridge weights separately for each source identity before multiplying amounts; inspect the per-source weight-sum output to identify the source whose weights fail conservation.

5. **Repair and reconcile a weighted allocation.** Within this exercise savepoint, change order 3 direct weight to 0.3. Return channel, allocated_amount ordered by channel, requiring every order weight total to equal 1 before producing any allocations. Verify that channel amounts sum to original order total 200.

**Inputs/evidence:** For sql-deep-02 Exercise 5, Within this exercise savepoint, change order 3 direct weight to 0.3. Return channel, allocated_amount ordered by channel, requiring every order weight total to equal 1 before producing any allocations. Verify that channel amounts sum to original order total 200.

**Expected result/shape:** For sql-deep-02 Exercise 5, Rows are direct 12, email 120, search 68. A failed global weight gate would return no allocation rows rather than silently exclude the invalid order. Roll back the repair after the case.

**Verify:** For sql-deep-02 Exercise 5, compare the repaired source-level weight sums with one and reconcile the allocated total to the original source total; inspect the named destination allocation as well.

6. **Expose temporal dimension ambiguity without multiplying events.** For every event return event_id, match_count, segment, match_status. Match customer history over valid_from<=occurred_at<valid_to. Only exactly one version supplies segment; zero matches is missing and multiple matches is ambiguous. One row per event, ordered by event_id.

**Inputs/evidence:** For sql-deep-02 Exercise 6, For every event return event_id, match_count, segment, match_status. Match customer history over valid_from<=occurred_at<valid_to. Only exactly one version supplies segment; zero matches is missing and multiple matches is ambiguous. One row per event, ordered by event_id.

**Expected result/shape:** For sql-deep-02 Exercise 6, Event 1 is 1, basic, matched; event 2 is 1, premium, matched; event 3 is 2, NULL, ambiguous; event 4 is 0, NULL, missing. The exact January 2 boundary belongs only to premium.

**Verify:** For sql-deep-02 Exercise 6, count effective interval matches per event before choosing a dimension value; preserve an event with zero matches and expose an event with multiple matches instead of arbitrary deduplication.

## Common mistakes and diagnosis

If average ratios disagree with a ratio of totals, calculate their implicit weights before declaring either query wrong. If stock grows merely because more dates were loaded, inspect whether snapshots were summed across time. If allocation totals fail reconciliation, audit weight sums per original fact before aggregating categories. If a temporal join duplicates an event, count matching version IDs and expose overlapping intervals. Never use SUM(DISTINCT amount) to repair multiplicity: different facts can legitimately share the same amount and would then be lost.

## Self-check

- Explain the row grain after each FROM, JOIN, filter, grouping or window step. Name the identity columns that prove rows were neither lost nor multiplied.
- Reconstruct a boundary result by hand, then compare with the query output. Explain why the tempting wrong query fails even if it returns the same total on an easier fixture.

## Next step

Transfer the same reasoning to a new small fixture before using it on larger data, then continue with [the next deepening lesson](sql_deep_03.md). Keep the result columns, ordering, NULL policy and observation horizon explicit. The [professional SQL track](../README.md) provides the wider route.

## Primary sources and official APIs

- [PostgreSQL aggregate semantics](https://www.postgresql.org/docs/17/functions-aggregate.html).

- [PostgreSQL DISTINCT ON and ordering](https://www.postgresql.org/docs/17/sql-select.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through sql-deep-02: Metric Algebra Across Grains, Snapshots, and Weighted Bridges.
Read sql/professional/companion-guides/sql_deep_02.md and sql/professional/lessons/sql_deep_02.sql. Direct prerequisites: sql-quality-01, sql-analytics-01.
Explain the row grain and SQL clauses, then ask me to predict a concrete result before my attempt. Give one hint at a time and review my exact result rows, identity, NULL behavior and boundary evidence. Ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt.
Use only the prepared local disposable advanced_sql_training database and the complete rollback-safe script. Preserve my ignored working copy and do not start services or redirect to another database.
Done when all six projected-result contracts and their counterexamples have inspected evidence and I can explain why the wrong query fails.
```
