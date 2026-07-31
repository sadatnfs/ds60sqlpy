-- SQL-TEST-01: SQL tests, migration checks, and data contracts
-- BEGINNER WORKFLOW — sql-test-01: SQL Tests, Migration Checks, and Data Contracts
-- Guide: sql/professional/companion-guides/sql_test_01_contracts_migrations.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-test-01/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pro_contract_test_lab.schema_migrations, pro_contract_test_lab.customers, pro_contract_test_lab.orders, pro_contract_test_lab.order_lines, pro_contract_test_lab.fixture_manifest.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Target: PostgreSQL 16+

\set ON_ERROR_STOP on
\echo 'SQL-TEST-01: disposable SQL contract-test lab'
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_contract_test_lab;

-- A minimal assertion helper: false and NULL both fail with a named message.
CREATE FUNCTION pro_contract_test_lab.assert_true(
    p_test_name text,
    p_condition boolean,
    p_detail text
)
RETURNS void
LANGUAGE plpgsql
VOLATILE
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
BEGIN
    IF p_condition IS DISTINCT FROM true THEN
        RAISE EXCEPTION 'FAIL [%]: %', p_test_name, p_detail;
    END IF;
    RAISE NOTICE 'PASS [%]', p_test_name;
END
$function$;

CREATE TABLE pro_contract_test_lab.schema_migrations (
    migration_id integer PRIMARY KEY,
    migration_name text NOT NULL UNIQUE
);

CREATE TABLE pro_contract_test_lab.customers (
    customer_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_key text NOT NULL UNIQUE,
    display_name text NOT NULL CHECK (btrim(display_name) <> '')
);

CREATE TABLE pro_contract_test_lab.orders (
    order_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_key text NOT NULL UNIQUE,
    customer_id bigint NOT NULL
        REFERENCES pro_contract_test_lab.customers (customer_id),
    status text NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'paid', 'cancelled')),
    reported_total numeric(12, 2) NOT NULL
        CHECK (reported_total >= 0),
    created_at timestamptz NOT NULL
);

CREATE TABLE pro_contract_test_lab.order_lines (
    order_line_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id bigint NOT NULL
        REFERENCES pro_contract_test_lab.orders (order_id),
    product_key text NOT NULL,
    quantity integer NOT NULL CHECK (quantity > 0),
    unit_price numeric(12, 2) NOT NULL CHECK (unit_price >= 0),
    UNIQUE (order_id, product_key)
);

CREATE TABLE pro_contract_test_lab.fixture_manifest (
    fixture_name text PRIMARY KEY,
    fixture_owner text NOT NULL,
    content_tag text NOT NULL,
    expected_rows integer NOT NULL CHECK (expected_rows >= 0)
);

INSERT INTO pro_contract_test_lab.schema_migrations
VALUES
    (1, 'create_order_model'),
    (2, 'require_order_status');

INSERT INTO pro_contract_test_lab.customers (customer_key, display_name)
VALUES
    ('CUS-100', 'Avery'),
    ('CUS-101', 'Morgan');

INSERT INTO pro_contract_test_lab.orders (
    order_key,
    customer_id,
    status,
    reported_total,
    created_at
)
SELECT
    fixture.order_key,
    c.customer_id,
    fixture.status,
    fixture.reported_total,
    fixture.created_at
FROM (
    VALUES
        (
            'ORD-100'::text,
            'CUS-100'::text,
            'paid'::text,
            25.00::numeric,
            TIMESTAMPTZ '2026-02-01 10:00:00+00'
        ),
        (
            'ORD-101'::text,
            'CUS-101'::text,
            'open'::text,
            14.00::numeric,
            TIMESTAMPTZ '2026-02-02 11:00:00+00'
        )
) AS fixture(
    order_key,
    customer_key,
    status,
    reported_total,
    created_at
)
JOIN pro_contract_test_lab.customers AS c
  ON c.customer_key = fixture.customer_key;

INSERT INTO pro_contract_test_lab.order_lines (
    order_id,
    product_key,
    quantity,
    unit_price
)
SELECT
    o.order_id,
    fixture.product_key,
    fixture.quantity,
    fixture.unit_price
FROM (
    VALUES
        ('ORD-100'::text, 'ITEM-A'::text, 1, 10.00::numeric),
        ('ORD-100'::text, 'ITEM-B'::text, 3, 5.00::numeric),
        ('ORD-101'::text, 'ITEM-A'::text, 2, 7.00::numeric)
) AS fixture(order_key, product_key, quantity, unit_price)
JOIN pro_contract_test_lab.orders AS o
  ON o.order_key = fixture.order_key;

INSERT INTO pro_contract_test_lab.fixture_manifest
VALUES
    ('customers', 'sql-test-01', 'customers-v1', 2),
    ('orders', 'sql-test-01', 'orders-v1', 2),
    ('order_lines', 'sql-test-01', 'order-lines-v1', 3);

-- Expected producer/consumer contract for the orders relation.
CREATE TABLE pro_contract_test_lab.expected_orders_contract (
    ordinal_position integer PRIMARY KEY,
    column_name text NOT NULL UNIQUE,
    data_type text NOT NULL,
    is_nullable text NOT NULL CHECK (is_nullable IN ('YES', 'NO'))
);

INSERT INTO pro_contract_test_lab.expected_orders_contract
VALUES
    (1, 'order_id', 'bigint', 'NO'),
    (2, 'order_key', 'text', 'NO'),
    (3, 'customer_id', 'bigint', 'NO'),
    (4, 'status', 'text', 'NO'),
    (5, 'reported_total', 'numeric', 'NO'),
    (6, 'created_at', 'timestamp with time zone', 'NO');

CREATE VIEW pro_contract_test_lab.orders_contract_mismatches AS
WITH actual AS (
    SELECT
        c.ordinal_position,
        c.column_name,
        c.data_type,
        c.is_nullable
    FROM information_schema.columns AS c
    WHERE c.table_schema = 'pro_contract_test_lab'
      AND c.table_name = 'orders'
)
SELECT
    COALESCE(e.ordinal_position, a.ordinal_position) AS ordinal_position,
    e.column_name AS expected_column,
    a.column_name AS actual_column,
    e.data_type AS expected_type,
    a.data_type AS actual_type,
    e.is_nullable AS expected_nullable,
    a.is_nullable AS actual_nullable
FROM pro_contract_test_lab.expected_orders_contract AS e
FULL JOIN actual AS a
  ON a.ordinal_position = e.ordinal_position
WHERE ROW(e.column_name, e.data_type, e.is_nullable)
      IS DISTINCT FROM
      ROW(a.column_name, a.data_type, a.is_nullable);

\echo 'Contract and migration assertions'
SELECT pro_contract_test_lab.assert_true(
    'orders column contract',
    NOT EXISTS (
        SELECT 1
        FROM pro_contract_test_lab.orders_contract_mismatches
    ),
    'orders columns, types, order, or nullability drifted'
);

SELECT pro_contract_test_lab.assert_true(
    'ordered migration manifest',
    (
        SELECT array_agg(sm.migration_id ORDER BY sm.migration_id)
        FROM pro_contract_test_lab.schema_migrations AS sm
    ) = ARRAY[1, 2],
    'expected exactly migration versions 1 and 2'
);

\echo 'Invariant and reconciliation assertions'
SELECT pro_contract_test_lab.assert_true(
    'no order orphans',
    NOT EXISTS (
        SELECT 1
        FROM pro_contract_test_lab.orders AS o
        LEFT JOIN pro_contract_test_lab.customers AS c
          ON c.customer_id = o.customer_id
        WHERE c.customer_id IS NULL
    ),
    'an order has no customer'
);

SELECT pro_contract_test_lab.assert_true(
    'reported totals reconcile',
    NOT EXISTS (
        SELECT 1
        FROM pro_contract_test_lab.orders AS o
        JOIN (
            SELECT
                ol.order_id,
                SUM(ol.quantity * ol.unit_price) AS calculated_total
            FROM pro_contract_test_lab.order_lines AS ol
            GROUP BY ol.order_id
        ) AS totals
          ON totals.order_id = o.order_id
        WHERE o.reported_total IS DISTINCT FROM totals.calculated_total
    ),
    'reported_total differs from line total'
);

SELECT pro_contract_test_lab.assert_true(
    'fixture manifest counts',
    NOT EXISTS (
        SELECT 1
        FROM (
            SELECT 'customers'::text AS fixture_name, COUNT(*)::integer AS rows
            FROM pro_contract_test_lab.customers
            UNION ALL
            SELECT 'orders', COUNT(*)::integer
            FROM pro_contract_test_lab.orders
            UNION ALL
            SELECT 'order_lines', COUNT(*)::integer
            FROM pro_contract_test_lab.order_lines
        ) AS actual
        JOIN pro_contract_test_lab.fixture_manifest AS fm
          ON fm.fixture_name = actual.fixture_name
        WHERE actual.rows <> fm.expected_rows
    ),
    'fixture count drifted from its owned manifest'
);

-- A negative control proves the assertion helper really fails. The nested block
-- catches only the expected named failure and keeps the outer test transaction.
DO $negative_control$
BEGIN
    BEGIN
        PERFORM pro_contract_test_lab.assert_true(
            'negative control',
            false,
            'intentional failure'
        );
        RAISE EXCEPTION 'negative control unexpectedly passed';
    EXCEPTION
        WHEN raise_exception THEN
            IF SQLERRM NOT LIKE 'FAIL [negative control]:%' THEN
                RAISE;
            END IF;
            RAISE NOTICE 'Expected assertion failure was observed';
    END;
END
$negative_control$;

-- Exercises:
--
-- 1. Add migration 3: currency_code character(3) NOT NULL DEFAULT 'USD'.
--    Update the expected contract and prove versions 1-3 are exact.
--
--    Inputs: For sql-test-01 Exercise 1, complete the currency migration written analysis and support its claims with read-only evidence from `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-test-01 Exercise 1, expected output: a completed the currency migration written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `character`.
--    Verify: For sql-test-01 Exercise 1, check the currency migration written analysis against `character`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-test-01 Exercise 1, check the currency migration written analysis against `character`.
-- 2. Create a raw producer fixture with duplicate source_order_key values.
--    Write one summary check and one detail query; label whether you count
--    duplicate groups, keys, or participating rows.
--
--    Inputs: For sql-test-01 Exercise 2, read from `pro_contract_test_lab.raw_orders`. Compute `source_order_key`, and `participating_rows` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-test-01 Exercise 2, expected output: one row per duplicate key group and labels its count `participating_rows`. The final columns are `source_order_key`, and `participating_rows`. The final order is `ro.source_order_key`.
--    Verify: For sql-test-01 Exercise 2, evaluate each of `source_order_key`, and `participating_rows` in a separate control `SELECT` over `pro_contract_test_lab.raw_orders`; require one final row and compare every value. Add duplicate source candidates for `source_order_key`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
--    Hint ladder, rung 1: For sql-test-01 Exercise 2, confirm the groups are `source_order_key`; then check `ro.source_order_key` before applying the row cap.
-- 3. Add contract checks for defaults, primary/unique keys, and the customer
--    foreign key without depending on generated constraint names.
--
--    Inputs: For sql-test-01 Exercise 3, read from `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, and `pg_constraint`. Compute `conkey` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-test-01 Exercise 3, expected output: exactly one aggregate summary row. The final columns are `conkey`.
--    Verify: For sql-test-01 Exercise 3, evaluate each of `row_count` in a separate control `SELECT` over `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, and `pg_constraint`; require one final row and compare every value. Add two tied candidates and prove `conkey` identifies both without accidental loss.
--    Hint ladder, rung 1: For sql-test-01 Exercise 3, start with the first relation in `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, and `pg_constraint`; after each join, record total rows and distinct `conkey` so the exact fanout or loss is visible.
-- 4. Add a reconciliation that includes orders with zero lines and distinguishes
--    a missing total from numeric zero.
--
--    Inputs: For sql-test-01 Exercise 4, read from `pro_contract_test_lab.orders`, `pro_contract_test_lab.order_lines`, and `line`. Build the answer toward `order_id`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-test-01 Exercise 4, expected output: one row per `order_id`. The final columns are `order_id`.
--    Verify: For sql-test-01 Exercise 4, project `order_id` plus the raw source columns from `pro_contract_test_lab.orders`, `pro_contract_test_lab.order_lines`, and `line` at each join stage; record row count and distinct `order_id`, then assert the final `order_id` values match those staged rows without unintended fanout or loss. Add one row for which `(o.order_key = 'ORD-200')` is true and one for which it is false; verify only the matching `order_id` value is returned.
--    Hint ladder, rung 1: For sql-test-01 Exercise 4, start with the first relation in `pro_contract_test_lab.orders`, `pro_contract_test_lab.order_lines`, and `line`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 5. Explain fixture ownership, rollback isolation, negative controls, and why
--    a test that only prints failures is unsafe in CI.
--
--    Inputs: For sql-test-01 Exercise 5, complete the harness written analysis and support its claims with read-only evidence from `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-test-01 Exercise 5, expected output: a completed the harness written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `on_error_stop`.
--    Verify: For sql-test-01 Exercise 5, check the harness written analysis against `on_error_stop`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-test-01 Exercise 5, check the harness written analysis against `on_error_stop`.
-- 6. Assert that duplicate source_order_key fails with the expected SQLSTATE and
--    constraint category. Explain why matching the entire localized error text
--    or accepting any exception makes a brittle or false-positive test.
--
--    Inputs: For sql-test-01 Exercise 6, read the target keys from `pro_contract_test_lab.orders` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-test-01 Exercise 6, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `unique_violation`, and `constraint_name`.
--    Verify: For sql-test-01 Exercise 6, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_contract_test_lab.orders` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
--    Hint ladder, rung 1: For sql-test-01 Exercise 6, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_contract_test_lab.orders` again and prove rollback or idempotent retry.
-- 7. Build table-driven boundary fixtures for quantity, money, dates, NULL, and
--    Unicode text. Include just-below, exact-boundary, just-above, and malformed
--    cases, with an explicit expected outcome for every row.
--
--    Inputs: For sql-test-01 Exercise 7, read from `pro_contract_test_lab.boundary_probe`, and `pro_contract_test_lab.boundary_results`. Build the answer toward `case_id`, `quantity`, and `expected_accept`; keep `case_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-test-01 Exercise 7, expected output: one row per `case_id`. The final columns are `case_id`, `quantity`, and `expected_accept`. The final order is `case_id LOOP accepted := true`.
--    Verify: For sql-test-01 Exercise 7, reselect the returned keys directly from the source; require unique `case_id` where the expected grain is one row per key and confirm the projected `case_id`, `quantity`, and `expected_accept` against `pro_contract_test_lab.boundary_probe`, and `pro_contract_test_lab.boundary_results`. Repeat with `NULL` in `case_id`, and `quantity` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-test-01 Exercise 7, inspect the source keys that survive `WHERE`; then check `case_id LOOP accepted := true` before applying the row cap.
-- 8. Design a two-session concurrency test for lost updates or double claims.
--    Document synchronization barriers, timeouts, cleanup, deterministic pass
--    criteria, and why a single transaction cannot reproduce every anomaly.
--
--    Inputs: For sql-test-01 Exercise 8, read from `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders`. Build the answer toward `lock_timeout`, and `statement_timeout`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-test-01 Exercise 8, expected output: one row per `customer_id`. The final columns are `lock_timeout`, and `statement_timeout`.
--    Verify: For sql-test-01 Exercise 8, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `lock_timeout`, and `statement_timeout` against `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-test-01 Exercise 8, select `customer_id` from `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders` before adding derived columns.
-- 9. Capture a stable schema fingerprint before and after a migration. Exclude
--    volatile OIDs and generated names, but detect changed types, defaults,
--    nullability, constraints, indexes, privileges, and routine signatures.
--
--    Inputs: For sql-test-01 Exercise 9, read from `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`. Build the answer toward `ordinal_position`, `column_name`, `data_type`, `is_nullable`, and `column_default`; keep `ordinal_position` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-test-01 Exercise 9, expected output: one row per `ordinal_position`. The final columns are `ordinal_position`, `column_name`, `data_type`, `is_nullable`, and `column_default`. The final order is `con.contype, definition`.
--    Verify: For sql-test-01 Exercise 9, project `ordinal_position` plus the raw source columns from `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` at each join stage; record row count and distinct `ordinal_position`, then assert the final `ordinal_position`, `column_name`, `data_type`, `is_nullable`, and `column_default` values match those staged rows without unintended fanout or loss. Give two rows the same `con.contype` value and different `definition` values; verify `con.contype, definition` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-test-01 Exercise 9, start with the first relation in `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `ordinal_position` so the exact fanout or loss is visible.
-- 10. Rehearse a destructive migration against a disposable restored database.
--     Compare row counts, checksums, rejected rows, critical queries, rollback
--     feasibility, elapsed time, and application compatibility before approval.
--    Inputs: For sql-test-01 Exercise 10, use `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-test-01 Exercise 10, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
--    Verify: For sql-test-01 Exercise 10, restore into an isolated target and reconcile `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-test-01 Exercise 10, restore into an isolated target and reconcile `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.

ROLLBACK;
\echo 'SQL-TEST-01 complete: pro_contract_test_lab was rolled back'
