-- SQL-TEST-01 executable solutions
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

ROLLBACK;

