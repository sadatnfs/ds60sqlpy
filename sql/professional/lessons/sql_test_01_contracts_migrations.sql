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
--    Inputs: For sql-test-01 Exercise 1, alter `pro_contract_test_lab.orders` with required `currency_code character(3) DEFAULT 'USD'`, add migration ID 3, and extend the expected column contract inside the rollback-only fixture.
--    Expected result/shape: For sql-test-01 Exercise 1, expected output: the version and currency assertions pass, followed by one evidence row with migration IDs `{1,2,3}`, type `character`, length 3, `is_nullable = 'NO'`, and a default containing USD.
--    Verify: For sql-test-01 Exercise 1, independently query the ordered migration IDs and the `information_schema.columns` row; then change the length or omit migration 3 in a negative control and require the assertion to raise.
--    Hint ladder, rung 1: Inspect `information_schema.columns` before writing
--    the assertion so you know PostgreSQL's exact type and default rendering.
-- 2. Create a raw producer fixture with duplicate source_order_key values.
--    Write one summary check and one detail query; label whether you count
--    duplicate groups, keys, or participating rows.
--
--    Inputs: For sql-test-01 Exercise 2, populate `pro_contract_test_lab.raw_orders` with two `ORD-100` producer rows and one `ORD-101` row, then group by `source_order_key` and retain duplicate groups with `HAVING COUNT(*) > 1`.
--    Expected result/shape: For sql-test-01 Exercise 2, expected output: one row per duplicate producer key with columns `source_order_key` and `participating_rows`, ordered by key; the supplied fixture returns `ORD-100` with 2 participating rows.
--    Verify: For sql-test-01 Exercise 2, independently assert one duplicate group and two participating rows; add another `ORD-100` plus two `ORD-102` rows and prove both groups appear once while `ORD-101` remains absent.
--    Hint ladder, rung 1: `WHERE` filters rows before grouping; duplicate
--    detection needs `GROUP BY ... HAVING COUNT(*) > 1`.
-- 3. Add contract checks for defaults, primary/unique keys, and the customer
--    foreign key without depending on generated constraint names.
--
--    Inputs: For sql-test-01 Exercise 3, inspect order defaults through `information_schema.columns` and inspect primary, unique, and foreign-key semantics through `pg_constraint`, `pg_class`, and `pg_namespace` without relying on generated names.
--    Expected result/shape: For sql-test-01 Exercise 3, expected output: four named assertions pass for the required defaults, primary key on `order_id`, unique key on `order_key`, and `customer_id` foreign key; no constraint name is contractual.
--    Verify: For sql-test-01 Exercise 3, render candidates with `pg_get_constraintdef`, require exactly one semantic match per rule, and prove a negative control looking for a nonexistent `UNIQUE (reported_total)` contract raises.
--    Hint ladder, rung 1: Filter by schema, table, `contype`, and rendered
--    definition; `conname` is not stable enough for this contract.
-- 4. Add a reconciliation that includes orders with zero lines and distinguishes
--    a missing total from numeric zero.
--
--    Inputs: For sql-test-01 Exercise 4, pre-aggregate `pro_contract_test_lab.order_lines` by `order_id`, LEFT JOIN those totals to every order, and apply the stated policy that no lines means numeric zero.
--    Expected result/shape: For sql-test-01 Exercise 4, expected output: one row per order with `order_id`, `order_key`, `reported_total`, `line_total`, and `reconciles`, ordered by `order_id`; zero-line orders remain and show zero.
--    Verify: For sql-test-01 Exercise 4, reconcile output count and unique IDs with the orders table, prove `ORD-200` totals 5 and `ORD-201` totals 0, then corrupt a reported total under a savepoint and require the assertion to fail.
--    Hint ladder, rung 1: Aggregate lines before joining; otherwise an order
--    with several lines changes the output grain.
-- 5. Explain fixture ownership, rollback isolation, negative controls, and why
--    a test that only prints failures is unsafe in CI.
--
--    Inputs: For sql-test-01 Exercise 5, derive a harness checklist from the fixture manifest, outer transaction, caught negative control, raised assertions, final rollback, and psql `ON_ERROR_STOP=1` behavior.
--    Expected result/shape: For sql-test-01 Exercise 5, expected output: exactly four ordered rows with `step_number`, `control_name`, `required_evidence`, and `failure_if_missing`, covering fixture ownership, rollback isolation, negative control, and process failure.
--    Verify: For sql-test-01 Exercise 5, run one intentionally false assertion in a disposable invocation and require a nonzero psql exit, then rerun the valid suite and confirm rollback leaves no `pro_contract_test_lab` schema.
--    Hint ladder, rung 1: Separate “the test detected the defect” from “the
--    command returned a failing process status.”
-- 6. Assert that duplicate source_order_key fails with the expected SQLSTATE and
--    constraint category. Explain why matching the entire localized error text
--    or accepting any exception makes a brittle or false-positive test.
--
--    Inputs: For sql-test-01 Exercise 6, record the order count, attempt a duplicate `order_key` inside a nested exception block, capture returned SQLSTATE and constraint name, and record the post-attempt count.
--    Expected result/shape: For sql-test-01 Exercise 6, expected output: one `negative_test_results` row showing SQLSTATE `23505`, a nonblank constraint name, unchanged before/after counts, and `passed = true`, followed by a passing assertion.
--    Verify: For sql-test-01 Exercise 6, fail if the insert succeeds or raises any category other than `unique_violation`, compare the before/after counts independently, and verify the duplicate row is absent.
--    Hint ladder, rung 1: Match the stable SQLSTATE/category first; treat the
--    full localized message as diagnostic text, not a test contract.
-- 7. Build table-driven boundary fixtures for quantity, money, dates, NULL, and
--    Unicode text. Include just-below, exact-boundary, just-above, and malformed
--    cases, with an explicit expected outcome for every row.
--
--    Inputs: For sql-test-01 Exercise 7, drive six quantity cases—below, lower bound, upper bound, above, NULL, and malformed—from data, executing each insert in its own exception subtransaction and recording observed SQLSTATE.
--    Expected result/shape: For sql-test-01 Exercise 7, expected output: six rows with `case_id`, raw value, expected/observed acceptance, observed SQLSTATE, and `matches`; bounds 1 and 100 pass, and all four invalid cases fail with their intended category.
--    Verify: For sql-test-01 Exercise 7, require exactly six unique case IDs and no false `matches`, independently inspect accepted rows, and prove an omitted or misclassified case makes the final assertion raise.
--    Hint ladder, rung 1: Expected rejection must be caught in a nested
--    subtransaction so the remaining cases still execute and get recorded.
-- 8. Design a two-session concurrency test for lost updates or double claims.
--    Document synchronization barriers, timeouts, cleanup, deterministic pass
--    criteria, and why a single transaction cannot reproduce every anomaly.
--
--    Inputs: For sql-test-01 Exercise 8, specify a two-session lock test with named setup, session barriers, bounded lock and statement timeouts, captured outcomes, deterministic final reconciliation, and cleanup.
--    Expected result/shape: For sql-test-01 Exercise 8, expected output: seven ordered protocol rows with `step_number`, `session_name`, `action`, `wait_for`, `expected_observation`, and `failure_evidence`, from setup through cleanup.
--    Verify: For sql-test-01 Exercise 8, execute the protocol only in two disposable sessions, capture both transcripts and the final row, require one committed owner plus the expected losing outcome, and restore the fixture even after failure.
--    Hint ladder, rung 1: A deterministic barrier is something one session can
--    observe (a lock or harness signal), not “wait about two seconds.”
-- 9. Capture a stable schema fingerprint before and after a migration. Exclude
--    volatile OIDs and generated names, but detect changed types, defaults,
--    nullability, constraints, indexes, privileges, and routine signatures.
--
--    Inputs: For sql-test-01 Exercise 9, inventory ordered order-column properties from `information_schema.columns` and semantic constraint definitions from PostgreSQL catalogs, excluding OIDs, statistics, timestamps, and generated names.
--    Expected result/shape: For sql-test-01 Exercise 9, expected output: one deterministic result set at one-row-per-column grain and another at one-row-per-constraint grain, with definitions ordered by constraint type and definition.
--    Verify: For sql-test-01 Exercise 9, compare visible semantic rows before any hash, inject one missing and one unexpected property, and prove both drift directions are diagnosable without depending on an OID or generated name.
--    Hint ladder, rung 1: A hash is only stable after every input row and field
--    has a deterministic representation and order.
-- 10. Rehearse a destructive migration against a disposable restored database.
--     Compare row counts, checksums, rejected rows, critical queries, rollback
--     feasibility, elapsed time, and application compatibility before approval.
--    Inputs: For sql-test-01 Exercise 10, describe a destructive-migration rehearsal in an isolated restored database, covering artifact identity, baseline contracts, migration evidence, reconciliation, application checks, recovery decision, approval, and cleanup.
--    Expected result/shape: For sql-test-01 Exercise 10, expected output: eight ordered rows with `phase_number`, `phase_name`, and `required_evidence`, beginning with restore and ending with cleanup; the SQL lesson records the plan but does not perform an external restore.
--    Verify: For sql-test-01 Exercise 10, rehearse against a disposable representative restore, inject one missing or invalid artifact, require validation to stop before cutover, and archive measured duration, rollback limits, approval, and cleanup evidence.
--    Hint ladder, rung 1: Treat the rehearsal record as evidence about one
--    exact artifact and migration revision, not as a timeless promise.

ROLLBACK;
\echo 'SQL-TEST-01 complete: pro_contract_test_lab was rolled back'
