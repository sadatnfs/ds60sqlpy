# Day 11: CASE Expressions and Conditional Logic (Companion Guide)

## How to run this lesson

Launch `./classroom` from the repository root, pick PostgreSQL and **sql-11**, and choose **Whole SQL lesson (psql)**. The lesson file opens a transaction on `advanced_sql_training`, points `search_path` at `training`, runs two queries and rolls back. The first labels the 50 largest orders with a size from `XL` down to `S`; the second counts units sold per product category in the last 30 and 90 days.

Your editable copy is
`.learning/sql/sql-11/lesson/workspace/sql/postgres-60day/day11_case_expressions.sql`.
A quick experiment worth doing there: swap the first two `WHEN` lines of Example 1 so `>= 300` comes before `>= 1000`, rerun, and watch every `XL` turn into `L`.

If the classroom does not start, see the study guide on [how to open a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom). The [notebook setup intended for contributors](../../STUDY-GUIDE.md#optional-contributor-notebook-route) is not needed for this lesson.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 10; data modification with subqueries](day10_dml_with_subqueries.md)
- **Artifacts:** [learner SQL](../day11_case_expressions.sql) ·
  [solution reasoning](../solutions/day11_solutions.md) ·
  [executable solution](../solutions/day11_solutions.sql)

## A beginner's mental model for this lesson

`CASE` is an expression, not a statement: it produces one value per row, so it can sit in the `SELECT` list, inside `SUM(...)`, in `ORDER BY` or in `WHERE`. It never changes how many rows a query returns. Example 1 still prints 50 rows and the Exercise 1 answer still prints all 4,362 orders, each with one extra label column.

A **searched CASE** lists conditions, `CASE WHEN o.total_amount >= 1000 THEN 'XL' WHEN ...`, and PostgreSQL tests them top to bottom. **First match wins**: as soon as one condition is true, the rest are skipped, which is why the highest threshold must come first. A **simple CASE**, `CASE p.method WHEN 'card' THEN 'Card' ...`, compares one expression with a list of values using `=`. Because `NULL = NULL` is not true, a simple `CASE` can never match a `NULL`; test `IS NULL` in a searched branch instead.

If no branch matches and there is no `ELSE`, the result is `NULL`. Writing `CASE WHEN o.total_amount >= 500 THEN 'large' END` over `orders` leaves 1,952 orders with no label at all. Every branch must also produce the same type: mixing `'missing'` with the integer `0` makes PostgreSQL try to read `'missing'` as an integer and fail.

## Two worked SQL examples

### Example 1

```sql
SELECT
  o.order_id,
  o.total_amount,
  CASE WHEN o.total_amount >= 1000 THEN
    'XL'
  WHEN o.total_amount >= 300 THEN
    'L'
  WHEN o.total_amount >= 100 THEN
    'M'
  ELSE
    'S'
  END AS order_size
FROM
  orders o
ORDER BY
  o.total_amount DESC,
  o.order_id
LIMIT 50;
```

**How to read it:** The searched `CASE` checks 1,000, then 300, then 100, and anything below falls to `ELSE 'S'`. Because the order is descending, an order of 1,312.39 matches the first branch and never reaches the others. `ORDER BY o.total_amount DESC, o.order_id` with `LIMIT 50` keeps the 50 largest orders.

**Expected result/shape:** 50 rows, all labeled `XL`: the largest total is 1,432.49 and the 50th is 1,312.39, both above 1,000. Sixteen orders share the top amount of 1,432.49 (order 104 first), so the `o.order_id` tie-breaker decides which of them print first. Across all 4,362 orders the same rule gives 334 `XL`, 2,807 `L`, 872 `M` and 349 `S`; remove the `LIMIT` and group by the label to see that.

### Example 2

```sql
SELECT
  p.category,
  SUM(
    CASE WHEN o.order_date >= now() - interval '30 days' THEN
      oi.quantity
    ELSE
      0
    END) AS qty_30d,
  SUM(
    CASE WHEN o.order_date >= now() - interval '90 days' THEN
      oi.quantity
    ELSE
      0
    END) AS qty_90d
FROM
  order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
GROUP BY
  p.category
ORDER BY
  qty_30d DESC,
  p.category;
```

**How to read it:** Each joined row is one order line with its order date and product category. The first `CASE` returns the line's quantity when the order is less than 30 days old and 0 otherwise, so `SUM` adds only recent units; the second does the same for 90 days. Both totals come from one pass over the 13,085 lines, grouped into six categories.

**Expected result/shape:** Six rows, one per category. In our check Sports led with 347 units in 30 days and 1,251 in 90, and Beauty was last with 290 and 1,217. Every 90-day figure is at least the 30-day figure, because a 30-day-old line also passes the 90-day test. `now()` moves, so your numbers will differ from ours; the `ELSE 0` keeps a quiet category at 0 instead of `NULL`.

## Learning objectives

- Classify rows with ordered, mutually understandable `CASE` branches.
- Use conditional aggregation without losing unmatched categories.

## Vocabulary and concepts

- **Searched CASE:** evaluates Boolean conditions in order.
- **Simple CASE:** compares one expression with several values.
- **Short-circuit ordering:** the first matching branch supplies the result.

## Worked example / walkthrough

Test any tiered `CASE` on values just below, exactly at, and just above each threshold before trusting it on real rows. For the Exercise 1 rule, `VALUES (99.99), (100), (499.99), (500)` should give `small`, `medium`, `medium` and `large`. No order in the fixture costs exactly 100 or 500, so the table alone would never reveal whether you wrote `>` where `>=` was meant; the four test values do.

## Practice assumptions and review method

- **Focus:** Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.
- **Assumptions:** Searched `CASE` uses first-match wins. Status/category labels are illustrative course rules, not universal business definitions.
- **Failure to watch for:** Overlapping broad conditions placed first make later branches unreachable; an omitted `ELSE` produces NULL.
- **Review loop:** after each labeling query, count rows per label and check that the counts add up to the unlabeled row count, then confirm no label is `NULL` unless the rule says it should be.

## Exercises

Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.

For each prompt, list the labels the `CASE` can produce and the order its branches must be tested in before writing any SQL. Then guess how many rows each label will get, and decide what a `NULL` input should become.

1. **Query writing:** Classify orders as small, medium, or large by total amount.
   **Wager:** which label will be the most common across 4,362 orders?
   **Progressive hint:** Validate boundaries and place the highest threshold first.
   **Inputs/evidence:** For sql-11 Exercise 1, read from `orders` and label every order with a searched `CASE`: `large` when `total_amount >= 500`, `medium` when it is at least 100, otherwise `small`; no `GROUP BY` is needed.
   **Expected result/shape:** For sql-11 Exercise 1, return 4,362 rows, one per order, each with exactly one label; order 1 (240.20) is `medium`, order 3 (601.73) is `large`, and order 5 (105.84) is `medium`. The final columns are `order_id`, `total_amount`, and `order_size`. The final order is `o.order_id`.
   **Verify:** For sql-11 Exercise 1, confirm 4362 rows, one per `order_id`, and that counting the labels gives 2410 `large`, 1603 `medium`, and 349 `small`; then evaluate the same `CASE` on `VALUES (99.99), (100), (499.99), (500)` and expect `small`, `medium`, `medium`, and `large`.
2. **Query writing:** Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation.
   **Wager:** do the first three counts add up to the fourth?
   **Progressive hint:** Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator.
   **Inputs/evidence:** For sql-11 Exercise 2, count the 4,362 `orders` rows four ways in one pass with `COUNT(*) FILTER (WHERE ...)`: `paid`, `shipped`, or `delivered` as `paid_like`, `placed` as `open_orders`, `returned` as `returned_orders`, and all rows as `all_orders`.
   **Expected result/shape:** For sql-11 Exercise 2, return one row: `paid_like` 2617, `open_orders` 873, `returned_orders` 872, and `all_orders` 4362. The final columns are `paid_like`, `open_orders`, `returned_orders`, and `all_orders`.
   **Verify:** For sql-11 Exercise 2, confirm `GROUP BY status` returns shipped 873, paid 872, and delivered 872 (adding up to 2617), placed 873, and returned 872, and that the three filtered counts add up to `all_orders`. Inside a rolled-back transaction, set order 1 from `paid` to `cancelled`; `paid_like` must drop to 2616 while `all_orders` stays 4362.
3. **Query writing:** Label missing customer segments separately from known segment values.
   **Wager:** how many of the four seeded segments count as premium?
   **Progressive hint:** Test `IS NULL` before comparing text values.
   **Inputs/evidence:** For sql-11 Exercise 3, read from `customers` and label each `segment` as `missing` when it is NULL, `premium` for `gold` or `platinum`, and `core` otherwise; return one row per customer.
   **Expected result/shape:** For sql-11 Exercise 3, return 500 rows, one per customer: customer 1 (`standard`) and customer 2 (`silver`) map to `core`, customer 3 (`gold`) and customer 4 (`platinum`) map to `premium`. The final columns are `customer_id`, `segment`, and `segment_group`. The final order is `c.customer_id`.
   **Verify:** For sql-11 Exercise 3, confirm 500 rows, one per `customer_id`; the seed gives 250 `premium` and 250 `core` rows and no `missing` row because every seeded customer has a segment. In a transaction you roll back, set one `segment` to NULL and confirm that customer becomes `missing`, not `core`.
4. **Prediction:** Predict the label for 500 when `>= 100` appears before `>= 500`, then repair the branch order.
   **Wager:** with the branches in the wrong order, how many of 50, 100 and 500 get the right label?
   **Progressive hint:** First-match wins, so specific/high thresholds must precede broader/lower ones.
   **Inputs/evidence:** For sql-11 Exercise 4, label the three amounts in the inline `VALUES (50), (100), (500)` fixture with a searched `CASE` that tests `amount >= 500` before `amount >= 100`, so the first matching branch is the most specific.
   **Expected result/shape:** For sql-11 Exercise 4, return 3 rows: 50 is `low`, 100 is `medium`, and 500 is `high`. The final columns are `amount`, and `corrected_label`. The final order is `amount`.
   **Verify:** For sql-11 Exercise 4, confirm the 3 labels above, then swap the two `WHEN` branches so `amount >= 100` is tested first; 500 must come back as `medium`, which is the bug being corrected. Add `499.99` and `99.99` to the fixture; the corrected `CASE` must return `medium` and `low`.
5. **Debugging:** Replace a CASE expression that returns mixed numeric and text types with one consistent output type.
   **Wager:** run the broken version and guess whether the error names `'missing'` or the number.
   **Progressive hint:** All result branches must resolve to a compatible PostgreSQL type.
   **Inputs/evidence:** For sql-11 Exercise 5, classify the three values in the inline `VALUES (NULL::integer), (0), (2)` fixture with a `CASE` whose first branch is `value IS NULL`.
   **Expected result/shape:** For sql-11 Exercise 5, return 3 rows: `NULL` is `missing`, 0 is `zero`, and 2 is `nonzero`, with the `NULL` row first. The final columns are `value`, and `value_state`. The final order is `value NULLS FIRST`.
   **Verify:** For sql-11 Exercise 5, confirm 3 rows with three different `value_state` labels. Remove the `IS NULL` branch and the `NULL` row must fall through to `ELSE` as `nonzero`, because `NULL = 0` is unknown rather than true; drop `NULLS FIRST` and the `NULL` row must sort last.
6. **Extension:** Create payment-method display labels and preserve unknown future methods with an explicit fallback.
   **Wager:** which method has the most payments?
   **Progressive hint:** A simple CASE fits equality mapping; `ELSE` prevents silent NULL labels.
   **Inputs/evidence:** For sql-11 Exercise 6, read from `payments`, group by `method`, count payments per method, and map each method to a display label with a simple `CASE p.method WHEN ... END` that keeps an `ELSE 'Other'` fallback.
   **Expected result/shape:** For sql-11 Exercise 6, return 4 rows, one per payment method: `bank` as `Bank transfer` (886), `card` as `Card` (860), `credit` as `Store credit` (1050), and `paypal` as `PayPal` (1040). The final columns are `method`, `method_label`, and `payment_count`. The final order is `p.method`.
   **Verify:** For sql-11 Exercise 6, confirm 4 rows (`bank` 886, `card` 860, `credit` 1050, `paypal` 1040) whose counts add up to `SELECT COUNT(*) FROM payments` (3836); then evaluate the same `CASE` on `VALUES ('crypto')` and confirm it returns `Other`, not NULL.

## Common mistakes and how to recover

- **A broad branch first:** `CASE WHEN amount >= 100 THEN 'medium' WHEN amount >= 500 THEN 'high' ...` labels 500 as `medium`; the second branch can never fire. Put the highest threshold first, or write closed ranges such as `amount >= 100 AND amount < 500`.
- **Forgetting `ELSE`:** unmatched rows get `NULL`. Over `orders`, a `CASE` with only the `>= 500` branch leaves 1,952 rows unlabeled. Add an explicit `ELSE`, even one like `'Other'`, so new values stay visible.
- **Mixed branch types:** `THEN 'missing' ... THEN 0` fails with `invalid input syntax for type integer: "missing"`; casting the text gives `CASE types integer and text cannot be matched`. Make every branch text, as Exercise 5 does.
- **`NULL` in a simple CASE:** `CASE segment WHEN NULL THEN ...` never matches, because it compares with `=`. Use a searched branch, `WHEN segment IS NULL`.
- **Expecting `CASE` to guard constants:** `CASE WHEN total_amount > 0 THEN 1 ELSE 1/0 END` raises `division by zero` even though no order reaches the `ELSE`, because PostgreSQL folds the constant `1/0` before reading rows. Guarding a column division such as `CASE WHEN v = 0 THEN NULL ELSE 10 / v END` does work.

When the file stops on an error, fix that first error and rerun the whole file; the study guide's [advice for runs that stop early](../../STUDY-GUIDE.md#recover-from-common-failures) has the details.

## Self-check

- Are branch boundaries exhaustive and non-overlapping?
- Do all branches, including `ELSE`, resolve to compatible data types?

## Next step

Continue to [Day 12; string functions](day12_string_functions.md).

## Deep dive and reference

Learning objectives
- Write simple and searched CASE expressions in SELECT and ORDER BY
- Use CASE within aggregates for conditional sums/counts
- Understand evaluation order and NULL handling in CASE

Core concepts and deep dive
- Simple CASE: CASE expr WHEN val1 THEN ... WHEN val2 THEN ... ELSE ... END
- Searched CASE: CASE WHEN cond1 THEN ... WHEN cond2 THEN ... ELSE ... END; more flexible; prefer for predicates.
- CASE is an expression; can be nested and used anywhere expressions are allowed.
- Use CASE to implement bucketing, flags, and conditional aggregation without extra joins.

Examples
- Segment labels: CASE WHEN ltv>=1000 THEN 'gold' WHEN ltv>=300 THEN 'silver' ELSE 'bronze' END.
- Conditional aggregate: `SUM(CASE WHEN status='returned' THEN total_amount
  ELSE 0 END)` over `orders`.

Pitfalls
- Overlapping conditions in searched CASE; first match wins. Order matters.
- Returning mixed types; ensure consistent result types across branches.

Further reading
- CASE: https://www.postgresql.org/docs/17/functions-conditional.html

## Ask an AI tutor about this lesson

You can finish this lesson without a tutor. If you use one, ask it to predict the Exercise 4 labels with the branches in the wrong order, then check its answer against `psql`. The study guide's [guidance on AI tutoring](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) explains how to ask for hints instead of complete queries.

```text
Tutor me through sql-11: CASE Expressions and Conditional Logic.

I have completed the direct catalog prerequisite: `sql-10`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day11_case_expressions.md
- Answer-free learner SQL: sql/postgres-60day/day11_case_expressions.sql

Key terms to teach in context: Searched CASE, Simple CASE, Short-circuit ordering. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Take a three-tier amount classification and test values just below, exactly at, and just above each boundary. Because `CASE` stops at the first match, place the most specific or highest-threshold conditions before broader ones.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-11/ working copy. Never point setup, reset, DDL, or DML
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
