# Day 53 Solutions: SCD Type 2 and Temporal Fact Keys


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day53_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are SCD Type 2, Business key, Validity interval. Its worked-model focus is:
For one changed customer, locate exactly one current row, set its `valid_to` to the day before the new version, and insert the successor at `CURRENT_DATE`. Then as-of join a fact date using inclusive bounds and verify it resolves to one surrogate key, not zero and not two.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

Run Day 52 first in the same database, either
[`day52_solutions.sql`](day52_solutions.sql) or the Day 52 learner file. Day 53
reads that committed `dwh` state but wraps its own changes in a transaction and
rolls them back. Its first statements restore the Day 52 Exercise 1 contract, a
`NOT NULL` `country_sk` that points at `dim_country`; they change nothing when
the warehouse already has it. The full answer is
[`day53_solutions.sql`](day53_solutions.sql).

## Exercise 1: Resolve dimension versions by fact date

The exercise requires the customer and product surrogate keys whose validity
intervals contain each source order date.

```sql
BEGIN;
SET search_path TO dwh, training, public;

CREATE TEMP TABLE fact_sales_temporal_solution AS
SELECT
  o.order_id,
  oi.order_item_id,
  dd.date_key,
  dc.customer_sk,
  dp.product_sk,
  oi.quantity,
  oi.unit_price,
  oi.discount,
  oi.unit_price * oi.quantity * (1 - oi.discount) AS amount
FROM
  training.orders o
  JOIN training.order_items oi USING (order_id)
  JOIN dim_date dd ON dd.date_actual = o.order_date::date
  JOIN dim_customer dc ON dc.customer_id = o.customer_id
    AND o.order_date::date >= dc.valid_from
    AND o.order_date::date <= COALESCE(dc.valid_to, 'infinity'::date)
  JOIN dim_product dp ON dp.product_id = oi.product_id
    AND o.order_date::date >= dp.valid_from
    AND o.order_date::date <= COALESCE(dp.valid_to, 'infinity'::date);

SELECT
  (
    SELECT
      COUNT(*)
    FROM
      fact_sales_temporal_solution) AS mapped_fact_rows,
  (
    SELECT
      COUNT(*)
    FROM
      training.order_items) AS source_item_rows;

ROLLBACK;
```

Expected result: `mapped_fact_rows` equals `source_item_rows`. A lower count
means a date or dimension-version gap; a higher count means overlapping
validity ranges caused one fact to match more than one version.

The executable solution also stages a deterministic customer change effective
30 days ago, closes the previous current row at `effective_date - 1`, inserts a
new current row, and then performs this temporal mapping.

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 1, map every `training.order_items` row to `dim_date`, to the `dim_customer` version whose `valid_from <= order_date::date <= COALESCE(valid_to, 'infinity')`, and to the matching `dim_product` version, after the Exercise 2 change gave customer 1 a second version.
- **Expected result/shape:** For sql-53 Exercise 1, expected output: the temporary table `fact_sales_temporal_solution`, one row per `order_item_id`, with columns `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount`; the check row reports `mapped_fact_rows = 13085`, `source_item_rows = 13085`, and `customer_versions = 2`.
- **Independent verification:** For sql-53 Exercise 1, confirm that `SELECT COUNT(DISTINCT order_item_id) FROM fact_sales_temporal_solution` also returns 13,085, so no item was duplicated by overlapping versions or lost in a validity gap; for customer 1, check that orders dated before the change map to the closed version's `customer_sk` and later orders to the current one.
- **Intermediate relation check:** For sql-53 Exercise 1, count rows after the `orders` to `order_items` join (13,085) and again after each dimension join; any change in the count points at a missing date row or an overlapping or missing version.
- **Clause check:** For sql-53 Exercise 1, the solution uses `CREATE TEMP TABLE ... AS SELECT` over `training.orders JOIN training.order_items USING (order_id)` plus three dimension joins with validity predicates, followed by a scalar-subquery check row.
- **Alternative/trade-off:** For sql-53 Exercise 1, storing `daterange(valid_from, valid_to, '[]')` and joining with `@> o.order_date::date` expresses the same rule and can use a GiST index, at the cost of a range column the rest of the warehouse must understand.
- **Edge case:** An order dated exactly on a version's `valid_to` still matches that closed version, because the date ranges are inclusive at both ends; the next version starts the following day.

## Exercise 2: Audit columns

Inside the Day 53 transaction, the answer adds:

```sql
BEGIN;
SET search_path TO dwh, training, public;

ALTER TABLE dim_customer
  ADD COLUMN updated_by text NOT NULL DEFAULT CURRENT_USER,
  ADD COLUMN updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE dim_product
  ADD COLUMN updated_by text NOT NULL DEFAULT CURRENT_USER,
  ADD COLUMN updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP;

ROLLBACK;
```

The SCD close and insert explicitly stamp `updated_by = 'day53_solution'`.
Because the executable answer rolls back, these columns do not remain after the
lesson.

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 2, add `updated_by text NOT NULL DEFAULT CURRENT_USER` and `updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP` to `dim_customer` and `dim_product`, then apply one staged segment change for customer 1 as an SCD2 close-and-insert whose new version also carries `country_sk`.
- **Expected result/shape:** For sql-53 Exercise 2, expected output: two `ALTER TABLE` command tags for the audit columns, then `SELECT 1`, `UPDATE 1`, and `INSERT 0 1` for the staged change; the closed and the new customer 1 rows both carry `updated_by = 'day53_solution'`.
- **Independent verification:** For sql-53 Exercise 2, query `information_schema.columns` for `table_schema = 'dwh'` and both tables and confirm the two new columns with `is_nullable = 'NO'`; after a savepoint, `UPDATE dim_customer SET updated_by = NULL WHERE customer_id = 1` must fail with SQLSTATE `23502` (not-null violation), then roll back to the savepoint.
- **Intermediate relation check:** For sql-53 Exercise 2, `SELECT customer_sk, valid_from, valid_to, is_current, updated_by FROM dim_customer WHERE customer_id = 1 ORDER BY valid_from` shows one row before the change and two rows after it.
- **Clause check:** For sql-53 Exercise 2, the solution uses two `ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT ...` statements, `CREATE TEMP TABLE staged_customer_change AS SELECT ...`, an `UPDATE ... FROM` that closes the current version, and an `INSERT ... SELECT` that opens the new one and looks up its `country_sk` with a scalar subquery on `dim_country`.
- **Alternative/trade-off:** For sql-53 Exercise 2, a `BEFORE UPDATE` trigger could set `updated_at` automatically, but it hides the audit write from the reader of the load script; this lesson sets the values explicitly.
- **Edge case:** `DEFAULT CURRENT_USER` records the role that ran the statement (`admin` in the classroom); a shared service login therefore needs an explicit `updated_by` value to identify the real actor.

## Reasoning, state, and pitfalls

- A Type 2 change is two operations in one transaction: close the current
  version, then insert the replacement.
- `valid_from <= fact_date <= COALESCE(valid_to, infinity)` matches the
  course's inclusive-date convention.
- Enforce one current row per business key in a production warehouse, commonly
  with a partial unique index on the business key where `is_current`.
- Audit defaults cover inserts, not meaningful update actors; set audit values
  explicitly when closing versions.
- Every new version must carry `country_sk`, the Day 52 Exercise 1 key. The
  scalar lookup returns NULL for an unknown country, which the `NOT NULL` rule
  rejects with SQLSTATE `23502`, so the whole close-and-insert statement fails
  instead of an inner join silently dropping the new version after its old row
  was closed. A repeated country code raises SQLSTATE `21000`.
- Do not run this before Day 52; the executable file raises a clear exception if
  `dwh.dim_customer` is absent.

## Exercise 3: Diagnose same-day changes

Inclusive DATE ranges cannot order two changes on one day without overlap or an
invalid close-before-open interval. The answer surfaces invalid ranges.

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 3, list customer 1's versions from `dim_customer` with `valid_from`, `valid_to`, and the flag `invalid_range = (valid_to IS NOT NULL AND valid_to < valid_from)`.
- **Expected result/shape:** For sql-53 Exercise 3, expected output: two rows ordered by `valid_from`, both with `invalid_range = false`; the closed version ends on `CURRENT_DATE - 31`, the day before the current version begins on `CURRENT_DATE - 30`.
- **Independent verification:** For sql-53 Exercise 3, after a savepoint, apply a second change for customer 1 with the same effective date: closing the current version at `effective_date - 1` gives it a `valid_to` earlier than its `valid_from`, so the flag becomes `true` for that row. That is why date-grain versions cannot order two changes on one date.
- **Intermediate relation check:** For sql-53 Exercise 3, `SELECT COUNT(*) FROM dim_customer WHERE customer_id = 1 AND is_current` returns 1 before and after the change, so exactly one version is current at any time.
- **Clause check:** For sql-53 Exercise 3, the solution uses one `SELECT` with a Boolean expression for `invalid_range`, `WHERE customer_id = 1`, and `ORDER BY valid_from`.
- **Alternative/trade-off:** For sql-53 Exercise 3, a `CHECK (valid_to IS NULL OR valid_to >= valid_from)` constraint would reject the invalid close instead of only reporting it; the report form keeps the load running so the problem can be inspected.
- **Edge case:** A change effective on the same day the customer was first loaded closes the first version at `valid_from - 1`, which is also an invalid range; the load must merge or sequence such changes.

## Exercise 4: Detect overlapping versions

The self-join compares each customer-version pair once and applies the inclusive
overlap condition. Any row can map one fact date to multiple surrogates.

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 4, self-join `dim_customer` on `customer_id` with `b.customer_sk > a.customer_sk`, keeping pairs whose inclusive ranges overlap: `a.valid_from <= COALESCE(b.valid_to, 'infinity')` and `b.valid_from <= COALESCE(a.valid_to, 'infinity')`.
- **Expected result/shape:** For sql-53 Exercise 4, expected output: zero rows with columns `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to`, ordered by `a.customer_id, version_a, version_b`, because every customer's versions are disjoint after the Exercise 2 change.
- **Independent verification:** For sql-53 Exercise 4, after a savepoint, set the closed version's `valid_to` to the new version's `valid_from` and confirm that exactly one row appears for `customer_id = 1`; each overlapping pair is reported once because of `b.customer_sk > a.customer_sk`.
- **Intermediate relation check:** For sql-53 Exercise 4, run the self-join without the two overlap predicates for `customer_id = 1`: it returns one pair, the two versions, which the overlap test then rejects.
- **Clause check:** For sql-53 Exercise 4, the solution uses `FROM dim_customer a JOIN dim_customer b ON b.customer_id = a.customer_id AND b.customer_sk > a.customer_sk AND ...` with two range predicates and `ORDER BY a.customer_id, version_a, version_b`.
- **Alternative/trade-off:** For sql-53 Exercise 4, an exclusion constraint `EXCLUDE USING gist (customer_id WITH =, daterange(valid_from, valid_to, '[]') WITH &&)` prevents overlaps at write time, but it needs the `btree_gist` extension for the equality part.
- **Edge case:** A version with `valid_to = NULL` is open-ended, so `COALESCE(valid_to, 'infinity')` makes it overlap any later version of the same customer until it is closed.

## Exercise 5: Gate unchanged reruns

`IS DISTINCT FROM` compares nullable attributes safely. The replay must use the
same staged desired state that produced the new version, not the unchanged base
table, otherwise the deliberate segment change looks like a new change again.

```sql
WITH desired_customer_state AS (
  SELECT
    customer_id,
    full_name,
    country,
    segment
  FROM
    staged_customer_change
)
SELECT
  COUNT(*) AS unchanged_rows_that_would_version
FROM
  dim_customer current_version
  JOIN desired_customer_state desired USING (customer_id)
WHERE
  current_version.is_current
  AND (current_version.full_name IS DISTINCT FROM desired.full_name
    OR current_version.country IS DISTINCT FROM desired.country
    OR current_version.segment IS DISTINCT FROM desired.segment);
```

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 5, compare the current `dim_customer` row to `desired_customer_state`, which is copied from the same `staged_customer_change` used by Exercise 2.
- **Expected result/shape:** For sql-53 Exercise 5, expected output: exactly one aggregate row, `unchanged_rows_that_would_version = 0`.
- **Independent verification:** For sql-53 Exercise 5, rerun the nullable-safe attribute comparison against `desired_customer_state`; the result must report zero differences. Then alter one staged attribute and require a result of exactly one difference before applying any close/insert statements.
- **Intermediate relation check:** For sql-53 Exercise 5, prove `desired_customer_state` and the current dimension are each unique on `customer_id` before comparing attributes.
- **Clause check:** For sql-53 Exercise 5, `IS DISTINCT FROM` compares nullable attributes, while `dc.is_current` restricts the check to the one version that a replay would consider.
- **Alternative/trade-off:** For sql-53 Exercise 5, comparing `md5(ROW(full_name, country, segment)::text)` on both sides detects the same differences in one comparison, but a reordered attribute list silently changes every hash; the explicit `IS DISTINCT FROM` list is easier to review.
- **Edge case:** A duplicate `customer_id` in desired state must fail a uniqueness gate before versioning; do not let the join multiply candidate changes.

## Exercise 6: Define a same-day policy

Half-open `tstzrange` examples show how effective timestamps can order changes.
They require trustworthy source effective time or sequence, not load-time guesswork.

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 6, model two same-day versions with half-open `tstzrange` values, `[2026-01-15 09:00+00, 2026-01-15 12:00+00)` and `[2026-01-15 12:00+00, infinity)`, instead of inclusive date ranges.
- **Expected result/shape:** For sql-53 Exercise 6, expected output: one row with columns `first_version` and `second_version` showing the two ranges; they meet at 12:00 without overlapping, because the `)` upper bound is exclusive.
- **Independent verification:** For sql-53 Exercise 6, confirm that `first_version && second_version` returns `false`, `first_version -|- second_version` (adjacent) returns `true`, and that `'2026-01-15 12:00+00'::timestamptz <@ second_version` returns `true` while the same test against `first_version` returns `false`.
- **Intermediate relation check:** For sql-53 Exercise 6, `SELECT lower(first_version), upper(first_version), lower(second_version)` shows that the first upper bound equals the second lower bound.
- **Clause check:** For sql-53 Exercise 6, the solution is one `SELECT` of two `tstzrange` literals labelled `first_version` and `second_version`.
- **Alternative/trade-off:** For sql-53 Exercise 6, a source sequence number orders same-day changes without timestamps, but it needs the source system to supply that sequence; load time is not a substitute, because it records when data arrived, not when it became true.
- **Edge case:** Two changes with the same source timestamp still cannot be ordered; the load must reject them or apply a documented tie-break such as the source sequence.
