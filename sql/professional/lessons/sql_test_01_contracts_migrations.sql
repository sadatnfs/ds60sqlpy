-- SQL-TEST-01: SQL tests, migration checks, and data contracts
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
-- 2. Create a raw producer fixture with duplicate source_order_key values.
--    Write one summary check and one detail query; label whether you count
--    duplicate groups, keys, or participating rows.
--
-- 3. Add contract checks for defaults, primary/unique keys, and the customer
--    foreign key without depending on generated constraint names.
--
-- 4. Add a reconciliation that includes orders with zero lines and distinguishes
--    a missing total from numeric zero.
--
-- 5. Explain fixture ownership, rollback isolation, negative controls, and why
--    a test that only prints failures is unsafe in CI.
--
-- 6. Assert that duplicate source_order_key fails with the expected SQLSTATE and
--    constraint category. Explain why matching the entire localized error text
--    or accepting any exception makes a brittle or false-positive test.
--
-- 7. Build table-driven boundary fixtures for quantity, money, dates, NULL, and
--    Unicode text. Include just-below, exact-boundary, just-above, and malformed
--    cases, with an explicit expected outcome for every row.
--
-- 8. Design a two-session concurrency test for lost updates or double claims.
--    Document synchronization barriers, timeouts, cleanup, deterministic pass
--    criteria, and why a single transaction cannot reproduce every anomaly.
--
-- 9. Capture a stable schema fingerprint before and after a migration. Exclude
--    volatile OIDs and generated names, but detect changed types, defaults,
--    nullability, constraints, indexes, privileges, and routine signatures.
--
-- 10. Rehearse a destructive migration against a disposable restored database.
--     Compare row counts, checksums, rejected rows, critical queries, rollback
--     feasibility, elapsed time, and application compatibility before approval.

ROLLBACK;
\echo 'SQL-TEST-01 complete: pro_contract_test_lab was rolled back'
