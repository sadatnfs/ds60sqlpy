# Day 59 Solution — Integrated Stakeholder Analytics

Day 59 is a capstone checkpoint, not a pair of discrete exercises. Its
deliverables are a reconciled KPI suite, performance evidence, stakeholder
queries, and a large-scale design note. The canonical executable checkpoint is
[`day59_solutions.sql`](day59_solutions.sql).

## Deliverable 1 — Business KPI suite

### LTV by signup cohort and segment

```sql
SET search_path TO training, public;

WITH customer_ltv AS (
  SELECT c.customer_id,
         c.country,
         COALESCE(c.segment, 'standard') AS segment,
         date_trunc('month', c.created_at)::date AS cohort_month,
         COALESCE(SUM(o.total_amount), 0) AS ltv
  FROM customers c
  LEFT JOIN orders o USING (customer_id)
  GROUP BY c.customer_id, c.country, c.segment, date_trunc('month', c.created_at)
)
SELECT cohort_month,
       segment,
       COUNT(*) AS customers,
       ROUND(AVG(ltv), 2) AS avg_ltv,
       ROUND(SUM(ltv), 2) AS total_ltv
FROM customer_ltv
GROUP BY cohort_month, segment
ORDER BY cohort_month DESC, total_ltv DESC;
```

Expected grain: one row per `(cohort_month, segment)`, including customers with
zero orders.

### Ninety-day conversion funnel

```sql
SET search_path TO training, public;

WITH activity AS (
  SELECT c.customer_id,
         BOOL_OR(e.event_type = 'page_view') AS viewed,
         BOOL_OR(e.event_type = 'add_to_cart') AS added,
         BOOL_OR(e.event_type = 'checkout') AS checked_out,
         EXISTS (
           SELECT 1
           FROM orders o
           WHERE o.customer_id = c.customer_id
             AND o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
         ) AS bought
  FROM customers c
  LEFT JOIN events e
    ON e.customer_id = c.customer_id
   AND e.event_time >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY c.customer_id
)
SELECT COUNT(*) FILTER (WHERE viewed) AS viewers,
       COUNT(*) FILTER (WHERE added) AS adders,
       COUNT(*) FILTER (WHERE checked_out) AS checkouts,
       COUNT(*) FILTER (WHERE bought) AS buyers,
       ROUND(
         COUNT(*) FILTER (WHERE bought)::numeric
           / NULLIF(COUNT(*) FILTER (WHERE viewed), 0),
         4
       ) AS viewer_to_buyer_rate
FROM activity;
```

Expected shape: one row. Every funnel stage is measured at customer grain, but
the synthetic data does not enforce strict stage ordering.

### Product-pair affinity

The learner script already supplies the runnable market-basket query. Its
deliverable is the 20 most frequent distinct product pairs. Deduplicate
`(order_id, product_id)` first and enforce `a.product_id < b.product_id`; this
prevents self-pairs and reversed duplicates. The metric is co-occurrence count,
despite the starter comment saying “revenue.”

## Deliverable 2 — Performance evidence

```sql
BEGIN;
SET search_path TO training, public;

CREATE INDEX idx_orders_customer_date_day59_solution
  ON orders(customer_id, order_date) INCLUDE (total_amount);

EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, SUM(total_amount) AS revenue
FROM orders
WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days'
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 50;

ROLLBACK;
```

Save the actual plan, execution time, buffer counts, and result reconciliation.
The compact seed may correctly use a sequential scan; index presence does not
guarantee index use.

## Deliverable 3 — Stakeholder queries

### Finance: YTD budget versus actual

```sql
SET search_path TO training, public;

WITH actual AS (
  SELECT category, SUM(amount) AS actual
  FROM expenses
  WHERE expense_date >= date_trunc('year', CURRENT_DATE)
  GROUP BY category
), budget AS (
  SELECT category, SUM(amount) AS budget
  FROM budgets
  WHERE period >= date_trunc('year', CURRENT_DATE)
  GROUP BY category
)
SELECT COALESCE(a.category, b.category) AS category,
       ROUND(COALESCE(b.budget, 0), 2) AS budget,
       ROUND(COALESCE(a.actual, 0), 2) AS actual,
       ROUND(COALESCE(a.actual, 0) - COALESCE(b.budget, 0), 2) AS variance
FROM actual a
FULL OUTER JOIN budget b USING (category)
ORDER BY category;
```

Expected grain: one row per category found in actuals or budget.

### Marketing: campaign-assisted purchases

The learner query anchors on each customer's first order and counts distinct
customers with a campaign touch in the preceding seven days. Document that
definition: it is first-purchase assistance, not all-purchase event attribution
from Day 48. Multiple campaigns can assist one customer, so campaign rows are
not additive.

## Deliverable 4 — Large-scale design note

For a hypothetical 100M-row deployment, record:

- candidate range partition keys (`orders.order_date`, `events.event_time`);
- proof that critical predicates constrain those keys for pruning;
- local/partial indexes on hot recent partitions;
- retention and partition-maintenance ownership; and
- an observed representative-scale plan, not an assumed benefit.

## Capstone checkpoint limits

- Days 59–60 provide sign-off criteria rather than neatly isolated exercises.
- The current executable solution selects representative KPI, finance, and
  performance checks; the learner starter contains the product-pair and
  marketing queries that must also be discussed in the final write-up.
- All DDL in the solution transaction rolls back. Production changes require a
  separate reviewed migration.
