# Metric Algebra Across Grains, Snapshots, and Weighted Bridges

**Stable ID:** `sql-deep-02`. **Estimated time:** 150 minutes, split across reading and query investigation.

## How to run this lesson

Use the private reader's **Create/open guided SQL notebook** action. It creates the ignored editable copy at `.learning/sql/sql-deep-02/lesson/workspace/sql/professional/lessons/sql_deep_02.sql`. Read the supplied fixture, write a prediction, edit that copy and run the complete script. The prepared target must be the local disposable `advanced_sql_training` database. These lessons never require a production connection or a new cloud service.

The learner file starts a transaction, checks the database name, creates only temporary tables, runs two worked examples and ends with ROLLBACK. Your six query attempts belong before that final rollback. Re-run the complete file after an error so the fixture and transaction state are known. Output appears in the notebook or terminal as named columns and bounded rows; a command tag alone does not verify a SELECT result.

Windows PowerShell fallback, from the repository root:

```powershell
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql/professional/lessons/sql_deep_02.sql"
```

macOS/Linux fallback, from the repository root:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_deep_02.sql
```

If the prepared database is unavailable, return to classroom setup rather than changing the target. Keep credentials outside lesson files and command text. Read the [learner SQL](../lessons/sql_deep_02.sql); keep [explanatory solutions](../solutions/sql_deep_02_solutions.md) and [executable solutions](../solutions/sql_deep_02_solutions.sql) closed until an attempt or an explicit worked comparison. PostgreSQL 16+ syntax is used; the canonical runtime is PostgreSQL 17.

## Level and prerequisites

Advanced. Direct catalog prerequisites: `sql-quality-01`, `sql-analytics-01`. The guide still defines each new mechanism before relying on it. Every fixture is local, deterministic and rolled back; no prior lesson state is required.

## Learning objectives

State the output grain and identity before writing a query. Explain the new SQL mechanism, produce each exact projected result, expose the listed counterexample and verify rollback-safe behavior without relying on a final success message.

## Vocabulary and mental model

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

## Worked examples and query anatomy

### Example 1

```sql
WITH groups(group_id,successes,trials) AS (VALUES ('small',1::numeric,2),('large',9::numeric,10))
SELECT 'population' AS metric_id,
 round(sum(successes)/sum(trials),3) AS trial_weighted_rate,
 round(avg(successes/trials),3) AS equal_group_rate
FROM groups;
```

One output row keyed by metric_id has trial_weighted_rate0.833 and equal_group_rate0.700. The small group rate is 0.5 and large group rate 0.9. Summing first weights by trials; averaging the two ratios gives each group equal influence. Neither formula is inherently wrong, but they answer different questions.

### Example 2

```sql
WITH states(day,product_id,units) AS (VALUES
 (DATE '2026-01-01',1,10),(DATE '2026-01-01',2,20),
 (DATE '2026-01-02',1,12),(DATE '2026-01-02',2,17))
SELECT day,sum(units) AS units_at_day FROM states GROUP BY day ORDER BY day;
```

The result grain is one snapshot day, with columns day and units_at_day, ordered by day. Totals are 30 and 29. Adding those two totals to 59 does not describe inventory at either day; it sums repeated state measurements across time. The example makes the dimension along which summation is meaningful explicit.

## Exercises

1. **Preserve undefined customer ratios.** Return customer_id, revenue, visits, revenue_per_visit, ratio_defined from deep 2_usage, one row per customer ordered by customer_id. Use NULLIF for a zero denominator and retain the zero-visit customer.

**Expected:** Customer 1 ratio 10, true; customer 2 ratio 30, true; customer 3 ratioNULL, false. Revenue/visits remain 10/1,90/3,0/0.

2. **Compare ratio weighting and population counts.** Return one row keyed by metric_id=all_customers with columns metric_id, customer_count, defined_ratio_count, ratio_of_totals, mean_customer_ratio. Compute both ratio targets from the same source, retaining the denominator policy from Exercise 1.

**Expected:** The row is all_customers,3,2,25,20. Ratio of totals uses 100 revenue/4 visits, while the mean customer ratio averages 10 and 30.

3. **Choose one state per product at a cutoff.** As of 2026-01-02, return product_id, snapshot_day, units from the latest eligible stock snapshot per product. Break same-day ties by greatest snapshot_id. One row represents one product and final order is product_id. Exclude the future January 3 snapshot.

**Expected:** Product 1 uses January 2 units 12 and product 2 uses January 2 units 17. Their as-of total is 29; product 1 future units 99 must not enter.

4. **Audit allocation conservation before aggregation.** Return order_id, weight_sum only for orders whose total bridge weight is not exactly 1, including orders with no bridge rows. Preserve one diagnostic row per invalid order and order by order_id. Use exact numeric weights from the fixture.

**Expected:** Only order 3 appears with weight_sum0.9. Orders 1 and 2 sum to 1. The diagnostic must exist before any channel totals are treated as complete allocations.

5. **Repair and reconcile a weighted allocation.** Within this exercise savepoint, change order 3 direct weight to 0.3. Return channel, allocated_amount ordered by channel, requiring every order weight total to equal 1 before producing any allocations. Verify that channel amounts sum to original order total 200.

**Expected:** Rows are direct 12, email 120, search 68. A failed global weight gate would return no allocation rows rather than silently exclude the invalid order. Roll back the repair after the case.

6. **Expose temporal dimension ambiguity without multiplying events.** For every event return event_id, match_count, segment, match_status. Match customer history over valid_from<=occurred_at<valid_to. Only exactly one version supplies segment; zero matches is missing and multiple matches is ambiguous. One row per event, ordered by event_id.

**Expected:** Event 1 is 1, basic, matched; event 2 is 1, premium, matched; event 3 is 2, NULL, ambiguous; event 4 is 0, NULL, missing. The exact January 2 boundary belongs only to premium.

## Common mistakes and diagnosis

If average ratios disagree with a ratio of totals, calculate their implicit weights before declaring either query wrong. If stock grows merely because more dates were loaded, inspect whether snapshots were summed across time. If allocation totals fail reconciliation, audit weight sums per original fact before aggregating categories. If a temporal join duplicates an event, count matching version IDs and expose overlapping intervals. Never use SUM(DISTINCT amount) to repair multiplicity: different facts can legitimately share the same amount and would then be lost.

## Self-check and retrieval

Explain the row grain after each FROM, JOIN, filter, grouping or window step in one exercise. Name the identity columns that prove rows were neither lost nor multiplied. Reconstruct a boundary result by hand, then compare with the query output. Explain why the tempting wrong query fails even if it returns the same total on an easier fixture.

## Next steps

Transfer the same reasoning to a new small fixture before using it on larger data. Keep the result columns, ordering, NULL policy and observation horizon explicit. The [professional SQL track](../README.md) contains the prerequisite operational and modeling lessons.

## Primary sources and official APIs

- [PostgreSQL aggregate semantics](https://www.postgresql.org/docs/17/functions-aggregate.html).

- [PostgreSQL DISTINCT ON and ordering](https://www.postgresql.org/docs/17/sql-select.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through sql-deep-02: Metric Algebra Across Grains, Snapshots, and Weighted Bridges.
Read sql/professional/companion-guides/sql_deep_02.md and sql/professional/lessons/sql_deep_02.sql. Direct prerequisites: sql-quality-01, sql-analytics-01.
Explain the row grain and SQL clauses, then ask me to predict a concrete result before my attempt. Give one hint at a time and review my exact result rows, identity, NULL behavior and boundary evidence. Ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt.
Use only the prepared local disposable advanced_sql_training database and the complete rollback-safe script. Preserve my ignored working copy and do not start services or redirect to another database.
Done when all six projected-result contracts and their counterexamples have inspected evidence and I can explain why the wrong query fails.
```
