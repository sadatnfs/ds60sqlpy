-- SQL-TEST-01 executable solutions
-- SOLUTION READING MAP — sql-test-01: SQL Tests, Migration Checks, and Data Contracts
-- Explanation: sql/professional/solutions/sql_test_01_contracts_migrations_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_test_01_contracts_migrations_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_contract_test_lab;

CREATE FUNCTION pro_contract_test_lab.assert_true(
    p_name text,
    p_condition boolean,
    p_detail text
)
RETURNS void
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
BEGIN
    IF p_condition IS DISTINCT FROM true THEN
        RAISE EXCEPTION 'FAIL [%]: %', p_name, p_detail;
    END IF;
    RAISE NOTICE 'PASS [%]', p_name;
END
$function$;

CREATE TABLE pro_contract_test_lab.schema_migrations (
    migration_id integer PRIMARY KEY,
    migration_name text NOT NULL UNIQUE
);

CREATE TABLE pro_contract_test_lab.orders (
    order_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_key text NOT NULL UNIQUE,
    reported_total numeric(12, 2) NOT NULL,
    currency_code character(3) NOT NULL DEFAULT 'USD'
);

INSERT INTO pro_contract_test_lab.schema_migrations
VALUES
    (1, 'create_orders'),
    (2, 'require_total'),
    (3, 'add_currency_code');

-- Exercise 1.
SELECT pro_contract_test_lab.assert_true(
    'versions 1-3 exact',
    (
        SELECT array_agg(sm.migration_id ORDER BY sm.migration_id)
        FROM pro_contract_test_lab.schema_migrations AS sm
    ) = ARRAY[1, 2, 3],
    'unexpected migration sequence'
);

SELECT pro_contract_test_lab.assert_true(
    'currency contract',
    EXISTS (
        SELECT 1
        FROM information_schema.columns AS c
        WHERE c.table_schema = 'pro_contract_test_lab'
          AND c.table_name = 'orders'
          AND c.column_name = 'currency_code'
          AND c.data_type = 'character'
          AND c.character_maximum_length = 3
          AND c.is_nullable = 'NO'
          AND c.column_default LIKE '%USD%'
    ),
    'currency_code type, nullability, length, or default drifted'
);

-- Exercise 2: raw producer data can contain duplicates before validation.
CREATE TABLE pro_contract_test_lab.raw_orders (
    source_row_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_order_key text NOT NULL,
    payload_total numeric(12, 2)
);

INSERT INTO pro_contract_test_lab.raw_orders (
    source_order_key, payload_total
)
VALUES
    ('ORD-100', 10.00),
    ('ORD-100', 10.00),
    ('ORD-101', 0.00);

SELECT
    ro.source_order_key,
    COUNT(*) AS participating_rows
FROM pro_contract_test_lab.raw_orders AS ro
GROUP BY ro.source_order_key
HAVING COUNT(*) > 1
ORDER BY ro.source_order_key;

SELECT pro_contract_test_lab.assert_true(
    'one duplicate key group detected',
    (
        SELECT COUNT(*)
        FROM (
            SELECT ro.source_order_key
            FROM pro_contract_test_lab.raw_orders AS ro
            GROUP BY ro.source_order_key
            HAVING COUNT(*) > 1
        ) AS duplicate_groups
    ) = 1,
    'expected one duplicate source_order_key group'
);

-- Exercise 3: use catalog properties rather than generated names.
SELECT pro_contract_test_lab.assert_true(
    'order key unique',
    EXISTS (
        SELECT 1
        FROM pg_catalog.pg_constraint AS con
        JOIN pg_catalog.pg_class AS rel
          ON rel.oid = con.conrelid
        JOIN pg_catalog.pg_namespace AS n
          ON n.oid = rel.relnamespace
        WHERE n.nspname = 'pro_contract_test_lab'
          AND rel.relname = 'orders'
          AND con.contype = 'u'
          AND pg_catalog.pg_get_constraintdef(con.oid)
              LIKE 'UNIQUE (order_key)%'
    ),
    'orders.order_key unique contract missing'
);

-- Exercise 4: LEFT JOIN and COALESCE distinguish no lines from nonzero lines.
CREATE TABLE pro_contract_test_lab.order_lines (
    line_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id bigint NOT NULL
        REFERENCES pro_contract_test_lab.orders (order_id),
    amount numeric(12, 2) NOT NULL
);

INSERT INTO pro_contract_test_lab.orders (order_key, reported_total)
VALUES ('ORD-200', 5.00), ('ORD-201', 0.00);

INSERT INTO pro_contract_test_lab.order_lines (order_id, amount)
SELECT o.order_id, 5.00
FROM pro_contract_test_lab.orders AS o
WHERE o.order_key = 'ORD-200';

SELECT pro_contract_test_lab.assert_true(
    'zero-line reconciliation',
    NOT EXISTS (
        SELECT 1
        FROM pro_contract_test_lab.orders AS o
        LEFT JOIN (
            SELECT ol.order_id, SUM(ol.amount) AS line_total
            FROM pro_contract_test_lab.order_lines AS ol
            GROUP BY ol.order_id
        ) AS totals
          ON totals.order_id = o.order_id
        WHERE o.reported_total
              IS DISTINCT FROM COALESCE(totals.line_total, 0::numeric)
    ),
    'reported total differs from line total including zero-line orders'
);

-- Exercise 5: every assertion raises on failure under ON_ERROR_STOP, fixtures
-- live in this rollback-isolated schema, and earlier negative controls prove
-- the harness can fail.

-- Exercise 6: require the intended SQLSTATE category and fail if no error or a
-- different error occurs. Full localized error text is deliberately ignored.
DO $solution$
BEGIN
    BEGIN
        INSERT INTO pro_contract_test_lab.orders (
            order_key, reported_total
        )
        VALUES ('ORD-200', 5.00);
        RAISE EXCEPTION 'duplicate order key unexpectedly succeeded';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Expected unique violation observed';
    END;
END
$solution$;

-- Exercise 7: table-driven exact-boundary cases. The expected outcome is data,
-- so an accidentally omitted or misclassified case is visible.
CREATE TABLE pro_contract_test_lab.boundary_probe (
    quantity integer NOT NULL CHECK (quantity BETWEEN 1 AND 100)
);

CREATE TABLE pro_contract_test_lab.boundary_results (
    case_id text PRIMARY KEY,
    expected_accept boolean NOT NULL,
    observed_accept boolean NOT NULL
);

DO $solution$
DECLARE
    test_case record;
    accepted boolean;
BEGIN
    FOR test_case IN
        SELECT *
        FROM (
            VALUES
                ('below'::text, 0, false),
                ('lower', 1, true),
                ('upper', 100, true),
                ('above', 101, false)
        ) AS cases(case_id, quantity, expected_accept)
        ORDER BY case_id
    LOOP
        accepted := true;
        BEGIN
            INSERT INTO pro_contract_test_lab.boundary_probe (quantity)
            VALUES (test_case.quantity);
        EXCEPTION
            WHEN check_violation THEN
                accepted := false;
        END;

        INSERT INTO pro_contract_test_lab.boundary_results (
            case_id, expected_accept, observed_accept
        )
        VALUES (test_case.case_id, test_case.expected_accept, accepted);
    END LOOP;
END
$solution$;

SELECT pro_contract_test_lab.assert_true(
    'all quantity boundaries match',
    NOT EXISTS (
        SELECT 1
        FROM pro_contract_test_lab.boundary_results AS r
        WHERE r.expected_accept IS DISTINCT FROM r.observed_accept
    ),
    'a boundary case differed from its expected acceptance'
);

-- Exercise 8: concurrency needs two independent sessions, named barriers,
-- bounded timeouts, captured outcomes, deterministic final assertions, and
-- cleanup. One transaction cannot simulate every conflicting snapshot.

-- Exercise 9: inspect ordered semantic properties; omit OIDs/statistics and
-- compare rows before hashing so any drift remains diagnosable.
SELECT
    c.ordinal_position,
    c.column_name,
    c.data_type,
    c.is_nullable,
    c.column_default
FROM information_schema.columns AS c
WHERE c.table_schema = 'pro_contract_test_lab'
  AND c.table_name = 'orders'
ORDER BY c.ordinal_position;

SELECT
    con.contype,
    pg_catalog.pg_get_constraintdef(con.oid) AS definition
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS rel
  ON rel.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = rel.relnamespace
WHERE n.nspname = 'pro_contract_test_lab'
  AND rel.relname = 'orders'
ORDER BY con.contype, definition;

-- Exercise 10: destructive migration validation belongs in a restored,
-- disposable database with baseline/post counts, checksums, rejected keys,
-- critical application queries, elapsed time, rollback evidence, and approval.

ROLLBACK;
