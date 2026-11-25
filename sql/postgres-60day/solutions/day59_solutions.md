# Day 59 Solution: Integrated Stakeholder Analytics


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day59_solutions.sql
```

The script opens one transaction and prints, in order: the 192-row LTV
table, the one-row funnel with `viewer_to_buyer_rate` 0.3266 on our run, the
5-row Finance table, a `CREATE INDEX` tag and the top-50 plan, then the eight
exercise results with a second `CREATE INDEX` and plan before Exercise 5. It
ends with `ROLLBACK`, so neither `_day59_solution` index survives. Results
that use `now()` drift with the calendar. The
[solution-reading steps](../../STUDY-GUIDE.md#read-a-solution) explain how to
compare your transcript with this one.

## Clause-by-clause reading map

Read each query in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order),
and for each one name the grain before and after its widest join. Three
choices recur through the file:

- **Who is in the population.** The headline LTV query starts from
  `customers` and `LEFT JOIN`s `orders`, so the 62 customers without orders
  stay in with an LTV of 0. The funnel starts from all 500 customers so a
  stage can only shrink.
- **Which money measure is used.** LTV and Exercise 5 sum
  `orders.total_amount`; Exercise 3 and Exercise 8 set it beside the line sum
  and the payment sum, so a stakeholder chooses one with the gaps visible.
- **What breaks a tie.** Exercise 4's `LATERAL` subquery orders touches by
  `event_time DESC, event_id DESC` before `LIMIT 1`, and Exercise 7 ends its
  ranking with `product_a, product_b`.

Exercises 1 and 6 are inline `VALUES` lists: the answer is the documentation
itself, made queryable.

Day 59 is a capstone checkpoint, not a pair of discrete exercises. Its
deliverables are a reconciled KPI suite, performance evidence, stakeholder
queries, and a large-scale design note. The canonical executable checkpoint is
[`day59_solutions.sql`](day59_solutions.sql).

## Deliverable 1: Business KPI suite

### LTV by signup cohort and segment

```sql
SET search_path TO training, public;

WITH customer_ltv AS (
  SELECT
    c.customer_id,
    c.country,
    COALESCE(c.segment, 'standard') AS segment,
    date_trunc('month', c.created_at)::date AS cohort_month,
    COALESCE(SUM(o.total_amount), 0) AS ltv
  FROM
    customers c
    LEFT JOIN orders o USING (customer_id)
  GROUP BY
    c.customer_id, c.country, c.segment, date_trunc('month', c.created_at))
SELECT
  cohort_month,
  segment,
  COUNT(*) AS customers,
  ROUND(AVG(ltv), 2) AS avg_ltv,
  ROUND(SUM(ltv), 2) AS total_ltv
FROM
  customer_ltv
GROUP BY
  cohort_month,
  segment
ORDER BY
  cohort_month DESC,
  total_ltv DESC;
```

Expected grain: one row per `(cohort_month, segment)`, including customers with
zero orders.

### Ninety-day conversion funnel

```sql
SET search_path TO training, public;

WITH viewed_stage AS (
  SELECT
    c.customer_id,
    MIN(e.event_time) FILTER (WHERE e.event_type = 'page_view') AS viewed_at
  FROM
    customers c
    LEFT JOIN events e ON e.customer_id = c.customer_id
      AND e.event_time >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY
    c.customer_id
),
added_stage AS (
  SELECT
    v.customer_id,
    v.viewed_at,
    MIN(e.event_time) AS added_at
  FROM
    viewed_stage v
    LEFT JOIN events e ON e.customer_id = v.customer_id
      AND e.event_type = 'add_to_cart'
      AND e.event_time >= v.viewed_at
  GROUP BY
    v.customer_id,
    v.viewed_at
),
checkout_stage AS (
  SELECT
    a.customer_id,
    a.viewed_at,
    a.added_at,
    MIN(e.event_time) AS checkout_at
  FROM
    added_stage a
    LEFT JOIN events e ON e.customer_id = a.customer_id
      AND e.event_type = 'checkout'
      AND e.event_time >= a.added_at
  GROUP BY
    a.customer_id,
    a.viewed_at,
    a.added_at
),
purchase_stage AS (
  SELECT
    ch.customer_id,
    ch.viewed_at,
    ch.added_at,
    ch.checkout_at,
    MIN(o.order_date) AS purchased_at
  FROM
    checkout_stage ch
    LEFT JOIN orders o ON o.customer_id = ch.customer_id
      AND o.order_date >= ch.checkout_at
      AND o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY
    ch.customer_id,
    ch.viewed_at,
    ch.added_at,
    ch.checkout_at
),
activity AS (
  SELECT
    customer_id,
    viewed_at IS NOT NULL AS viewed,
    added_at IS NOT NULL
    AND added_at >= viewed_at AS added,
    checkout_at IS NOT NULL
    AND checkout_at >= added_at AS checked_out,
    purchased_at IS NOT NULL
    AND purchased_at >= checkout_at AS bought
  FROM
    purchase_stage
)
SELECT
  COUNT(*) FILTER (WHERE viewed) AS viewers,
  COUNT(*) FILTER (WHERE added) AS adders,
  COUNT(*) FILTER (WHERE checked_out) AS checkouts,
  COUNT(*) FILTER (WHERE bought) AS buyers,
  ROUND(COUNT(*) FILTER (WHERE bought)::numeric / NULLIF (COUNT(*) FILTER (WHERE viewed), 0), 4) AS viewer_to_buyer_rate
FROM
  activity;
```

Expected shape: one row. Every later funnel population is a subset of the
preceding population because its timestamp must follow the prior stage.

### Product-pair affinity

The learner script already supplies the runnable market-basket query. Its
deliverable is the 20 most frequent distinct product pairs. Deduplicate
`(order_id, product_id)` first and enforce `a.product_id < b.product_id`; this
prevents self-pairs and reversed duplicates. The metric is co-occurrence count,
despite the starter comment saying “revenue.”

## Deliverable 2: Performance evidence

```sql
BEGIN;
SET search_path TO training, public;

CREATE INDEX idx_orders_customer_date_day59_solution ON orders (customer_id, order_date) INCLUDE (total_amount);

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  customer_id,
  SUM(total_amount) AS revenue
FROM
  orders
WHERE
  order_date >= CURRENT_TIMESTAMP - interval '180 days'
GROUP BY
  customer_id
ORDER BY
  revenue DESC
LIMIT 50;

ROLLBACK;
```

Save the actual plan, execution time, buffer counts, and result reconciliation.
The compact seed may correctly use a sequential scan; index presence does not
guarantee index use.

## Deliverable 3: Stakeholder queries

### Finance: YTD budget versus actual

```sql
SET search_path TO training, public;

WITH actual AS (
  SELECT
    category,
    SUM(amount) AS actual
  FROM
    expenses
  WHERE
    expense_date >= date_trunc('year', CURRENT_DATE)
  GROUP BY
    category
),
budget AS (
  SELECT
    category,
    SUM(amount) AS budget
  FROM
    budgets
  WHERE
    period >= date_trunc('year', CURRENT_DATE)
  GROUP BY
    category
)
SELECT
  COALESCE(a.category, b.category) AS category,
  ROUND(COALESCE(b.budget, 0), 2) AS budget,
  ROUND(COALESCE(a.actual, 0), 2) AS actual,
  ROUND(COALESCE(a.actual, 0) - COALESCE(b.budget, 0), 2) AS variance
FROM
  actual a
  FULL OUTER JOIN budget b USING (category)
ORDER BY
  category;
```

Expected grain: one row per category found in actuals or budget.

### Marketing: campaign-assisted purchases

The learner query anchors on each customer's first order and counts distinct
customers with a campaign touch in the preceding seven days. The touch
whitelist is `page_view`, `add_to_cart`, and `checkout`; campaign metadata on a
different event type does not qualify. Document that definition: it is
first-purchase assistance, not all-purchase event attribution from Day 48.
Multiple campaigns can assist one customer, so campaign rows are not additive.

## Deliverable 4: Large-scale design note

For a hypothetical 100M-row deployment, record:

- candidate range partition keys (`orders.order_date`, `events.event_time`);
- proof that critical predicates constrain those keys for pruning;
- local/partial indexes on hot recent partitions;
- retention and partition-maintenance ownership; and
- an observed representative-scale plan, not an assumed benefit.

## Capstone checkpoint limits

- Days 59-60 provide sign-off criteria rather than neatly isolated exercises.
- The current executable solution selects representative KPI, finance, and
  performance checks; the learner starter contains the product-pair and
  marketing queries that must also be discussed in the final write-up.
- All DDL in the solution transaction rolls back. Production changes require a
  separate reviewed migration.

## Exercise 1: Make every grain transition explicit

The executable `grain_map` states the key and row meaning for order values,
customer LTV, and cohort/segment summary. A lower-grain join after aggregation
would invalidate the metric.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 1, read the learner LTV query in section 1a (`order_values`, then `ltv`, then `cohort`, then the grouped `SELECT`) and record each aggregation step in an inline `VALUES` fixture with `step_name`, `row_grain`, and `key_columns`.
- **Expected result/shape:** For sql-59 Exercise 1, expected output: 3 rows, one per `step_name`: `order_values` at one row per order keyed by `customer_id + order_id`, `customer_ltv` at one row per customer keyed by `customer_id`, and `cohort_segment_summary` at one row per cohort/segment keyed by `cohort_month + segment`. The final columns are `step_name`, `row_grain`, and `key_columns`.
- **Independent verification:** For sql-59 Exercise 1, prove each grain claim by running the learner CTEs: `order_values` has 4,362 rows and 4,362 distinct `order_id` values but only 438 distinct `customer_id` values, `ltv` has 438 rows (the order-to-customer step, since 62 of the 500 customers never ordered), `cohort` has 500, and the summary has 191 (`segment`, `cohort_month`) groups whose `customers` add back to 438 before `LIMIT 100` trims the output.
- **Intermediate relation check:** The `VALUES` list is the whole input: three rows, one per pipeline step. Run the learner's `order_values` CTE alone and check that `COUNT(*)` equals `COUNT(DISTINCT order_id)` at 4,362 before trusting the label "one row per order".
- **Clause check:** Only `FROM (VALUES ...) AS grain_map (step_name, row_grain, key_columns)` and `SELECT *` run. The column list after the alias names the three columns, so the row order printed is simply the order typed.
- **Alternative/trade-off:** A comment block above each CTE records the same facts, but a result set can be diffed between runs and joined to a test that counts rows per key. A fourth row for the learner's unused `first_order_month` column would make the map more honest about what the `ltv` CTE carries.
- **Edge case:** Add a lower-grain step after `customer_ltv`, such as one row per order line, and the map should flag that joining it back would multiply each customer's LTV by their line count.

## Exercise 2: Calculate funnel rates with a stable population

Start from all customers and derive the first valid timestamp at each ordered
stage. A later event counts only when it occurs at or after the prior stage.
Keep an independent buyer-without-view diagnostic, but do not mix it into the
ordered conversion numerators.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 2, derive `viewed_at`, `added_at`, `checkout_at`, and `purchased_at` per customer over the same trailing-90-day window.
- **Expected result/shape:** For sql-59 Exercise 2, expected output: exactly one summary row with ordered stage counts, `buyers_without_view`, and three conversion rates whose denominators are the preceding ordered populations.
- **Independent verification:** For sql-59 Exercise 2, confirm one row with 398 viewers, 340 adders, 275 checkouts, 130 buyers, `buyers_without_view` 29, and rates 0.8543, 0.8088, and 0.4727; the unordered reach counts for the same window (398 customers with a `page_view`, 399 with `add_to_cart`, 397 with `checkout`, 290 with an order) show why reach is not a funnel. In a rolled-back transaction give customer 45, who has no recent `page_view`, an `add_to_cart` 2 days ago and a `checkout` 1 day ago: every count stays the same. Add a `page_view` 3 days ago and the row becomes 399, 341, 276, and 130 with `buyers_without_view` 28, because the September order precedes the new checkout.
- **Intermediate relation check:** Run the four stage CTEs as plain `SELECT`s for customer 45, who has events in the window but no `page_view`: `viewed_stage` has no row for them, so `added_stage`, `checkout_stage`, and `purchase_stage` cannot have one either, and their September order is counted only in `buyers_without_view`.
- **Clause check:** For sql-59 Exercise 2, each staged `LEFT JOIN` retains the all-customer population while its timestamp predicate conditions the next stage on the previous one; aggregate `FILTER` then counts nested booleans.
- **Alternative/trade-off:** Counting each event type with its own `COUNT(DISTINCT customer_id)` is shorter, but on our run it reported 399 cart adders against 398 viewers, because it never asks whether the add came after the view. The staged `LEFT JOIN`s cost four passes over `events` and buy the nested populations the rates need.
- **Edge case:** Add checkout and purchase events that occur before add-to-cart; they must not count as ordered checkout or purchase stages.

## Exercise 3: Reconcile candidate money measures

Line values and payments each aggregate to `order_id` before joining orders.
The answer retains stored total, calculated line total, paid amount, and both
differences so stakeholders can choose a named measure.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 3, start from `orders` and `LEFT JOIN` two order-grain CTEs: `lines`, which sums `quantity * unit_price * (1 - discount)` from `order_items`, and `paid`, which sums `amount` from `payments`; derive `header_minus_lines` and `paid_minus_header` from the three amounts.
- **Expected result/shape:** For sql-59 Exercise 3, expected output: exactly 50 rows, `order_id` 1 through 50 in order, one per order. The final columns are `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`; orders 5, 9, 14, 20, 25, 27, 32, 40, 45, and 49 show NULL `paid_amount` and `paid_minus_header`.
- **Independent verification:** For sql-59 Exercise 3, confirm `lines` has 4,362 rows and `paid` has 3,489 rows built from 3,836 payment rows (347 orders have more than one payment), and that the absolute `header_minus_lines` never exceeds 0.0045 across all 4,362 orders. The ten NULL-payment orders are all `placed`. In a rolled-back transaction insert a second 10.00 payment for order 1 (header 240.20): the output stays at 50 rows, `paid` still has 3,489 rows, and order 1 shows `paid_amount` 250.20 and `paid_minus_header` 10.00.
- **Intermediate relation check:** Run `lines` alone: 4,362 rows, one per order, because every order has at least one line. Run `paid` alone: 3,489 rows, because 873 orders have no payment. That gap is why both joins to `orders` must be `LEFT JOIN`s.
- **Clause check:** Each CTE groups its own table to `order_id` first, then `orders` joins both with `USING (order_id)`. Grouping before joining keeps a multi-line order from repeating its payment amount once per line.
- **Alternative/trade-off:** Joining `order_items` and `payments` to `orders` in one `FROM` and grouping once is a common shortcut, but 347 orders have more than one payment, and each extra payment row would repeat that order's line revenue. Grouping each table before the join avoids that fanout entirely.
- **Edge case:** `header_minus_lines` values such as 0.0005 are cents rounding: the header is stored at two decimals while the line formula keeps four. Treat any absolute gap of 0.005 or more as a real defect; on our run there were none.

## Exercise 4: Include direct attribution

Start from purchases and choose at most one latest qualifying touch with a
LATERAL query. Missing touches become `(direct)`, so attribution counts
reconcile to the purchase population.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 4, start from `orders` and choose at most one event whose `event_type` is in the declared marketing-touch whitelist (`page_view`, `add_to_cart`, `checkout`), whose campaign metadata is present, and whose timestamp is in the preceding seven-day half-open window.
- **Expected result/shape:** For sql-59 Exercise 4, expected output: 6 rows, one per `attribution_bucket`: `(direct)` 2,895, `none` 310, `fall` 305, `spring` 288, `summer` 282, and `winter` 282, summing to 4,362 orders; `none` is a literal campaign value, not a missing one. The final order is `purchases DESC, attribution_bucket`.
- **Independent verification:** For sql-59 Exercise 4, assert that `SUM(purchases)` equals the 4,362 rows of `orders`. Then in a rolled-back transaction use order 31 (customer 5, currently `(direct)`): a `support` event tagged `spring` 1 day before the order changes nothing; adding a `page_view` tagged `fall` 2 days before, a `page_view` tagged `summer` 1 day before, and a `checkout` tagged `winter` also 1 day before but inserted last moves order 31 to `winter`, giving `(direct)` 2,894 and `winter` 283, because the higher `event_id` breaks the timestamp tie.
- **Intermediate relation check:** Before grouping, count the rows that leave the `LATERAL` join: it should be exactly 4,362, one per order, because `LIMIT 1` returns at most one touch and `ON true` keeps orders with none.
- **Clause check:** The subquery is correlated on `o.customer_id` and `o.order_date`, filters to the three touch types in a half-open seven-day window, orders by `event_time DESC, event_id DESC` and keeps one row. `COALESCE` turns a missing campaign into `(direct)` in both `SELECT` and `GROUP BY`.
- **Alternative/trade-off:** `ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY event_time DESC, event_id DESC)` over a join of orders to touches gives the same choice, but the join briefly holds every touch per order. `LATERAL ... LIMIT 1` states "at most one" in the query's shape.
- **Edge case:** Every `purchase` and `support` event in the fixture also carries a campaign, 4,000 of each, so dropping the `event_type IN (...)` list would credit campaigns with events that are not marketing touches. Rerun with the list removed and compare the `(direct)` count to see the effect.

## Exercise 5: Compare index column order

`(customer_id, order_date)` supports one customer's history; `(order_date,
customer_id)` better anchors a global date-bound scan. EXPLAIN evidence is
environment-specific and both indexes add write cost.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 5, run the 180-day `SUM(total_amount)` per `customer_id` over `orders` with only the customer-leading index, then create `idx_orders_date_customer_day59_solution` on `(order_date, customer_id) INCLUDE (total_amount)` and capture `EXPLAIN (ANALYZE, BUFFERS)` for the same query; check that `pg_class.relallvisible` equals `relpages` (65) for `orders` first, and run `VACUUM orders` if earlier practice writes lowered it.
- **Expected result/shape:** For sql-59 Exercise 5, expected output: 410 rows, one per `customer_id`, from 1,538 orders in the window, with the same totals under both indexes. The final columns are `customer_id` and `revenue`.
- **Independent verification:** For sql-59 Exercise 5, save the 410 rows before any index change and compare them afterward. With the customer-leading index alone the plan is a `Seq Scan` over 65 pages; with the date-leading index and a fully visible table it becomes an `Index Only Scan` with `Heap Fetches: 0` touching 11 buffers. A 1,500-day window returns 438 rows from a `Seq Scan` over all 4,362 orders, while `WHERE customer_id = 42 ORDER BY order_date` uses the customer-leading index for 7 rows.
- **Intermediate relation check:** Run the aggregate without `EXPLAIN` first: 410 `customer_id` rows for the 180-day window. Keep that output to compare after each index change, since a faster plan must return the same 410 rows and totals.
- **Clause check:** `WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days'` is a range on the second column of the customer-leading index but the first column of the date-leading one. Only a leading column can bound an index range scan, which is why the second `CREATE INDEX` changes the plan.
- **Alternative/trade-off:** The customer-leading index is not wasted. For one customer's history, such as `WHERE customer_id = 42 ORDER BY order_date`, it gave an `Index Only Scan` of 7 rows from 3 pages on our run. Each index is 192 kB here and adds work to every insert, so keep only the one your most frequent query needs.
- **Edge case:** Widen the window to 1,500 days and the planner returns to a `Seq Scan` over all 4,362 rows: once most of the table qualifies, walking the index costs more than reading 65 pages in order. The index-only plan also depends on the visibility map: earlier rolled-back test writes left only 34 of the 65 pages marked all-visible on our container, and the planner stayed on a `Seq Scan` until `VACUUM orders` restored 65 of 65.

## Exercise 6: Publish a metric contract

The answer records metric name, grain, numerator, denominator, UTC window, NULL
policy, exclusions, and owner as queryable values. This prevents silent semantic
changes between teams.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 6, write one inline `VALUES` row for `viewer_to_buyer_rate` with `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`, describing the ordered funnel from the headline query.
- **Expected result/shape:** For sql-59 Exercise 6, expected output: 1 row, `metric_name` `viewer_to_buyer_rate`. The final columns are `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`.
- **Independent verification:** For sql-59 Exercise 6, rebuild the KPI from the text alone: the headline funnel gives 130 ordered buyers over 398 viewers, 0.3266, while the solution's numerator wording, "distinct customers with an order", would count 290 customers and give 0.7286, so the numerator text must name the ordered sequence. To test `null_policy`, move the window start to `CURRENT_TIMESTAMP + interval '1 day'` in the headline query: viewers become 0 and `viewer_to_buyer_rate` is NULL.
- **Intermediate relation check:** The one-row `VALUES` list is the whole input. Read it next to the headline funnel query and confirm that each column, from `grain` to `null_policy`, matches something that query actually does.
- **Clause check:** `SELECT * FROM (VALUES (...)) AS metric_contract (...)` names eight columns. The `null_policy` value describes the `NULLIF(..., 0)` guard in the funnel query, which returns `NULL` rather than an error when no customer viewed.
- **Alternative/trade-off:** A wiki page can hold the same text, but a table row can be joined to a metric's output and checked in CI. The cost is that free text inside SQL still needs a human to keep it true when the query changes.
- **Edge case:** The `numerator` says "distinct customers with an order", but the headline query's 130 buyers are customers whose order came at or after their checkout in the staged sequence, while 290 customers ordered at all in the window. Tighten the wording until a reader could rebuild 0.3266 from the contract alone.

## Exercise 7: Publish defensible basket metrics

Distinct baskets feed support, confidence, and lift. A minimum pair count limits
noise, and product IDs resolve ordering ties deterministically.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 7, read `order_items` through four CTEs: `baskets` (distinct `order_id`, `product_id`), `totals` (4,362 baskets), `product_baskets` (basket count per product), and `pairs` (a self-join on `order_id` with `a.product_id < b.product_id`); build `together`, `support`, `confidence_a_to_b`, and `lift` from them.
- **Expected result/shape:** For sql-59 Exercise 7, expected output: 20 rows, one per (`product_a`, `product_b`) pair. The final columns are `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift`. The final order is `lift DESC, together DESC, product_a, product_b`, and the first four rows tie at lift 63.2174 with together 30: 14/45, 14/258, 31/62, and 31/275.
- **Independent verification:** For sql-59 Exercise 7, confirm `pairs` has 770 rows with the rarest at 15 baskets, so `together >= 2` removes nothing here, and hand-check the top row: 30 × 4,362 / (45 × 46) = 63.2174, where product 14 is in 45 baskets and product 45 in 46. In a rolled-back transaction insert `(order_id, product_id, quantity, unit_price)` = `(238, 14, 1, 10.00)` into `order_items` (order 238 already holds product 14): `order_items` grows to 13,086 rows but `baskets` stays at 13,085 and pair 14/45 stays at 30, while a self-join on raw `order_items` would report 31.
- **Intermediate relation check:** Run `baskets`: 13,085 rows, the same as `order_items`, so no basket repeats a product. `totals` holds one value, 4,362. `pairs` holds 770 rows, and `product_baskets` gives the per-product counts behind confidence and lift.
- **Clause check:** The self-join on `order_id` with `a.product_id < b.product_id` produces each unordered pair once. `CROSS JOIN totals` attaches the basket count to every pair, the two `JOIN product_baskets` add each side's count and `WHERE p.together >= 2` drops rare pairs before the final ranking.
- **Alternative/trade-off:** Ranking by `together`, as the learner query does, rewards popular products; on our run 255 pairs tied at 32. Lift divides by both products' frequencies, so it separates pairs that co-occur more than chance predicts, and the minimum count keeps a single shared basket from earning a huge lift.
- **Edge case:** On this fixture the `together >= 2` filter is inactive, since the rarest pair already appears in 15 baskets. Raise it to 31 and 313 of the 770 pairs survive, and the current top row, products 14 and 45 at 30 baskets, drops out, which shows how strongly that threshold shapes what a stakeholder sees.

## Exercise 8: Assemble cross-domain controls

Named counts and money totals provide a small sign-off surface for customer,
order, line, and payment domains. Any non-equivalence must be explained by a
declared metric definition rather than hidden.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 8, build a control-total result with `UNION ALL`: one labeled row each for the customer count, the order count, the stored order revenue, the line revenue, and the payment total, with every value cast to `numeric`.
- **Expected result/shape:** For sql-59 Exercise 8, expected output: 5 rows, one per `control_name`: `customers` 500, `line_revenue` 2355647.12, `orders` 4362, `payments` 1831900.81, and `stored_order_revenue` 2355646.89. The final columns are `control_name` and `observed_value`. The final order is `control_name`.
- **Independent verification:** For sql-59 Exercise 8, confirm that each `observed_value` equals its standalone query, for example `SELECT ROUND(SUM(amount), 2) FROM payments` for `payments`; `stored_order_revenue` is 0.23 lower than `line_revenue` because each order stores its own line total rounded to cents, so record that gap as a known difference rather than a defect.
- **Intermediate relation check:** For sql-59 Exercise 8, run each control query alone first and cast it to `numeric`, so every `UNION ALL` branch returns the same column types.
- **Clause check:** Five `SELECT`s, each a single aggregate, are stacked with `UNION ALL`, and the final `ORDER BY control_name` sorts the combined rows. Only the first branch casts `COUNT(*)` to `numeric`; `UNION` type resolution then fits the other counts and the money sums into that one `observed_value` column.
- **Alternative/trade-off:** One row with five columns would read more compactly, but the labeled-row shape lets a sign-off script add a sixth control without changing a schema, and it compares cleanly against a stored list of expected values.
- **Edge case:** A control total proves completeness only for what it measures: equal order counts do not prove equal revenue, which is why the result carries both counts and amounts.
