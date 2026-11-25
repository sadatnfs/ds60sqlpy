# Day 05: CROSS and SELF JOINs: Combinatorics and Relationships to Self (Companion Guide)

## How to run this lesson

In `./classroom` choose PostgreSQL, select **sql-05**, then **Whole SQL lesson (psql)**. Inside one `BEGIN`/`ROLLBACK` block against `advanced_sql_training`, `psql` prints two results: a grid pairing every product category with every customer country, and an employee list beside each person's manager. Both are reads. The six prompts below them are comments, so the first run shows only those two results.

Your working copy is
`.learning/sql/sql-05/lesson/workspace/sql/postgres-60day/day05_cross_self_joins.sql`.
Exercise 3 builds its months from `CURRENT_DATE`, so the six months it shows depend on the day you run it; every other answer is fixed by the fixture. If one exercise errors, `ON_ERROR_STOP` ends the run at that statement.

Reset and loading steps live in the [classroom section](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) of the study guide; the [notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route) is optional.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 04; outer joins](day04_outer_joins.md)
- **Artifacts:** [learner SQL](../day05_cross_self_joins.sql) ·
  [solution reasoning](../solutions/day05_solutions.md) ·
  [executable solution](../solutions/day05_solutions.sql)

## A beginner's mental model for this lesson

Both joins in this lesson break the habit of matching a foreign key to a different table. A `CROSS JOIN` matches nothing at all: it pairs every left row with every right row, producing a **Cartesian product**. Its size is the product of the input sizes, which is why Example 1 returns exactly 6 categories times 8 countries, 48 rows, and why it is safe only on small, deliberate lists.

A **self-join** reads one table twice under two aliases. `employees` holds 100 people, and `manager_id` points back into the same table, so `employees e` plays the employee and `employees m` plays the manager. Six people (IDs 1 to 6, one heading each department) have no manager; employee 8 manages 92 of the rest. A left self-join keeps those six with an empty manager column.

When the two aliases are peers rather than employee and boss, every pair can appear twice, as (7, 13) and (13, 7), and each row can pair with itself. A **canonical pair** keeps one spelling: `a.employee_id < b.employee_id`. In Exercise 5 that one predicate turns 1,668 same-department combinations into 784 unordered pairs.

## Two worked SQL examples

### Example 1

```sql
WITH cats AS (
  SELECT DISTINCT
    category
  FROM
    products
),
ctries AS (
  SELECT DISTINCT
    country
  FROM
    customers
)
SELECT
  cats.category,
  ctries.country
FROM
  cats
  CROSS JOIN ctries
ORDER BY
  1,
  2;
```

**How to read it:** The two CTEs shrink each table to a short list of distinct values: `cats` reads the category of 300 products and keeps 6, `ctries` reads 500 customers and keeps 8 countries. `CROSS JOIN` has no `ON` clause; it simply combines each category with each country. `ORDER BY 1, 2` sorts by the first and second output columns, category then country.

**Expected result/shape:** 48 rows of `category` and `country`, from Apparel/AU to Sports/US. Brazil appears with every category even though Brazilian customers never ordered, because this grid comes from the customer list, not from sales; that is the point of a grid, which is often left-joined to real totals afterwards. Check it with `SELECT COUNT(DISTINCT category) * COUNT(DISTINCT country)` style arithmetic: 6 times 8.

### Example 2

```sql
SELECT
  e.employee_id,
  e.full_name AS employee,
  m.full_name AS manager
FROM
  employees e
  LEFT JOIN employees m ON m.employee_id = e.manager_id
ORDER BY
  manager NULLS FIRST,
  m.employee_id NULLS FIRST,
  employee,
  e.employee_id
LIMIT 50;
```

**How to read it:** `employees e` is each person and `employees m` is the same table read again as possible managers. `m.employee_id = e.manager_id` finds the manager's row, and `LEFT JOIN` keeps people whose `manager_id` is NULL. The sort puts those NULL managers first, then groups by manager name, and `LIMIT 50` keeps half of the 100 rows.

**Expected result/shape:** Rows 1 to 6 are Employees 1 to 6 with an empty `manager`. Row 7 is Employee 8 (manager Employee 1) and row 8 is Employee 7 (manager Employee 2), because `'Employee 1'` sorts before `'Employee 2'`. Rows 9 to 50 are 42 of Employee 8's 92 reports in text order: Employee 10, Employee 100, Employee 11 and so on to Employee 50. Names sort as text, so Employee 9 comes after Employee 89 and is cut by the limit.

## Learning objectives

- Generate intentional combinations with `CROSS JOIN`.
- Traverse same-table relationships with distinct aliases and generate each
  unordered pair exactly once.

## Vocabulary and concepts

- **Cartesian product:** every possible left/right row combination.
- **Self-join:** joining a relation to another alias of itself.
- **Canonical pair:** one stable representation, such as `a.id < b.id`, for an
  unordered pair.

## Worked example / walkthrough

For product pairs, compare `p1.product_id <> p2.product_id` with
`p1.product_id < p2.product_id`. The first produces both `(A,B)` and `(B,A)`;
the second removes reversed duplicates and self-pairs in one predicate.

## Practice assumptions and review method

- **Focus:** Use cross joins for intentional combinations and self joins for relationships within one table, with explicit cardinality controls.
- **Assumptions:** The employee hierarchy uses `manager_id`; equality pairs need a strict key ordering to avoid self-pairs and mirrored duplicates.
- **Failure to watch for:** An accidental cross join multiplies row counts. Estimate left × right cardinality before materializing combinations.
- **Review loop:** work out the row count before you run anything (6 times 12, or n times n minus 1 over 2 per department), then let `COUNT(*)` confirm or refute it.

## Exercises

Use cross joins for intentional combinations and self joins for relationships within one table, with explicit cardinality controls.

Exercises 1, 2 and 6 read `employees` against itself, Exercises 3 and 4 build small grids, and Exercise 5 is the pair problem. Write the row count you expect next to each before running it.

1. **Query writing:** List every employee with their direct manager when present.
   **Before running:** how many of the 100 rows will show an empty manager, and which IDs are they?
   **Progressive hint:** Self join employees and use a left join so top-level employees remain visible.
   **Inputs/evidence:** For sql-05 Exercise 1, self-join the 100 `employees` rows, aliasing the manager copy as `m`; 6 employees (1 through 6) have no `manager_id`, and the other 94 report to employee 1, 2, or 8. Return `employee_id`, `employee_name`, `manager_id`, and `manager_name`.
   **Expected result/shape:** For sql-05 Exercise 1, return 100 rows, one per employee; employees 1 through 6 show `NULL` manager columns, employee 7 reports to Employee 2, employee 8 to Employee 1, and the remaining 92 to Employee 8. The final columns are `employee_id`, `employee_name`, `manager_id`, and `manager_name`. The final order is `e.employee_id`.
   **Verify:** For sql-05 Exercise 1, confirm 100 distinct `employee_id` values and exactly 6 rows with `manager_name IS NULL`. Switch `LEFT JOIN` to an inner join and the count must fall to 94, losing exactly employees 1 through 6.
2. **Query writing:** Find employees who manage nobody.
   **Before running:** only three people manage anyone here; how many rows does that leave?
   **Progressive hint:** Left join candidate managers to reports and retain managers with no right-side match.
   **Inputs/evidence:** For sql-05 Exercise 2, `LEFT JOIN` each of the 100 `employees` to the employees who report to them and keep rows with no report; only employees 1, 2, and 8 manage anyone.
   **Expected result/shape:** For sql-05 Exercise 2, return 97 rows, one per employee who manages nobody, from employee 3 to employee 100 with 1, 2, and 8 missing. The final columns are `employee_id`, and `full_name`. The final order is `e.employee_id`.
   **Verify:** For sql-05 Exercise 2, confirm `SELECT COUNT(DISTINCT manager_id) FROM employees` returns 3 and that 100 minus 3 equals the 97 rows. Inside a rolled-back transaction, make employee 100 report to employee 3; the result must drop to 96 rows because employee 3 is no longer a leaf.
3. **Query writing:** Build a complete grid of six recent months and all expense categories.
   **Before running:** `expenses` has 10,000 rows but only 5 categories; how big is the grid, and how big would it be if you crossed the raw rows?
   **Progressive hint:** Cross join two small declared dimensions; do not cross join raw fact tables.
   **Inputs/evidence:** For sql-05 Exercise 3, cross join the 5 distinct `expenses` categories with a `generate_series` of 6 month starts, from five months before the current month through the current month.
   **Expected result/shape:** For sql-05 Exercise 3, return 30 rows, six month starts for each of `COGS`, `G&A`, `Infrastructure`, `Marketing`, and `Payroll`, whether or not the month has expenses. The final columns are `category`, and `month_start`. The final order is `c.category, m.month_start`.
   **Verify:** For sql-05 Exercise 3, confirm 30 distinct `(category, month_start)` pairs and that each category appears exactly 6 times. Widen the series to start eleven months back and the result must grow to 60 rows, 5 categories times 12 months.
4. **Prediction:** Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.
   **Before running:** would the count change if `departments` gained a seventh row? By how much?
   **Progressive hint:** Cross-join cardinality is the product of input row counts.
   **Inputs/evidence:** For sql-05 Exercise 4, cross join the 6 `departments` rows with `generate_series(1, 12)` and count the combinations; no department key is returned.
   **Expected result/shape:** For sql-05 Exercise 4, return exactly one row with `department_month_combinations` equal to 72. The final columns are `department_month_combinations`.
   **Verify:** For sql-05 Exercise 4, confirm 72 equals `SELECT COUNT(*) FROM departments` (6) times 12. Change the series to `generate_series(1, 6)` and the count must become 36, showing that a cross join multiplies the row counts.
5. **Debugging:** List unique employee pairs in the same department without self-pairs or mirrored duplicates.
   **Before running:** departments 1 to 4 have 17 people and 5 to 6 have 16; what total does `n * (n - 1) / 2` give?
   **Progressive hint:** Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.
   **Inputs/evidence:** For sql-05 Exercise 5, self-join the 100 `employees` rows on `department_id`; departments 1 to 4 hold 17 employees each and departments 5 and 6 hold 16 each. Return `department_id`, `first_employee_id`, and `second_employee_id` as the composite pair key.
   **Expected result/shape:** For sql-05 Exercise 5, return 784 rows, one row per unordered same-department pair: 136 for each 17-person department and 120 for each 16-person department, starting with the pair 1 and 7 in department 1. The final columns are `department_id`, `first_employee_id`, and `second_employee_id`. The final order is `left_employee.department_id, left_employee.employee_id, right_employee.employee_id`.
   **Verify:** For sql-05 Exercise 5, confirm `first_employee_id < second_employee_id` on all 784 rows and that 4 * 136 + 2 * 120 equals 784. Joining on `department_id` alone returns 1,668 rows, which includes 100 self-pair rows and every mirror pair; replacing `<` with `<>` returns 1,568 rows, exactly twice 784.
6. **Extension:** Show each employee, their manager, and their manager's manager.
   **Before running:** which employees have a manager but no grandmanager?
   **Progressive hint:** Use two independently aliased left self joins; NULLs indicate the hierarchy ends.
   **Inputs/evidence:** For sql-05 Exercise 6, join `employees` to itself twice with `LEFT JOIN`, first for the manager and then for the manager's manager; only employee 8's 92 reports have a two-level chain.
   **Expected result/shape:** For sql-05 Exercise 6, return 100 rows, one per employee: 94 show a `manager_name`, and 92 show `grandmanager_name` Employee 1, because they report to Employee 8, who reports to Employee 1. The final columns are `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name`. The final order is `e.employee_id`.
   **Verify:** For sql-05 Exercise 6, confirm 100 rows, 94 non-`NULL` `manager_name` values, and 92 non-`NULL` `grandmanager_name` values. Employee 7 must show Employee 2 with no grandmanager, and making either join an inner join must cut the result to 94 or 92 rows.

## Common mistakes and how to recover

- **Leaving out the join condition:** `FROM employees a, employees b` with no `WHERE` returns 10,000 rows. Comma joins and `CROSS JOIN` behave the same, so a forgotten predicate looks like a slow, huge answer rather than an error.
- **Using `<>` for peer pairs:** `a.employee_id <> b.employee_id` drops self-pairs but keeps both (7, 13) and (13, 7), so Exercise 5 doubles to 1,568 rows. Only `<` keeps one of each.
- **Inner self-join for managers:** `JOIN employees m` silently drops Employees 1 to 6, the department heads, because their `manager_id` is NULL. Exercise 1 then shows 94 rows instead of 100.
- **`NOT IN` for "manages nobody":** `employee_id NOT IN (SELECT manager_id FROM employees)` returns zero rows here, because six `manager_id` values are NULL and any comparison with NULL is unknown. Use the left anti-join or `NOT EXISTS`.
- **Crossing raw fact rows:** crossing all 10,000 `expenses` with six months makes 60,000 rows; reduce to distinct categories first.

For a run that stopped on an error, see the study guide's [failure recovery notes](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Does every table instance have a clear alias and role?
- Can you prove the pair query contains neither self-pairs nor reversed
  duplicates?

## Next step

Continue to [Day 06; set operations](day06_set_operations.md).

## Deep dive and reference

Learning objectives
- Use CROSS JOIN to form Cartesian products intentionally
- Write self-joins to compare rows within the same table
- Generate pairs and ensure de-duplication (i<j pattern)

Why this matters
Some analyses require pairing rows (A/B comparisons, before/after, customer-customer similarity). Self-joins and controlled Cartesian products enable these.

Core concepts and deep dive
- CROSS JOIN: every row on left with every row on right; use only with small sets or with subsequent filters.
- SELF JOIN: join a table to itself (aliasing required) to compare peers (e.g., orders on consecutive days per customer).
- Pair generation patterns:
  - Symmetric pairs once: JOIN with key ordering (a.id < b.id) to avoid duplicates and self-pairs.
  - Time adjacency: join on the same key and use
    `date_a BETWEEN date_b - interval '1 day' AND date_b + interval '1 day'`.

Walkthrough mapping
- Product substitution pairs within a category (p1.category=p2.category AND p1.product_id<p2.product_id) for bundling analysis.
- Employee hierarchy: `employees e LEFT JOIN employees m ON
  e.manager_id=m.employee_id` gets manager names with a self-join.

Performance notes
- CROSS JOIN blows up quickly; reduce with filters immediately after.
- Consider generating sequences with generate_series for small domains rather than CROSS of large tables.

Further reading
- Self-joins: https://www.postgresql.org/docs/17/queries-table-expressions.html#QUERIES-JOINS

## Ask an AI tutor about this lesson

Use a tutor only if it helps. A good question for this lesson is why `<` removes mirrored pairs while `<>` does not; ask the tutor to make you prove it on a three-person department. The prompt below keeps `solutions/` closed until you ask; [more on tutor use](../../STUDY-GUIDE.md#use-an-ai-tutor-optional).

```text
Tutor me through sql-05: Cross Joins and Self-Joins.

I have completed the direct catalog prerequisite: `sql-04`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day05_cross_self_joins.md
- Answer-free learner SQL: sql/postgres-60day/day05_cross_self_joins.sql

Key terms to teach in context: Cartesian product, Self-join, Canonical pair. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For product pairs, compare `p1.product_id <> p2.product_id` with `p1.product_id < p2.product_id`. The first produces both `(A,B)` and `(B,A)`; the second removes reversed duplicates and self-pairs in one predicate.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-05/ working copy. Never point setup, reset, DDL, or DML
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
