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
--    Inputs: Alter `pro_contract_test_lab.orders`, insert migration ID 3 into
--    `pro_contract_test_lab.schema_migrations`, and extend
--    `pro_contract_test_lab.expected_orders_contract`. Keep the whole attempt
--    inside this lesson transaction.
--    Expected result/shape: The migration manifest is exactly `{1,2,3}`. The
--    `information_schema.columns` row for `currency_code` reports
--    `data_type = 'character'`, length `3`, `is_nullable = 'NO'`, and a default
--    containing `USD`; the named assertions emit PASS notices.
--    Verify: Query the ordered migration IDs and that one catalog row
--    independently, then run the full mismatch view. Change the length to 4 or
--    omit migration 3 as a negative control and prove the appropriate assertion
--    raises instead of merely printing a warning.
--    Hint ladder, rung 1: Inspect `information_schema.columns` before writing
--    the assertion so you know PostgreSQL's exact type and default rendering.
-- 2. Create a raw producer fixture with duplicate source_order_key values.
--    Write one summary check and one detail query; label whether you count
--    duplicate groups, keys, or participating rows.
--
--    Inputs: Create `pro_contract_test_lab.raw_orders(source_row_id,
--    source_order_key, payload_total)` with two `ORD-100` rows and one
--    `ORD-101` row. Group by the literal producer key and use HAVING to retain
--    only duplicate groups.
--    Expected result/shape: One row per duplicate `source_order_key`, with
--    columns `source_order_key` and `participating_rows`, ordered by
--    `source_order_key`. The supplied fixture returns `ORD-100 | 2`.
--    Verify: Separately count the returned groups (`1`) and sum their
--    `participating_rows` (`2`). Add a third `ORD-100` row and two `ORD-102`
--    rows; the result must become `ORD-100 | 3` and `ORD-102 | 2`, without
--    returning `ORD-101`.
--    Hint ladder, rung 1: `WHERE` filters rows before grouping; duplicate
--    detection needs `GROUP BY ... HAVING COUNT(*) > 1`.
-- 3. Add contract checks for defaults, primary/unique keys, and the customer
--    foreign key without depending on generated constraint names.
--
--    Inputs: Inspect `information_schema.columns` for the `status` and
--    `currency_code` defaults, and join `pg_constraint`, `pg_class`, and
--    `pg_namespace` for the `orders` primary key, `order_key` uniqueness, and
--    `customer_id -> customers(customer_id)` foreign key.
--    Expected result/shape: Four named scalar assertions pass: required
--    defaults, primary key on `order_id`, unique key on `order_key`, and the
--    customer foreign key. No generated constraint name is part of the
--    contract.
--    Verify: Render each candidate with `pg_get_constraintdef`, require exactly
--    one semantic match per rule, and prove a negative control fails after
--    looking for a nonexistent key such as `UNIQUE (reported_total)`.
--    Hint ladder, rung 1: Filter by schema, table, `contype`, and rendered
--    definition; `conname` is not stable enough for this contract.
-- 4. Add a reconciliation that includes orders with zero lines and distinguishes
--    a missing total from numeric zero.
--
--    Inputs: Pre-aggregate `pro_contract_test_lab.order_lines` by `order_id`,
--    then LEFT JOIN those totals to every row in
--    `pro_contract_test_lab.orders`. State explicitly that this exercise treats
--    an order with no lines as a numeric total of zero.
--    Expected result/shape: One evidence row per `order_id`, with
--    `order_id`, `order_key`, `reported_total`, `line_total`, and `reconciles`,
--    ordered by `order_id`; `line_total` is zero for an order with no lines.
--    A final scalar assertion passes only when every row reconciles.
--    Verify: The evidence row count equals the orders count, each `order_id`
--    appears once, `ORD-200` has a line total of 5, and zero-line `ORD-201` has
--    a line total of 0. Set `ORD-201.reported_total` to 1 inside a savepoint and
--    prove the assertion fails, then roll back to the savepoint.
--    Hint ladder, rung 1: Aggregate lines before joining; otherwise an order
--    with several lines changes the output grain.
-- 5. Explain fixture ownership, rollback isolation, negative controls, and why
--    a test that only prints failures is unsafe in CI.
--
--    Inputs: Use the checked-in `fixture_manifest`, the outer `BEGIN`/
--    `ROLLBACK`, the caught negative control, and `ON_ERROR_STOP` as concrete
--    evidence. Write one checklist row for each harness control.
--    Expected result/shape: One row per control with columns `control_name`,
--    `required_evidence`, and `failure_if_missing`. Cover fixture ownership,
--    deterministic content tags/counts, rollback isolation, a negative control,
--    raised assertion errors, and `psql` stop-on-error behavior.
--    Verify: Point every checklist row to an observable statement or result in
--    this file. Replace one raised assertion with a printed failure row in a
--    disposable copy and confirm `psql` can exit zero, demonstrating why
--    printing alone is unsafe for CI.
--    Hint ladder, rung 1: Separate “the test detected the defect” from “the
--    command returned a failing process status.”
-- 6. Assert that duplicate source_order_key fails with the expected SQLSTATE and
--    constraint category. Explain why matching the entire localized error text
--    or accepting any exception makes a brittle or false-positive test.
--
--    Inputs: Attempt a second insert of an existing `order_key` inside a nested
--    PL/pgSQL block. Capture `RETURNED_SQLSTATE` and `CONSTRAINT_NAME` with
--    `GET STACKED DIAGNOSTICS`; record order counts before and after.
--    Expected result/shape: One evidence row with `test_name`,
--    `observed_sqlstate`, `constraint_name`, `row_count_before`,
--    `row_count_after`, and `passed`. `observed_sqlstate` is `23505`, the
--    counts are equal, and `passed` is true.
--    Verify: Raise if the insert succeeds or any different exception occurs,
--    and independently check that the existing key still has exactly one row.
--    A NOT NULL failure must not satisfy this unique-key test.
--    Hint ladder, rung 1: Match the stable SQLSTATE/category first; treat the
--    full localized message as diagnostic text, not a test contract.
-- 7. Build table-driven boundary fixtures for quantity, money, dates, NULL, and
--    Unicode text. Include just-below, exact-boundary, just-above, and malformed
--    cases, with an explicit expected outcome for every row.
--
--    Inputs: Begin with raw quantity cases `0`, `1`, `100`, `101`, `NULL`, and
--    `'not-an-integer'`, each with a unique `case_id` and expected acceptance.
--    Convert and insert each case in its own nested block, then extend the same
--    table-driven pattern to one money, date, and Unicode rule.
--    Expected result/shape: One row per `case_id`, with `case_id`, `raw_value`,
--    `expected_accept`, `observed_accept`, `observed_sqlstate`, and `matches`,
--    ordered by `case_id`. Every supplied case has `matches = true`.
--    Verify: Assert that the result count equals the fixture count, no case ID
--    is duplicated or missing, every outcome matches, constraint rejections
--    report `23514`/`23502`, and malformed conversion reports `22P02`. Add a
--    deliberately wrong expectation and prove the final assertion catches it.
--    Hint ladder, rung 1: Expected rejection must be caught in a nested
--    subtransaction so the remaining cases still execute and get recorded.
-- 8. Design a two-session concurrency test for lost updates or double claims.
--    Document synchronization barriers, timeouts, cleanup, deterministic pass
--    criteria, and why a single transaction cannot reproduce every anomaly.
--
--    Inputs: Write a protocol for two independent `psql` sessions operating on
--    one disposable claim row. Include initial state, named barriers, each
--    session's statement, `lock_timeout`, `statement_timeout`, commit/rollback,
--    and cleanup; do not try to simulate both sessions in this one transaction.
--    Expected result/shape: One reviewed protocol row per `step_number`, with
--    `session_name`, `action`, `wait_for`, `expected_observation`, and
--    `failure_evidence`. The final pass criterion names the one permitted owner
--    or value and both session outcomes.
--    Verify: Run the protocol only in the disposable database, capture both
--    transcripts, and reconcile the final row plus SQLSTATEs. Repeat after
--    reversing session order; neither run may depend only on arbitrary sleeps,
--    and cleanup must restore the fixture.
--    Hint ladder, rung 1: A deterministic barrier is something one session can
--    observe (a lock or harness signal), not “wait about two seconds.”
-- 9. Capture a stable schema fingerprint before and after a migration. Exclude
--    volatile OIDs and generated names, but detect changed types, defaults,
--    nullability, constraints, indexes, privileges, and routine signatures.
--
--    Inputs: Build canonical, ordered catalog rows for
--    `pro_contract_test_lab.orders`. Use stable semantic fields and exclude
--    OIDs, file identifiers, statistics, timestamps, and generated names.
--    Expected result/shape: The column result has one row per
--    `ordinal_position`, with `ordinal_position`, `column_name`, `data_type`,
--    `is_nullable`, and `column_default`, ordered by `ordinal_position`. The
--    constraint result has one row per `(contype, definition)`, with those two
--    columns ordered by both fields. Add analogous named result sets for
--    indexes, privileges, and routine signatures before hashing.
--    Verify: Compare canonical rows before comparing hashes so drift remains
--    diagnosable. Add one expected-but-missing column and one unexpected
--    privilege as negative controls; both directions of difference must fail.
--    Hint ladder, rung 1: A hash is only stable after every input row and field
--    has a deterministic representation and order.
-- 10. Rehearse a destructive migration against a disposable restored database.
--     Compare row counts, checksums, rejected rows, critical queries, rollback
--     feasibility, elapsed time, and application compatibility before approval.
--    Inputs: Prepare a separately restored, access-isolated copy of a
--    representative backup; this transaction is only a plan/template and must
--    not create or reset that database. Record artifact hash, `pg_dump`/
--    `pg_restore` and server versions, migration revision, application versions,
--    start/end time, and approver.
--    Expected result/shape: One evidence row per rehearsal phase with columns
--    `phase_number`, `phase_name`, `required_evidence`, `observed_result`,
--    `status`, and `owner`. Phases cover restore, baseline contracts,
--    migration, row/count/checksum reconciliation, rejected keys, read/write
--    smoke tests, lock/WAL/storage timing, rollback or forward-fix limit,
--    compatibility decision, and cleanup.
--    Verify: Every required phase is present and `status = 'pass'` before an
--    approval can be recorded. Inject a checksum mismatch or failed critical
--    query in the isolated rehearsal and prove approval remains blocked; a
--    successful course fixture never authorizes production execution.
--    Hint ladder, rung 1: Treat the rehearsal record as evidence about one
--    exact artifact and migration revision, not as a timeless promise.

ROLLBACK;
\echo 'SQL-TEST-01 complete: pro_contract_test_lab was rolled back'
