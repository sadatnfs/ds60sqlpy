# Day 59: Final Capstone, Part 2: Stakeholder Analytics

## How to run this lesson

In `./classroom`, pick PostgreSQL, open **sql-59** and choose
**Whole SQL lesson (psql)**; the snippet runner would skip the `BEGIN`, the
three `CREATE INDEX IF NOT EXISTS` statements and the closing `ROLLBACK` that
keep this capstone harmless. Your saved copy lives at
`.learning/sql/sql-59/lesson/workspace/sql/postgres-60day/day59_final_capstone_part2.sql`
inside the Docker learning volume. One run against `advanced_sql_training`
prints six results in this order: the LTV table capped at 100 rows, the
one-row funnel, 20 product pairs, the `EXPLAIN ANALYZE` plan for the top-50
customer revenue query, the Finance budget table and the Marketing campaign
table. `psql` stops at the first error, so a missing table shows up before
any KPI looks plausible. The
[study guide's launcher steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom)
cover setup and reset, and contributors who prefer JupyterLab can follow the
[notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 58; capstone ingestion and data quality](day58_final_capstone_part1.md) Day 58 loaded and validated the capstone inputs; today every KPI is built on those same `orders`, `order_items`, `events` and `budgets` rows, so a count you reconciled yesterday should still reconcile here.
- **Artifacts:** [learner SQL](../day59_final_capstone_part2.sql) ·
  [solution reasoning](../solutions/day59_solutions.md) ·
  [executable solution](../solutions/day59_solutions.sql)

## A beginner's mental model for this lesson

Day 59 asks one question four times, once each for leadership, Finance,
Marketing and the platform team: what does one row of this table mean, and
which total proves it is complete? The fixture answers with fixed anchors:
500 customers, 438 of whom have ever ordered, 4,362 orders, 13,085 order
lines and 20,000 events split evenly across five event types.

A **KPI contract** is the written promise behind a number: its name, formula,
grain, population, window, exclusions and owner. The LTV query in Example 1
shows why it matters. It starts from customers who have orders and joins them
to their signup cohort, so on our run it produced 191 cohort/segment groups.
The solution starts from all 500 customers instead and returns 192 groups,
and in the October 2026 platinum cell the learner shows 1 customer averaging
2,760.47 while the solution shows 2 customers averaging 1,380.24. Neither is
wrong until a contract says whether a customer with no orders belongs in the
average.

A **funnel denominator** is the population each conversion rate divides by.
In the ordered 90-day funnel on our run, 398 customers viewed, 340 then added
to cart, 275 then checked out and 130 then ordered, so each step shrinks.
Counting each event type on its own gives 398 page viewers but 399 cart
adders, which is why independent reach is not a funnel.

A **scale hypothesis** is a claim such as "monthly partitions on `orders`
will speed this up at 100 million rows" that the 4,362-row fixture cannot
prove. Write it down, name the plan you would expect and say what evidence
would settle it. When a result surprises you, walk the query in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order)
and count rows after each CTE.

## Two worked SQL examples

Both excerpts are the first two KPIs in `day59_final_capstone_part2.sql`:
lifetime value by signup cohort and segment, then the ordered 90-day funnel.
They run inside the script's transaction with no setup of their own.

### Example 1

```sql
WITH order_values AS (
  SELECT
    o.customer_id,
    o.order_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value,
    o.order_date
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.customer_id,
    o.order_id,
    o.order_date
),
ltv AS (
  SELECT
    customer_id,
    date_trunc('month', MIN(order_date))::date AS first_order_month,
    SUM(order_value) AS ltv
  FROM
    order_values
  GROUP BY
    customer_id
),
cohort AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at)::date AS cohort_month,
    COALESCE(c.segment, 'standard') AS segment
  FROM
    customers c
)
SELECT
  cohort.segment,
  cohort.cohort_month,
  ROUND(AVG(ltv.ltv), 2) AS avg_ltv,
  COUNT(*) AS customers
FROM
  ltv
  JOIN cohort ON cohort.customer_id = ltv.customer_id
GROUP BY
  cohort.segment,
  cohort.cohort_month
ORDER BY
  cohort.cohort_month DESC,
  avg_ltv DESC
LIMIT 100;
```

**How to read it:** Three CTEs change the grain twice. `order_values` joins `orders` to
`order_items` and sums discounted line values into one row per order.
`ltv` collapses those to one row per customer and keeps the month of the
first order, which the final query never displays. `cohort` reads every
customer's signup month and segment. The final `JOIN` from `ltv` to `cohort`
keeps only customers who have ordered, and the outer `GROUP BY` averages
their LTV per (`segment`, `cohort_month`) before `LIMIT 100` keeps the newest
cohorts.

**Expected result/shape:** One row per (`segment`, `cohort_month`) with `avg_ltv` and `customers`,
capped at 100 of the 191 groups on our run. The first row is gold in the
October 2026 cohort: 2 customers averaging 8,296.32. Ties on `avg_ltv` within
a month have no tie-breaker, so add `segment` to the `ORDER BY` before you
compare two runs row by row.

### Example 2

```sql
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
    viewed.customer_id,
    viewed.viewed_at,
    MIN(event.event_time) AS added_at
  FROM
    viewed_stage viewed
    LEFT JOIN events event ON event.customer_id = viewed.customer_id
      AND event.event_type = 'add_to_cart'
      AND event.event_time >= viewed.viewed_at
  GROUP BY
    viewed.customer_id,
    viewed.viewed_at
),
checkout_stage AS (
  SELECT
    added.customer_id,
    added.viewed_at,
    added.added_at,
    MIN(event.event_time) AS checkout_at
  FROM
    added_stage added
    LEFT JOIN events event ON event.customer_id = added.customer_id
      AND event.event_type = 'checkout'
      AND event.event_time >= added.added_at
  GROUP BY
    added.customer_id,
    added.viewed_at,
    added.added_at
),
purchase_stage AS (
  SELECT
    checkout.customer_id,
    checkout.viewed_at,
    checkout.added_at,
    checkout.checkout_at,
    MIN(customer_order.order_date) AS purchased_at
  FROM
    checkout_stage checkout
    LEFT JOIN orders customer_order ON customer_order.customer_id = checkout.customer_id
      AND customer_order.order_date >= checkout.checkout_at
      AND customer_order.order_date >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY
    checkout.customer_id,
    checkout.viewed_at,
    checkout.added_at,
    checkout.checkout_at
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
  COUNT(*) FILTER (WHERE bought) AS buyers
FROM
  activity;
```

**How to read it:** `viewed_stage` retains one row per customer and records the
earliest recent page view. Each later `LEFT JOIN` searches only at or after its
prior timestamp. A customer who checks out before adding to cart therefore does
not enter the ordered checkout population. `activity` turns the four timestamps
into nested Boolean populations, and aggregate `FILTER` returns one summary row.
This is different from independently asking whether each event happened at any
time; independent reach can increase between stages and is not a funnel.

**Expected result/shape:** Exactly one row with `viewers`, `adders`, `checkouts`,
and `buyers`. The invariant is `buyers <= checkouts <= adders <= viewers`.
Inspect one customer's four timestamps before trusting the aggregate, and add a
counterexample whose checkout precedes add-to-cart; that checkout must not count.

## Learning objectives

- Deliver stakeholder-specific metrics with an explicit row grain, denominator,
  scope, and reconciliation.
- Pair performance recommendations with representative evidence and operational
  ownership.

## Vocabulary and concepts

- **KPI contract:** metric name, formula, grain, population, window, exclusions,
  and owner.
- **Funnel denominator:** the eligible population used at each conversion step.
- **Scale hypothesis:** a design expected to help at larger volume but still
  requiring representative validation.

## Worked example / walkthrough

Choose one KPI and write its contract before SQL. Build its lowest stable grain,
add dimensions only after reconciliation, and return numerator/denominator
beside any rate. Present the stakeholder table together with its control total
and a limitation; repeat that evidence pattern for Finance and Marketing.

## Exercises

Complete these in the [learner SQL](../day59_final_capstone_part2.sql):

1. State every LTV CTE's grain and its grain transition.
   **Inputs/evidence:** For sql-59 Exercise 1, read the learner LTV query in section 1a (`order_values`, then `ltv`, then `cohort`, then the grouped `SELECT`) and record each aggregation step in an inline `VALUES` fixture with `step_name`, `row_grain`, and `key_columns`.
   **Expected result/shape:** For sql-59 Exercise 1, expected output: 3 rows, one per `step_name`: `order_values` at one row per order keyed by `customer_id + order_id`, `customer_ltv` at one row per customer keyed by `customer_id`, and `cohort_segment_summary` at one row per cohort/segment keyed by `cohort_month + segment`. The final columns are `step_name`, `row_grain`, and `key_columns`.
   **Verify:** For sql-59 Exercise 1, prove each grain claim by running the learner CTEs: `order_values` has 4,362 rows and 4,362 distinct `order_id` values but only 438 distinct `customer_id` values, `ltv` has 438 rows (the order-to-customer step, since 62 of the 500 customers never ordered), `cohort` has 500, and the summary has 191 (`segment`, `cohort_month`) groups whose `customers` add back to 438 before `LIMIT 100` trims the output.
   **Data check:** The solution's grain map returns 3 rows: `order_values` at one row per order, `customer_ltv` at one row per customer and `cohort_segment_summary` at one row per cohort and segment. The learner's middle CTE is named `ltv`, so map your names to those three steps rather than copying the labels.
2. Add funnel conversion rates and retain buyers without events.
   **Inputs/evidence:** For sql-59 Exercise 2, derive `viewed_at`, `added_at`, `checkout_at`, and `purchased_at` per customer over the same trailing-90-day window.
   **Expected result/shape:** For sql-59 Exercise 2, expected output: exactly one summary row with ordered stage counts, `buyers_without_view`, and three conversion rates whose denominators are the preceding ordered populations.
   **Verify:** For sql-59 Exercise 2, confirm one row with 398 viewers, 340 adders, 275 checkouts, 130 buyers, `buyers_without_view` 29, and rates 0.8543, 0.8088, and 0.4727; the unordered reach counts for the same window (398 customers with a `page_view`, 399 with `add_to_cart`, 397 with `checkout`, 290 with an order) show why reach is not a funnel. In a rolled-back transaction give customer 45, who has no recent `page_view`, an `add_to_cart` 2 days ago and a `checkout` 1 day ago: every count stays the same. Add a `page_view` 3 days ago and the row becomes 399, 341, 276, and 130 with `buyers_without_view` 28, because the September order precedes the new checkout.
   **Data check:** On our run the ordered counts were 398 viewers, 340 adders, 275 checkouts and 130 buyers, giving rates of 0.8543, 0.8088 and 0.4727, with 29 buyers who ordered in the window but never viewed a page. The 29 stay outside the funnel numerators.
3. Reconcile order totals, line revenue, and payments before KPI selection.
   **Inputs/evidence:** For sql-59 Exercise 3, start from `orders` and `LEFT JOIN` two order-grain CTEs: `lines`, which sums `quantity * unit_price * (1 - discount)` from `order_items`, and `paid`, which sums `amount` from `payments`; derive `header_minus_lines` and `paid_minus_header` from the three amounts.
   **Expected result/shape:** For sql-59 Exercise 3, expected output: exactly 50 rows, `order_id` 1 through 50 in order, one per order. The final columns are `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`; orders 5, 9, 14, 20, 25, 27, 32, 40, 45, and 49 show NULL `paid_amount` and `paid_minus_header`.
   **Verify:** For sql-59 Exercise 3, confirm `lines` has 4,362 rows and `paid` has 3,489 rows built from 3,836 payment rows (347 orders have more than one payment), and that the absolute `header_minus_lines` never exceeds 0.0045 across all 4,362 orders. The ten NULL-payment orders are all `placed`. In a rolled-back transaction insert a second 10.00 payment for order 1 (header 240.20): the output stays at 50 rows, `paid` still has 3,489 rows, and order 1 shows `paid_amount` 250.20 and `paid_minus_header` 10.00.
   **Data check:** Every order's stored total differs from its line sum by less than half a cent (2,855 of 4,362 differ at all, by at most 0.0045), while 873 orders, all `placed`, have no payment and 199 paid orders differ from their header. In the first 50 rows, 10 show an empty `paid_amount`.
4. Add direct attribution and reconcile purchases.
   **Inputs/evidence:** For sql-59 Exercise 4, start from `orders` and choose at most one event whose `event_type` is in the declared marketing-touch whitelist (`page_view`, `add_to_cart`, `checkout`), whose campaign metadata is present, and whose timestamp is in the preceding seven-day half-open window.
   **Expected result/shape:** For sql-59 Exercise 4, expected output: 6 rows, one per `attribution_bucket`: `(direct)` 2,895, `none` 310, `fall` 305, `spring` 288, `summer` 282, and `winter` 282, summing to 4,362 orders; `none` is a literal campaign value, not a missing one. The final order is `purchases DESC, attribution_bucket`.
   **Verify:** For sql-59 Exercise 4, assert that `SUM(purchases)` equals the 4,362 rows of `orders`. Then in a rolled-back transaction use order 31 (customer 5, currently `(direct)`): a `support` event tagged `spring` 1 day before the order changes nothing; adding a `page_view` tagged `fall` 2 days before, a `page_view` tagged `summer` 1 day before, and a `checkout` tagged `winter` also 1 day before but inserted last moves order 31 to `winter`, giving `(direct)` 2,894 and `winter` 283, because the higher `event_id` breaks the timestamp tie.
   **Data check:** The six buckets on our run were `(direct)` 2,895, `none` 310, `fall` 305, `spring` 288, `summer` 282 and `winter` 282, which add to 4,362. `none` is a literal campaign string in `metadata`, not a missing value, so it earns its own row next to `(direct)`.
5. Compare customer/date and date/customer index orders.
   **Inputs/evidence:** For sql-59 Exercise 5, run the 180-day `SUM(total_amount)` per `customer_id` over `orders` with only the customer-leading index, then create `idx_orders_date_customer_day59_solution` on `(order_date, customer_id) INCLUDE (total_amount)` and capture `EXPLAIN (ANALYZE, BUFFERS)` for the same query; check that `pg_class.relallvisible` equals `relpages` (65) for `orders` first, and run `VACUUM orders` if earlier practice writes lowered it.
   **Expected result/shape:** For sql-59 Exercise 5, expected output: 410 rows, one per `customer_id`, from 1,538 orders in the window, with the same totals under both indexes. The final columns are `customer_id` and `revenue`.
   **Verify:** For sql-59 Exercise 5, save the 410 rows before any index change and compare them afterward. With the customer-leading index alone the plan is a `Seq Scan` over 65 pages; with the date-leading index and a fully visible table it becomes an `Index Only Scan` with `Heap Fetches: 0` touching 11 buffers. A 1,500-day window returns 438 rows from a `Seq Scan` over all 4,362 orders, while `WHERE customer_id = 42 ORDER BY order_date` uses the customer-leading index for 7 rows.
   **Data check:** The aggregate returns 410 customers for the 180-day window with either index. On our run the customer-leading index left the plan on a `Seq Scan` over all 65 pages, while the date-leading index produced an `Index Only Scan` reading 11 pages. A 1,500-day window returned all 438 buyers and went back to a `Seq Scan` even with both indexes present. If the plan stays on a `Seq Scan` with the date-leading index, compare `relallvisible` with `relpages` in `pg_class`: after earlier rolled-back writes we saw 34 of 65, and `VACUUM orders` brought back the `Index Only Scan`.
6. Write a complete metric contract for one KPI.
   **Inputs/evidence:** For sql-59 Exercise 6, write one inline `VALUES` row for `viewer_to_buyer_rate` with `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`, describing the ordered funnel from the headline query.
   **Expected result/shape:** For sql-59 Exercise 6, expected output: 1 row, `metric_name` `viewer_to_buyer_rate`. The final columns are `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`.
   **Verify:** For sql-59 Exercise 6, rebuild the KPI from the text alone: the headline funnel gives 130 ordered buyers over 398 viewers, 0.3266, while the solution's numerator wording, "distinct customers with an order", would count 290 customers and give 0.7286, so the numerator text must name the ordered sequence. To test `null_policy`, move the window start to `CURRENT_TIMESTAMP + interval '1 day'` in the headline query: viewers become 0 and `viewer_to_buyer_rate` is NULL.
   **Data check:** The solution publishes one row for `viewer_to_buyer_rate`. Compare its `numerator` text with the funnel SQL: the headline query counts the 130 ordered buyers, not the 290 customers with any order in the window, so the written contract must say which one it means.
7. Publish product-pair support, confidence, and lift with a minimum count.
   **Inputs/evidence:** For sql-59 Exercise 7, read `order_items` through four CTEs: `baskets` (distinct `order_id`, `product_id`), `totals` (4,362 baskets), `product_baskets` (basket count per product), and `pairs` (a self-join on `order_id` with `a.product_id < b.product_id`); build `together`, `support`, `confidence_a_to_b`, and `lift` from them.
   **Expected result/shape:** For sql-59 Exercise 7, expected output: 20 rows, one per (`product_a`, `product_b`) pair. The final columns are `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift`. The final order is `lift DESC, together DESC, product_a, product_b`, and the first four rows tie at lift 63.2174 with together 30: 14/45, 14/258, 31/62, and 31/275.
   **Verify:** For sql-59 Exercise 7, confirm `pairs` has 770 rows with the rarest at 15 baskets, so `together >= 2` removes nothing here, and hand-check the top row: 30 × 4,362 / (45 × 46) = 63.2174, where product 14 is in 45 baskets and product 45 in 46. In a rolled-back transaction insert `(order_id, product_id, quantity, unit_price)` = `(238, 14, 1, 10.00)` into `order_items` (order 238 already holds product 14): `order_items` grows to 13,086 rows but `baskets` stays at 13,085 and pair 14/45 stays at 30, while a self-join on raw `order_items` would report 31.
   **Data check:** The 4,362 baskets hold 770 distinct product pairs, and the rarest pair appears in 15 baskets, so `together >= 2` removes nothing on this fixture. The top row on our run was products 14 and 45: together 30, support 0.0069, confidence 0.6667 and lift 63.2174. Product 14 sits in 45 baskets.
8. Assemble named cross-domain control totals for stakeholder sign-off.
   **Inputs/evidence:** For sql-59 Exercise 8, build a control-total result with `UNION ALL`: one labeled row each for the customer count, the order count, the stored order revenue, the line revenue, and the payment total, with every value cast to `numeric`.
   **Expected result/shape:** For sql-59 Exercise 8, expected output: 5 rows, one per `control_name`: `customers` 500, `line_revenue` 2355647.12, `orders` 4362, `payments` 1831900.81, and `stored_order_revenue` 2355646.89. The final columns are `control_name` and `observed_value`. The final order is `control_name`.
   **Verify:** For sql-59 Exercise 8, confirm that each `observed_value` equals its standalone query, for example `SELECT ROUND(SUM(amount), 2) FROM payments` for `payments`; `stored_order_revenue` is 0.23 lower than `line_revenue` because each order stores its own line total rounded to cents, so record that gap as a known difference rather than a defect.
   **Data check:** Expect `customers` 500, `orders` 4,362, `stored_order_revenue` 2,355,646.89, `line_revenue` 2,355,647.12 and `payments` 1,831,900.81. The payment gap of about 523,746 is mostly the 873 unpaid orders, which is a status fact to record, not a rounding issue.

Add a one-page metric dictionary and before/after evidence table.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: Choose one KPI and write its contract before SQL. Build its lowest stable grain, add dimensions only after reconciliation, and return numerator/denominator beside any rate. Present the stakeholder table together with its control total and a limitation; repeat that evidence pattern for Finance and Marketing.
- **Summing non-additive campaign rows:** the learner Marketing table on our
  run lists 47, 43, 42, 29 and 28 assisted customers, which add to 189, yet
  only 149 distinct customers were assisted. One customer touched by two
  campaigns appears in both rows. Report the distinct total separately.
- **Treating `'none'` as missing:** `NULLIF(trim(...), '')` removes blank
  campaign strings but keeps the literal value `none`, which then tops the
  Marketing table with 47 customers. Decide in the contract whether `none`
  means direct traffic.
- **Picking a top 20 from a tie:** in the learner basket query 255 product
  pairs share the maximum `together` of 32, and `ORDER BY together DESC
  LIMIT 20` returns an arbitrary 20 of them. Add `product_a` and `product_b`
  as tie-breakers or rank by lift with a minimum count.
- **Assuming the learner indexes help:** `idx_orders_customer_date` leads
  with `customer_id`, so the date-bounded top-50 query cannot use it for its
  range filter; on our run the plan still read every page of `orders`.
- **Reading the Finance year wrong:** both CTEs filter from
  `date_trunc('year', now())`, so the table changes on 1 January. On our run
  Payroll showed a budget of 8,752,000.00 against 4,564,618.75 actual.
- For anything not listed, the
  [recovery checklist](../../STUDY-GUIDE.md#recover-from-common-failures)
  walks through first-error diagnosis.

## Self-check

- Can another analyst reproduce every KPI from its written contract?
- Are campaign counts, pair counts, and funnel rates prevented from being
  summed across non-additive rows?

## Next step

Continue to [Day 60; end-to-end sign-off](day60_final_capstone_part3.md).

## Deep dive and reference

Day 59 is a capstone checkpoint, not a pair of discrete exercises. It combines
KPI definitions, performance evidence, stakeholder outputs, and scale planning.

## Deliverable 1: KPI suite

- LTV by signup cohort and customer segment, with customer count, average LTV,
  and total LTV.
- A 90-day customer-grain funnel for page view, add to cart, checkout, and
  purchase/order conversion, with explicit denominators.
- The top 20 distinct product pairs from order baskets, ranked by co-occurrence
  count (`together`), not by attributed pair revenue.

## Deliverable 2: Performance evidence

Create candidate indexes only inside the rollback-only experiment, then capture
`EXPLAIN (ANALYZE, BUFFERS)` for the recent customer-revenue query. Save result
reconciliation, timing, buffers, row estimates, and plan choice. The compact
seed may correctly use a sequential scan.

## Deliverable 3: Stakeholder outputs

- Finance: current-year budget, actual expense, and variance by category.
- Marketing: campaign touches within seven days before each customer's first
  order, counted as distinct assisted customers. Only the declared touch types
  (`page_view`, `add_to_cart`, and `checkout`) qualify; a campaign tag on an
  unrelated event must not create marketing credit.

The marketing definition differs from Day 48's all-purchase event attribution.
Multiple campaigns can assist one customer, so campaign rows are not additive.

## Deliverable 4: Large-scale design note

For a hypothetical 100M-row workload, identify candidate time partitions for
orders/events, prove partition-key filters for pruning, describe local/partial
indexes, and assign retention/maintenance ownership. Do not claim a benefit
without a representative plan.

## Sign-off limits

Record metric grain, time window, exclusions, reconciliation, and consumer for
every KPI. All candidate DDL rolls back; production changes require a separate
reviewed migration.

## Ask an AI tutor about this lesson

Use a tutor as a stakeholder who keeps asking "how do you know?" Share your
KPI tables and control totals, then ask it to find one number you could not
defend from a written contract. The checklist in
[the tutor section](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) lists what
to share and what to keep private. Paste the prompt that follows once your
numbers are in hand:

```text
Tutor me through sql-59: Final Capstone, Part 2: Stakeholder Analytics.

I have completed the direct catalog prerequisite: `sql-58`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day59_final_capstone_part2.md
- Answer-free learner SQL: sql/postgres-60day/day59_final_capstone_part2.sql

Key terms to teach in context: KPI contract, Funnel denominator, Scale hypothesis. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Choose one KPI and write its contract before SQL. Build its lowest stable grain, add dimensions only after reconciliation, and return numerator/denominator beside any rate. Present the stakeholder table together with its control total and a limitation; repeat that evidence pattern for Finance and Marketing.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-59/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
