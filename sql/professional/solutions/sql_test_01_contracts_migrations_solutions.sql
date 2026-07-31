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

CREATE TABLE pro_contract_test_lab.customers (
    customer_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_key text NOT NULL UNIQUE
);

INSERT INTO pro_contract_test_lab.customers (customer_key)
VALUES ('CUS-100');

CREATE TABLE pro_contract_test_lab.orders (
    order_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_key text NOT NULL UNIQUE,
    customer_id bigint NOT NULL DEFAULT 1
        REFERENCES pro_contract_test_lab.customers (customer_id),
    status text NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'paid', 'cancelled')),
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

SELECT
    (
        SELECT array_agg(sm.migration_id ORDER BY sm.migration_id)
        FROM pro_contract_test_lab.schema_migrations AS sm
    ) AS migration_ids,
    c.data_type,
    c.character_maximum_length,
    c.is_nullable,
    c.column_default
FROM information_schema.columns AS c
WHERE c.table_schema = 'pro_contract_test_lab'
  AND c.table_name = 'orders'
  AND c.column_name = 'currency_code';

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

-- Exercise 3: use catalog properties rather than generated names. Each
-- assertion tests one semantic contract and raises on absence or ambiguity.
SELECT pro_contract_test_lab.assert_true(
    'required defaults',
    (
        SELECT COUNT(*)
        FROM information_schema.columns AS c
        WHERE c.table_schema = 'pro_contract_test_lab'
          AND c.table_name = 'orders'
          AND (
              (c.column_name = 'status' AND c.column_default LIKE '%open%')
              OR (
                  c.column_name = 'currency_code'
                  AND c.column_default LIKE '%USD%'
              )
          )
    ) = 2,
    'status or currency_code default drifted'
);

SELECT pro_contract_test_lab.assert_true(
    'order primary key',
    (
        SELECT COUNT(*)
        FROM pg_catalog.pg_constraint AS con
        JOIN pg_catalog.pg_class AS rel
          ON rel.oid = con.conrelid
        JOIN pg_catalog.pg_namespace AS n
          ON n.oid = rel.relnamespace
        WHERE n.nspname = 'pro_contract_test_lab'
          AND rel.relname = 'orders'
          AND con.contype = 'p'
          AND pg_catalog.pg_get_constraintdef(con.oid)
              = 'PRIMARY KEY (order_id)'
    ) = 1,
    'orders.order_id primary-key contract missing or ambiguous'
);

SELECT pro_contract_test_lab.assert_true(
    'order key unique',
    (
        SELECT COUNT(*)
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
    ) = 1,
    'orders.order_key unique contract missing or ambiguous'
);

SELECT pro_contract_test_lab.assert_true(
    'orders customer foreign key',
    (
        SELECT COUNT(*)
        FROM pg_catalog.pg_constraint AS con
        JOIN pg_catalog.pg_class AS rel
          ON rel.oid = con.conrelid
        JOIN pg_catalog.pg_namespace AS n
          ON n.oid = rel.relnamespace
        WHERE n.nspname = 'pro_contract_test_lab'
          AND rel.relname = 'orders'
          AND con.contype = 'f'
          AND pg_catalog.pg_get_constraintdef(con.oid)
              LIKE 'FOREIGN KEY (customer_id) REFERENCES %customers(customer_id)%'
    ) = 1,
    'orders.customer_id foreign-key contract missing or ambiguous'
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

SELECT
    o.order_id,
    o.order_key,
    o.reported_total,
    COALESCE(totals.line_total, 0::numeric) AS line_total,
    o.reported_total
        IS NOT DISTINCT FROM COALESCE(totals.line_total, 0::numeric)
        AS reconciles
FROM pro_contract_test_lab.orders AS o
LEFT JOIN (
    SELECT ol.order_id, SUM(ol.amount) AS line_total
    FROM pro_contract_test_lab.order_lines AS ol
    GROUP BY ol.order_id
) AS totals
  ON totals.order_id = o.order_id
ORDER BY o.order_id;

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
SELECT *
FROM (
    VALUES
        (
            1,
            'fixture ownership',
            'fixture owner, content tag, and expected row count',
            'stale or cross-test data can pass accidentally'
        ),
        (
            2,
            'rollback isolation',
            'outer BEGIN and final ROLLBACK in a disposable database',
            'test DDL or DML can leak into later work'
        ),
        (
            3,
            'negative control',
            'an intentional false assertion raises and is observed',
            'a broken assertion helper can make every test look green'
        ),
        (
            4,
            'process failure',
            'raised errors plus psql ON_ERROR_STOP=1',
            'printed failure rows can still return exit status zero'
        )
) AS harness_controls(
    step_number,
    control_name,
    required_evidence,
    failure_if_missing
)
ORDER BY step_number;

-- Exercise 6: require the intended SQLSTATE category and fail if no error or a
-- different error occurs. Full localized error text is deliberately ignored.
CREATE TABLE pro_contract_test_lab.negative_test_results (
    test_name text PRIMARY KEY,
    observed_sqlstate text NOT NULL,
    constraint_name text NOT NULL,
    row_count_before bigint NOT NULL,
    row_count_after bigint NOT NULL,
    passed boolean NOT NULL
);

DO $solution$
DECLARE
    before_count bigint;
    after_count bigint;
    actual_sqlstate text;
    actual_constraint text;
BEGIN
    SELECT COUNT(*) INTO before_count
    FROM pro_contract_test_lab.orders;

    BEGIN
        INSERT INTO pro_contract_test_lab.orders (
            order_key, reported_total
        )
        VALUES ('ORD-200', 5.00);
        RAISE EXCEPTION 'duplicate order key unexpectedly succeeded';
    EXCEPTION
        WHEN unique_violation THEN
            GET STACKED DIAGNOSTICS
                actual_sqlstate = RETURNED_SQLSTATE,
                actual_constraint = CONSTRAINT_NAME;
    END;

    SELECT COUNT(*) INTO after_count
    FROM pro_contract_test_lab.orders;

    INSERT INTO pro_contract_test_lab.negative_test_results (
        test_name,
        observed_sqlstate,
        constraint_name,
        row_count_before,
        row_count_after,
        passed
    )
    VALUES (
        'duplicate order_key',
        actual_sqlstate,
        actual_constraint,
        before_count,
        after_count,
        actual_sqlstate = '23505' AND before_count = after_count
    );
END
$solution$;

SELECT *
FROM pro_contract_test_lab.negative_test_results
ORDER BY test_name;

SELECT pro_contract_test_lab.assert_true(
    'duplicate order_key negative test',
    (
        SELECT ntr.passed
        FROM pro_contract_test_lab.negative_test_results AS ntr
        WHERE ntr.test_name = 'duplicate order_key'
    ),
    'duplicate insert did not produce 23505 with an unchanged row count'
);

-- Exercise 7: table-driven exact-boundary cases. The expected outcome is data,
-- so an accidentally omitted or misclassified case is visible.
CREATE TABLE pro_contract_test_lab.boundary_probe (
    quantity integer NOT NULL CHECK (quantity BETWEEN 1 AND 100)
);

CREATE TABLE pro_contract_test_lab.boundary_results (
    case_id text PRIMARY KEY,
    raw_value text,
    expected_accept boolean NOT NULL,
    expected_sqlstate text,
    observed_accept boolean NOT NULL,
    observed_sqlstate text,
    matches boolean NOT NULL
);

DO $solution$
DECLARE
    test_case record;
    accepted boolean;
    actual_sqlstate text;
BEGIN
    FOR test_case IN
        SELECT *
        FROM (
            VALUES
                ('01-below'::text, '0'::text, false, '23514'::text),
                ('02-lower', '1', true, NULL),
                ('03-upper', '100', true, NULL),
                ('04-above', '101', false, '23514'),
                ('05-null', NULL, false, '23502'),
                ('06-malformed', 'not-an-integer', false, '22P02')
        ) AS cases(
            case_id,
            raw_value,
            expected_accept,
            expected_sqlstate
        )
        ORDER BY case_id
    LOOP
        accepted := true;
        actual_sqlstate := NULL;
        BEGIN
            INSERT INTO pro_contract_test_lab.boundary_probe (quantity)
            VALUES (test_case.raw_value::integer);
        EXCEPTION
            WHEN OTHERS THEN
                accepted := false;
                GET STACKED DIAGNOSTICS
                    actual_sqlstate = RETURNED_SQLSTATE;
        END;

        INSERT INTO pro_contract_test_lab.boundary_results (
            case_id,
            raw_value,
            expected_accept,
            expected_sqlstate,
            observed_accept,
            observed_sqlstate,
            matches
        )
        VALUES (
            test_case.case_id,
            test_case.raw_value,
            test_case.expected_accept,
            test_case.expected_sqlstate,
            accepted,
            actual_sqlstate,
            test_case.expected_accept = accepted
            AND test_case.expected_sqlstate IS NOT DISTINCT FROM actual_sqlstate
        );
    END LOOP;
END
$solution$;

SELECT
    br.case_id,
    br.raw_value,
    br.expected_accept,
    br.observed_accept,
    br.observed_sqlstate,
    br.matches
FROM pro_contract_test_lab.boundary_results AS br
ORDER BY br.case_id;

SELECT pro_contract_test_lab.assert_true(
    'all quantity boundaries match',
    (SELECT COUNT(*) FROM pro_contract_test_lab.boundary_results) = 6
    AND NOT EXISTS (
        SELECT 1
        FROM pro_contract_test_lab.boundary_results AS r
        WHERE NOT r.matches
    ),
    'a boundary case was missing or differed from its expected outcome'
);

-- Exercise 8: concurrency needs two independent sessions, named barriers,
-- bounded timeouts, captured outcomes, deterministic final assertions, and
-- cleanup. One transaction cannot simulate every conflicting snapshot.
SELECT *
FROM (
    VALUES
        (1, 'setup', 'create one unclaimed disposable row', 'both sessions idle', 'one known fixture row', 'fixture key and value'),
        (2, 'session-a', 'BEGIN; lock/claim the row', 'setup complete', 'session A holds the row lock', 'A transcript plus pg_locks observation'),
        (3, 'session-b', 'attempt the competing claim', 'session A lock visible', 'bounded wait or expected lock error', 'B SQLSTATE and elapsed time'),
        (4, 'session-a', 'commit the winning claim', 'session B attempted', 'one committed owner', 'A commit and returned key'),
        (5, 'session-b', 'retry or roll back by contract', 'session A committed', 'no second successful claim', 'B command tag or rollback'),
        (6, 'verify', 'reconcile row and both transcripts', 'both sessions ended', 'one owner plus expected SQLSTATEs', 'final row and both logs'),
        (7, 'cleanup', 'restore the disposable fixture', 'verification captured', 'original fixture state', 'post-cleanup query')
) AS protocol(
    step_number,
    session_name,
    action,
    wait_for,
    expected_observation,
    failure_evidence
)
ORDER BY step_number;

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
SELECT *
FROM (
    VALUES
        (1, 'restore', 'artifact hash, tool/server versions, restore transcript'),
        (2, 'baseline contracts', 'schema inventory, counts, checksums, key samples'),
        (3, 'migration', 'exact revision, command status, elapsed time, lock/WAL/storage evidence'),
        (4, 'reconciliation', 'post counts/checksums, rejected keys, semantic differences'),
        (5, 'application smoke tests', 'compatible readers and writers exercised'),
        (6, 'recovery decision', 'rollback data-loss limit or forward-fix plan'),
        (7, 'approval', 'named reviewer accepts every prior evidence item'),
        (8, 'cleanup', 'isolated target removed or retained under named custody')
) AS rehearsal_plan(phase_number, phase_name, required_evidence)
ORDER BY phase_number;

ROLLBACK;
