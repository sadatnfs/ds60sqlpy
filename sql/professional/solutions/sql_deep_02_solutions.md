# sql-deep-02: Explained reference solutions

Read [Metric Algebra Across Grains, Snapshots, and Weighted Bridges](../companion-guides/sql_deep_02.md) and attempt its six queries before comparing. The [complete reference script](sql_deep_02_solutions.sql) recreates the same temporary fixture, runs every answer inside its own savepoint, compares exact JSON row sets with fail-fast assertions, then rolls back. No permanent table, role or service is changed.

## Exercises and reasoning

## Exercise 1: Preserve undefined customer ratios

Return customer_id, revenue, visits, revenue_per_visit, ratio_defined from deep 2_usage, one row per customer ordered by customer_id. Use NULLIF for a zero denominator and retain the zero-visit customer.

**Inputs/evidence:** For sql-deep-02 Exercise 1, Return customer_id, revenue, visits, revenue_per_visit, ratio_defined from deep 2_usage, one row per customer ordered by customer_id. Use NULLIF for a zero denominator and retain the zero-visit customer.

**Expected result/shape:** For sql-deep-02 Exercise 1, Customer 1 ratio 10, true; customer 2 ratio 30, true; customer 3 ratioNULL, false. Revenue/visits remain 10/1,90/3,0/0.

**Verify:** For sql-deep-02 Exercise 1, recompute each numerator and denominator from its customer rows; retain a NULL ratio when the denominator is zero rather than substituting an observed zero.

```sql
SELECT customer_id,revenue,visits,revenue/NULLIF(visits,0) AS revenue_per_visit,
 visits>0 AS ratio_defined FROM deep2_usage ORDER BY customer_id;
```

NULLIF converts only a zero denominator to NULL, preventing a division error while retaining an undefined ratio. The separate ratio_defined flag exposes why the ratio is missing. Keeping customer 3 preserves the original customer population even though that customer cannot contribute a defined per-visit ratio. COALESCE of the ratio to zero would silently assert an efficiency value that was never measured.

## Exercise 2: Compare ratio weighting and population counts

Return one row keyed by metric_id=all_customers with columns metric_id, customer_count, defined_ratio_count, ratio_of_totals, mean_customer_ratio. Compute both ratio targets from the same source, retaining the denominator policy from Exercise 1.

**Inputs/evidence:** For sql-deep-02 Exercise 2, Return one row keyed by metric_id=all_customers with columns metric_id, customer_count, defined_ratio_count, ratio_of_totals, mean_customer_ratio. Compute both ratio targets from the same source, retaining the denominator policy from Exercise 1.

**Expected result/shape:** For sql-deep-02 Exercise 2, The row is all_customers,3,2,25,20. Ratio of totals uses 100 revenue/4 visits, while the mean customer ratio averages 10 and 30.

**Verify:** For sql-deep-02 Exercise 2, calculate the pooled numerator divided by the pooled denominator independently of the average of defined customer ratios; report how many customer ratios each calculation includes.

```sql
SELECT 'all_customers' AS metric_id,count(*) AS customer_count,
 count(revenue/NULLIF(visits,0)) AS defined_ratio_count,
 sum(revenue)/NULLIF(sum(visits),0) AS ratio_of_totals,
 avg(revenue/NULLIF(visits,0)) AS mean_customer_ratio
FROM deep2_usage;
```

Both measures use correct arithmetic but different weighting. The ratio of totals gives each visit equal influence and includes all source revenue in its numerator. AVG ignores NULL ratios, so its denominator is the two customers with visits, not all three customers. Reporting both population counts prevents readers from confusing an equal-customer summary with a visit-weighted operational rate.

## Exercise 3: Choose one state per product at a cutoff

As of 2026-01-02, return product_id, snapshot_day, units from the latest eligible stock snapshot per product. Break same-day ties by greatest snapshot_id. One row represents one product and final order is product_id. Exclude the future January 3 snapshot.

**Inputs/evidence:** For sql-deep-02 Exercise 3, As of 2026-01-02, return product_id, snapshot_day, units from the latest eligible stock snapshot per product. Break same-day ties by greatest snapshot_id. One row represents one product and final order is product_id. Exclude the future January 3 snapshot.

**Expected result/shape:** For sql-deep-02 Exercise 3, Product 1 uses January 2 units 12 and product 2 uses January 2 units 17. Their as-of total is 29; product 1 future units 99 must not enter.

**Verify:** For sql-deep-02 Exercise 3, check the chosen timestamp is at or before the cutoff and no later eligible snapshot exists for the same product; sum only those chosen states.

```sql
SELECT product_id,snapshot_day,units FROM (
 SELECT DISTINCT ON(product_id) product_id,snapshot_day,units,snapshot_id
 FROM deep2_stock WHERE snapshot_day<=DATE '2026-01-02'
 ORDER BY product_id,snapshot_day DESC,snapshot_id DESC
) AS latest ORDER BY product_id;
```

The cutoff filter removes future state before selecting the latest row. DISTINCT ON keeps the first row within each product under the explicitly descending version order. The outer ORDER BY states the final presentation order, separate from the inner selection order. Summing all snapshots would count state repeatedly, while selecting one global maximum date could omit products whose most recent eligible snapshot occurred earlier.

## Exercise 4: Audit allocation conservation before aggregation

Return order_id, weight_sum only for orders whose total bridge weight is not exactly 1, including orders with no bridge rows. Preserve one diagnostic row per invalid order and order by order_id. Use exact numeric weights from the fixture.

**Inputs/evidence:** For sql-deep-02 Exercise 4, Return order_id, weight_sum only for orders whose total bridge weight is not exactly 1, including orders with no bridge rows. Preserve one diagnostic row per invalid order and order by order_id. Use exact numeric weights from the fixture.

**Expected result/shape:** For sql-deep-02 Exercise 4, Only order 3 appears with weight_sum0.9. Orders 1 and 2 sum to 1. The diagnostic must exist before any channel totals are treated as complete allocations.

**Verify:** For sql-deep-02 Exercise 4, sum the bridge weights separately for each source identity before multiplying amounts; inspect the per-source weight-sum output to identify the source whose weights fail conservation.

```sql
SELECT o.order_id,COALESCE(sum(b.weight),0) AS weight_sum
FROM deep2_orders AS o LEFT JOIN deep2_bridge AS b ON b.order_id=o.order_id
GROUP BY o.order_id HAVING COALESCE(sum(b.weight),0)<>1
ORDER BY o.order_id;
```

Starting from orders ensures a completely missing bridge would also be diagnosed with total weight zero. Grouping by order_id checks conservation at the original fact grain before multiplying amounts. Exact numeric inputs make equality to one a deliberate contract; approximate floating weights would need a justified tolerance. A channel aggregate could otherwise look plausible while quietly losing part of an order's value.

## Exercise 5: Repair and reconcile a weighted allocation

Within this exercise savepoint, change order 3 direct weight to 0.3. Return channel, allocated_amount ordered by channel, requiring every order weight total to equal 1 before producing any allocations. Verify that channel amounts sum to original order total 200.

**Inputs/evidence:** For sql-deep-02 Exercise 5, Within this exercise savepoint, change order 3 direct weight to 0.3. Return channel, allocated_amount ordered by channel, requiring every order weight total to equal 1 before producing any allocations. Verify that channel amounts sum to original order total 200.

**Expected result/shape:** For sql-deep-02 Exercise 5, Rows are direct 12, email 120, search 68. A failed global weight gate would return no allocation rows rather than silently exclude the invalid order. Roll back the repair after the case.

**Verify:** For sql-deep-02 Exercise 5, compare the repaired source-level weight sums with one and reconcile the allocated total to the original source total; inspect the named destination allocation as well.

```sql
UPDATE deep2_bridge SET weight=0.3 WHERE order_id=3 AND channel='direct';
WITH weights AS (
 SELECT o.order_id,COALESCE(sum(b.weight),0) AS weight_sum
 FROM deep2_orders AS o LEFT JOIN deep2_bridge AS b ON b.order_id=o.order_id
 GROUP BY o.order_id
)
SELECT b.channel,sum(o.amount*b.weight) AS allocated_amount
FROM deep2_orders AS o JOIN deep2_bridge AS b ON b.order_id=o.order_id
WHERE NOT EXISTS(SELECT 1 FROM weights WHERE weight_sum<>1)
GROUP BY b.channel ORDER BY b.channel;
```

The global gate is evaluated before presenting the aggregate as a complete allocation. It does not hide a bad order by dropping only that order, which would silently change the total population. Multiplying each order amount by its bridge fraction then summing by channel preserves total value once every order conserves weight. The savepoint isolates the corrective fixture mutation so later examples still begin from known original data.

## Exercise 6: Expose temporal dimension ambiguity without multiplying events

For every event return event_id, match_count, segment, match_status. Match customer history over valid_from<=occurred_at<valid_to. Only exactly one version supplies segment; zero matches is missing and multiple matches is ambiguous. One row per event, ordered by event_id.

**Inputs/evidence:** For sql-deep-02 Exercise 6, For every event return event_id, match_count, segment, match_status. Match customer history over valid_from<=occurred_at<valid_to. Only exactly one version supplies segment; zero matches is missing and multiple matches is ambiguous. One row per event, ordered by event_id.

**Expected result/shape:** For sql-deep-02 Exercise 6, Event 1 is 1, basic, matched; event 2 is 1, premium, matched; event 3 is 2, NULL, ambiguous; event 4 is 0, NULL, missing. The exact January 2 boundary belongs only to premium.

**Verify:** For sql-deep-02 Exercise 6, count effective interval matches per event before choosing a dimension value; preserve an event with zero matches and expose an event with multiple matches instead of arbitrary deduplication.

```sql
SELECT e.event_id,count(h.version_id) AS match_count,
 CASE WHEN count(h.version_id)=1 THEN min(h.segment) END AS segment,
 CASE WHEN count(h.version_id)=0 THEN 'missing'
      WHEN count(h.version_id)=1 THEN 'matched' ELSE 'ambiguous' END AS match_status
FROM deep2_events AS e LEFT JOIN deep2_history AS h
 ON h.customer_id=e.customer_id AND h.valid_from<=e.occurred_at AND e.occurred_at<h.valid_to
GROUP BY e.event_id ORDER BY e.event_id;
```

The left join retains unmatched events, while counting the nonnull version_id distinguishes a real match from the left-join placeholder. Half-open bounds prevent adjacent versions from both owning the transition instant. min(segment) is used only after proving exactly one match, so it is not an arbitrary way to hide overlap. Returning one diagnostic row per event makes ambiguity visible without allowing raw history fanout to inflate downstream measures.

## Verification and transaction boundary

Every answer is materialized into a temporary answer table and compared with a literal expected row set, including column names, NULL values and deterministic order. The assertion function rejects both false and unknown Boolean results, so a NULL comparison cannot silently pass. Each exercise rolls back to its own savepoint, ensuring mutations used for one boundary case do not alter the next. The final ROLLBACK removes the full fixture. Read the first error if a contract fails; a later row count or command tag cannot repair an earlier failed assertion.
